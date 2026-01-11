#!/usr/bin/env python3
"""
Analyze external Maven dependencies per module for Kotlin Multiplatform feasibility.

This script parses pom.xml files to identify external (non-flexmark) dependencies
and categorizes them by their impact on KMP conversion.

Categories:
- BLOCKING: No KMP alternative exists (docx4j, openhtmltopdf)
- REPLACEABLE: KMP alternative available (jsoup -> Ksoup, autolink -> custom impl)
- SAFE: Test-only, logging, or platform-agnostic libraries
- INTERNAL: flexmark internal dependencies

Usage:
    python analyze_external_deps.py [--repo-root PATH] [--output PATH]

Output:
    JSON report with dependencies per module and overall feasibility assessment.
"""

import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Dependency:
    """Represents a Maven dependency."""
    group_id: str
    artifact_id: str
    version: Optional[str]
    scope: str  # compile, test, provided, runtime
    category: str  # BLOCKING, REPLACEABLE, SAFE, INTERNAL
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "artifact_id": self.artifact_id,
            "version": self.version,
            "scope": self.scope,
            "category": self.category,
            "notes": self.notes
        }


# Known dependency categorization based on research findings
DEPENDENCY_CATEGORIES = {
    # BLOCKING - No KMP alternative, cannot convert
    ("org.docx4j", "docx4j-JAXB-ReferenceImpl"): ("BLOCKING", "DOCX generation via JAXB - JVM only"),
    ("org.docx4j", "docx4j-core"): ("BLOCKING", "DOCX generation via JAXB - JVM only"),
    ("com.openhtmltopdf", "openhtmltopdf-core"): ("BLOCKING", "HTML to PDF rendering - JVM only"),
    ("com.openhtmltopdf", "openhtmltopdf-pdfbox"): ("BLOCKING", "PDF generation - JVM only"),
    ("com.openhtmltopdf", "openhtmltopdf-svg-support"): ("BLOCKING", "SVG in PDF - JVM only"),
    ("org.apache.xmlgraphics", "xmlgraphics-commons"): ("BLOCKING", "XML/graphics utilities - JVM only"),
    ("jakarta.xml.bind", None): ("BLOCKING", "JAXB - JVM only"),
    ("javax.xml.bind", None): ("BLOCKING", "JAXB - JVM only"),
    ("org.osgi", None): ("BLOCKING", "OSGi framework - JVM only"),

    # REPLACEABLE - KMP alternatives exist
    ("org.jsoup", "jsoup"): ("REPLACEABLE", "Use Ksoup (fleeksoft/ksoup) - API compatible"),
    ("org.nibor.autolink", "autolink"): ("REPLACEABLE", "Implement custom autolink or port - simple algorithm"),
    ("commons-io", "commons-io"): ("REPLACEABLE", "Use kotlinx-io for basic file utilities"),

    # SAFE - Test/logging/utility libraries
    ("junit", None): ("SAFE", "Test framework - JVM testing is fine"),
    ("org.junit", None): ("SAFE", "Test framework - JVM testing is fine"),
    ("org.openjdk.jmh", None): ("SAFE", "Benchmarking - JVM only is fine"),
    ("org.pegdown", "pegdown"): ("SAFE", "Test-only compatibility check"),
    ("org.apache.logging.log4j", None): ("SAFE", "Logging - test scope only"),
    ("org.slf4j", None): ("SAFE", "Logging facade - replaceable with println or Kermit"),
    ("org.jetbrains", "annotations"): ("SAFE", "Compile-time annotations - not needed at runtime"),
}


def categorize_dependency(group_id: str, artifact_id: str, scope: str) -> Tuple[str, str]:
    """
    Determine the category of a dependency based on known mappings.

    Returns (category, notes) tuple.
    """
    # Check exact match first
    key = (group_id, artifact_id)
    if key in DEPENDENCY_CATEGORIES:
        return DEPENDENCY_CATEGORIES[key]

    # Check group-level match (artifact_id = None)
    group_key = (group_id, None)
    if group_key in DEPENDENCY_CATEGORIES:
        return DEPENDENCY_CATEGORIES[group_key]

    # Test scope dependencies are generally safe
    if scope == "test":
        return ("SAFE", "Test-only dependency")

    # Unknown compile-scope dependencies - flag for review
    if scope in ("compile", "", None):
        return ("UNKNOWN", "Needs manual review for KMP compatibility")

    return ("SAFE", f"Scope: {scope}")


def parse_pom_xml(pom_path: Path) -> Tuple[str, List[Dependency]]:
    """
    Parse a pom.xml file and extract dependencies.

    Returns (module_name, list of dependencies).
    """
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Warning: Could not parse {pom_path}: {e}")
        return (pom_path.parent.name, [])

    # Extract namespace from root tag (Maven POM files use namespace)
    ns_uri = ""
    if root.tag.startswith('{'):
        ns_uri = root.tag[1:root.tag.index('}')]

    # Helper to find element with or without namespace
    def find_el(parent, tag):
        if ns_uri:
            el = parent.find(f'{{{ns_uri}}}{tag}')
            if el is not None:
                return el
        return parent.find(tag)

    def findall_el(parent, tag):
        if ns_uri:
            els = parent.findall(f'{{{ns_uri}}}{tag}')
            if els:
                return els
        return parent.findall(tag)

    # Get artifact ID (module name)
    artifact_el = find_el(root, 'artifactId')
    module_name = artifact_el.text if artifact_el is not None else pom_path.parent.name

    dependencies = []

    # Find all dependencies
    deps_el = find_el(root, 'dependencies')
    if deps_el is None:
        return (module_name, [])

    for dep in findall_el(deps_el, 'dependency'):
        group_el = find_el(dep, 'groupId')
        artifact_el = find_el(dep, 'artifactId')
        version_el = find_el(dep, 'version')
        scope_el = find_el(dep, 'scope')

        if group_el is None or artifact_el is None:
            continue

        group_id = group_el.text
        artifact_id = artifact_el.text
        version = version_el.text if version_el is not None else None
        scope = scope_el.text if scope_el is not None else "compile"

        # Determine if internal flexmark dependency
        if group_id == "com.vladsch.flexmark":
            category = "INTERNAL"
            notes = "flexmark internal module"
        else:
            category, notes = categorize_dependency(group_id, artifact_id, scope)

        dependencies.append(Dependency(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            scope=scope,
            category=category,
            notes=notes
        ))

    return (module_name, dependencies)


def find_pom_files(repo_root: Path) -> List[Path]:
    """Find all pom.xml files in module directories."""
    pom_files = []

    # Get immediate subdirectories that contain pom.xml
    for item in repo_root.iterdir():
        if item.is_dir() and item.name.startswith('flexmark'):
            pom_path = item / 'pom.xml'
            if pom_path.exists():
                pom_files.append(pom_path)

    # Also check root pom.xml for global dependencies
    root_pom = repo_root / 'pom.xml'
    if root_pom.exists():
        pom_files.append(root_pom)

    return pom_files


def assess_module_feasibility(dependencies: List[Dependency]) -> str:
    """
    Assess module's KMP conversion feasibility based on dependencies.

    Returns: FEASIBLE, PARTIAL, NOT_FEASIBLE
    """
    has_blocking = any(
        d.category == "BLOCKING" and d.scope != "test"
        for d in dependencies
    )
    has_replaceable = any(
        d.category == "REPLACEABLE" and d.scope != "test"
        for d in dependencies
    )
    has_unknown = any(
        d.category == "UNKNOWN" and d.scope != "test"
        for d in dependencies
    )

    if has_blocking:
        return "NOT_FEASIBLE"
    elif has_replaceable or has_unknown:
        return "PARTIAL"
    else:
        return "FEASIBLE"


def generate_report(module_deps: Dict[str, List[Dependency]]) -> dict:
    """Generate the final JSON report structure."""

    # Per-module analysis
    modules = {}
    for module, deps in sorted(module_deps.items()):
        external_deps = [d for d in deps if d.category != "INTERNAL"]
        internal_deps = [d for d in deps if d.category == "INTERNAL"]

        modules[module] = {
            "feasibility": assess_module_feasibility(deps),
            "external_dependencies": {
                "count": len(external_deps),
                "blocking": [d.to_dict() for d in external_deps if d.category == "BLOCKING"],
                "replaceable": [d.to_dict() for d in external_deps if d.category == "REPLACEABLE"],
                "safe": [d.to_dict() for d in external_deps if d.category == "SAFE"],
                "unknown": [d.to_dict() for d in external_deps if d.category == "UNKNOWN"],
            },
            "internal_dependencies": {
                "count": len(internal_deps),
                "modules": [d.artifact_id for d in internal_deps]
            }
        }

    # Summary statistics
    feasibility_counts = {"FEASIBLE": 0, "PARTIAL": 0, "NOT_FEASIBLE": 0}
    blocking_deps = set()
    replaceable_deps = set()

    for module, data in modules.items():
        feasibility_counts[data["feasibility"]] += 1
        for dep in data["external_dependencies"]["blocking"]:
            blocking_deps.add(f"{dep['group_id']}:{dep['artifact_id']}")
        for dep in data["external_dependencies"]["replaceable"]:
            replaceable_deps.add(f"{dep['group_id']}:{dep['artifact_id']}")

    return {
        "summary": {
            "total_modules": len(modules),
            "feasibility_breakdown": feasibility_counts,
            "unique_blocking_deps": sorted(blocking_deps),
            "unique_replaceable_deps": sorted(replaceable_deps)
        },
        "modules": modules
    }


def print_summary(report: dict) -> None:
    """Print a human-readable summary to console."""
    print("\n" + "=" * 70)
    print("EXTERNAL DEPENDENCIES ANALYSIS - SUMMARY")
    print("=" * 70)

    summary = report["summary"]
    print(f"\nTotal modules analyzed: {summary['total_modules']}")
    print(f"\nFeasibility breakdown:")
    for status, count in summary["feasibility_breakdown"].items():
        print(f"  {status}: {count} modules")

    if summary["unique_blocking_deps"]:
        print(f"\nBLOCKING dependencies ({len(summary['unique_blocking_deps'])}):")
        for dep in summary["unique_blocking_deps"]:
            print(f"  - {dep}")

    if summary["unique_replaceable_deps"]:
        print(f"\nREPLACEABLE dependencies ({len(summary['unique_replaceable_deps'])}):")
        for dep in summary["unique_replaceable_deps"]:
            print(f"  - {dep}")

    print("\n" + "-" * 70)
    print("BY MODULE:")
    print("-" * 70)

    for module, data in sorted(report["modules"].items()):
        feasibility = data["feasibility"]
        ext_count = data["external_dependencies"]["count"]
        blocking_count = len(data["external_dependencies"]["blocking"])
        replaceable_count = len(data["external_dependencies"]["replaceable"])

        indicator = {"FEASIBLE": "[OK]", "PARTIAL": "[--]", "NOT_FEASIBLE": "[XX]"}[feasibility]

        print(f"\n  {indicator} {module}")
        print(f"      Feasibility: {feasibility}")
        if ext_count > 0:
            print(f"      External deps: {ext_count} (blocking: {blocking_count}, replaceable: {replaceable_count})")
            if blocking_count > 0:
                for dep in data["external_dependencies"]["blocking"]:
                    print(f"        BLOCKING: {dep['group_id']}:{dep['artifact_id']} - {dep['notes']}")
            if replaceable_count > 0:
                for dep in data["external_dependencies"]["replaceable"]:
                    print(f"        REPLACEABLE: {dep['group_id']}:{dep['artifact_id']} - {dep['notes']}")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze external Maven dependencies for Kotlin Multiplatform feasibility"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Path to repository root (default: two levels up from script)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: .ai_out/.../external_deps.json)"
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.output:
        output_path = args.output
    else:
        output_dir = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "external_deps.json"

    print(f"Analyzing pom.xml files in: {repo_root}")

    pom_files = find_pom_files(repo_root)
    print(f"Found {len(pom_files)} pom.xml files")

    module_deps = {}
    for pom_path in pom_files:
        module_name, deps = parse_pom_xml(pom_path)
        module_deps[module_name] = deps

    report = generate_report(module_deps)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nJSON report written to: {output_path}")
    print_summary(report)


if __name__ == "__main__":
    main()
