#!/usr/bin/env python3
"""
Aggregate analysis to produce module-level Kotlin Multiplatform feasibility assessment.

This script combines the results from:
- analyze_java_api_blockers.py (Java API usage analysis)
- analyze_external_deps.py (External dependency analysis)

And produces a per-module feasibility assessment with tier classification.

Tiers (from research):
- Tier 1: Fully Convertible (no external blockers, minimal API issues)
- Tier 2: Convertible with Effort (replaceable deps, moderate API work)
- Tier 3: JVM-Only (cannot convert for Web/JS target)

Usage:
    python analyze_module_feasibility.py [--repo-root PATH] [--output PATH]

Prerequisites:
    Run analyze_java_api_blockers.py and analyze_external_deps.py first,
    OR this script will run them automatically.

Output:
    JSON report with per-module assessment and console summary.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ModuleAssessment:
    """Complete assessment for a single module."""
    module_name: str
    tier: int  # 1, 2, or 3
    feasibility: str  # FEASIBLE, PARTIAL, NOT_FEASIBLE
    api_blocker_count: int
    regex_usage_count: int
    blocking_deps: List[str]
    replaceable_deps: List[str]
    notes: List[str]

    def to_dict(self) -> dict:
        return {
            "module_name": self.module_name,
            "tier": self.tier,
            "tier_description": {
                1: "Fully Convertible",
                2: "Convertible with Effort",
                3: "JVM-Only"
            }[self.tier],
            "feasibility": self.feasibility,
            "api_blocker_count": self.api_blocker_count,
            "regex_usage_count": self.regex_usage_count,
            "blocking_deps": self.blocking_deps,
            "replaceable_deps": self.replaceable_deps,
            "notes": self.notes
        }


# Module tier classification based on research
# These are pre-classified from the research document
RESEARCH_TIERS = {
    # Tier 1: Fully Convertible (utilities with no blockers)
    "flexmark-util-ast": 1,
    "flexmark-util-builder": 1,
    "flexmark-util-collection": 1,
    "flexmark-util-data": 1,
    "flexmark-util-dependency": 1,
    "flexmark-util-format": 1,
    "flexmark-util-html": 1,
    "flexmark-util-misc": 1,
    "flexmark-util-sequence": 1,
    "flexmark-util-visitor": 1,
    "flexmark-util-options": 1,
    "flexmark-util": 1,  # Aggregation module

    # Tier 2: Convertible with dependency replacement or API work
    "flexmark": 2,  # Core has regex usage
    "flexmark-ext-abbreviation": 2,
    "flexmark-ext-admonition": 2,
    "flexmark-ext-anchorlink": 2,
    "flexmark-ext-aside": 2,
    "flexmark-ext-attributes": 2,
    "flexmark-ext-autolink": 2,  # Has replaceable dep (autolink)
    "flexmark-ext-definition": 2,
    "flexmark-ext-emoji": 2,
    "flexmark-ext-enumerated-reference": 2,
    "flexmark-ext-escaped-character": 2,
    "flexmark-ext-footnotes": 2,
    "flexmark-ext-gfm-issues": 2,
    "flexmark-ext-gfm-strikethrough": 2,
    "flexmark-ext-gfm-tasklist": 2,
    "flexmark-ext-gfm-users": 2,
    "flexmark-ext-gitlab": 2,
    "flexmark-ext-ins": 2,
    "flexmark-ext-jekyll-front-matter": 2,
    "flexmark-ext-jekyll-tag": 2,
    "flexmark-ext-macros": 2,
    "flexmark-ext-media-tags": 2,
    "flexmark-ext-resizable-image": 2,
    "flexmark-ext-spec-example": 2,
    "flexmark-ext-superscript": 2,
    "flexmark-ext-tables": 2,
    "flexmark-ext-toc": 2,
    "flexmark-ext-typographic": 2,
    "flexmark-ext-wikilink": 2,
    "flexmark-ext-xwiki-macros": 2,
    "flexmark-ext-yaml-front-matter": 2,
    "flexmark-ext-youtube-embedded": 2,
    "flexmark-ext-zzzzzz": 2,
    "flexmark-html2md-converter": 2,  # Has replaceable dep (jsoup)
    "flexmark-jira-converter": 2,
    "flexmark-youtrack-converter": 2,

    # Tier 3: JVM-Only (cannot convert)
    "flexmark-docx-converter": 3,
    "flexmark-pdf-converter": 3,
    "flexmark-osgi": 3,
    "flexmark-test-util": 3,
    "flexmark-test-specs": 3,
    "flexmark-core-test": 3,
    "flexmark-integration-test": 3,
    "flexmark-profile-pegdown": 3,
    "flexmark-all": 3,  # Uber JAR
    "flexmark-tree-iteration": 3,  # Experimental
    "flexmark-util-experimental": 3,
}


def load_json_report(path: Path) -> Optional[dict]:
    """Load a JSON report file."""
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse {path}: {e}")
        return None


def run_prerequisite_scripts(repo_root: Path, scripts_dir: Path) -> bool:
    """Run prerequisite analysis scripts if reports don't exist."""
    api_report = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis" / "java_api_blockers.json"
    deps_report = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis" / "external_deps.json"

    if not api_report.exists():
        print("Running analyze_java_api_blockers.py...")
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "analyze_java_api_blockers.py"), "--repo-root", str(repo_root)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running analyze_java_api_blockers.py: {result.stderr}")
            return False

    if not deps_report.exists():
        print("Running analyze_external_deps.py...")
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "analyze_external_deps.py"), "--repo-root", str(repo_root)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running analyze_external_deps.py: {result.stderr}")
            return False

    return True


def assess_module(
    module_name: str,
    api_data: Optional[dict],
    deps_data: Optional[dict]
) -> ModuleAssessment:
    """
    Produce a feasibility assessment for a single module.
    """
    notes = []

    # Get API blocker counts
    api_blocker_count = 0
    regex_count = 0
    if api_data:
        for category, data in api_data.items():
            api_blocker_count += data.get("count", 0)
            if category == "regex_pattern_matcher":
                regex_count = data.get("count", 0)

    # Get dependency data
    blocking_deps = []
    replaceable_deps = []
    dep_feasibility = "FEASIBLE"

    if deps_data:
        ext_deps = deps_data.get("external_dependencies", {})
        blocking_deps = [
            f"{d['group_id']}:{d['artifact_id']}"
            for d in ext_deps.get("blocking", [])
        ]
        replaceable_deps = [
            f"{d['group_id']}:{d['artifact_id']}"
            for d in ext_deps.get("replaceable", [])
        ]
        dep_feasibility = deps_data.get("feasibility", "FEASIBLE")

    # Determine tier from research or calculate
    if module_name in RESEARCH_TIERS:
        tier = RESEARCH_TIERS[module_name]
    else:
        # Calculate tier based on analysis
        if blocking_deps:
            tier = 3
        elif replaceable_deps or regex_count > 50:
            tier = 2
        elif api_blocker_count > 0:
            tier = 2
        else:
            tier = 1

    # Determine overall feasibility
    if tier == 3:
        feasibility = "NOT_FEASIBLE"
    elif tier == 2:
        feasibility = "PARTIAL"
    else:
        feasibility = "FEASIBLE"

    # Generate notes
    if blocking_deps:
        notes.append(f"Has blocking dependencies: {', '.join(blocking_deps)}")
    if replaceable_deps:
        notes.append(f"Needs dependency replacement: {', '.join(replaceable_deps)}")
    if regex_count > 0:
        notes.append(f"Uses Pattern/Matcher ({regex_count} occurrences) - needs kotlin.text.Regex migration")
    if api_blocker_count > regex_count:
        other_count = api_blocker_count - regex_count
        notes.append(f"Has {other_count} other Java API usages requiring migration")

    return ModuleAssessment(
        module_name=module_name,
        tier=tier,
        feasibility=feasibility,
        api_blocker_count=api_blocker_count,
        regex_usage_count=regex_count,
        blocking_deps=blocking_deps,
        replaceable_deps=replaceable_deps,
        notes=notes
    )


def generate_report(
    api_report: dict,
    deps_report: dict,
    all_modules: List[str]
) -> dict:
    """Generate the final aggregated report."""

    # Build per-module assessment
    assessments = {}
    for module in all_modules:
        api_data = api_report.get("by_module", {}).get(module, {})
        deps_data = deps_report.get("modules", {}).get(module, {})

        assessment = assess_module(module, api_data, deps_data)
        assessments[module] = assessment.to_dict()

    # Group by tier
    tier_1_modules = [m for m, a in assessments.items() if a["tier"] == 1]
    tier_2_modules = [m for m, a in assessments.items() if a["tier"] == 2]
    tier_3_modules = [m for m, a in assessments.items() if a["tier"] == 3]

    # Calculate summary statistics
    total_regex_usage = sum(a["regex_usage_count"] for a in assessments.values())
    total_api_blockers = sum(a["api_blocker_count"] for a in assessments.values())

    all_blocking_deps = set()
    all_replaceable_deps = set()
    for a in assessments.values():
        all_blocking_deps.update(a["blocking_deps"])
        all_replaceable_deps.update(a["replaceable_deps"])

    return {
        "summary": {
            "total_modules": len(all_modules),
            "tier_breakdown": {
                "tier_1_fully_convertible": len(tier_1_modules),
                "tier_2_convertible_with_effort": len(tier_2_modules),
                "tier_3_jvm_only": len(tier_3_modules)
            },
            "total_regex_usages": total_regex_usage,
            "total_api_blockers": total_api_blockers,
            "unique_blocking_deps": sorted(all_blocking_deps),
            "unique_replaceable_deps": sorted(all_replaceable_deps),
            "conversion_recommendation": generate_recommendation(
                len(tier_1_modules), len(tier_2_modules), len(tier_3_modules),
                total_regex_usage, all_blocking_deps
            )
        },
        "tiers": {
            "tier_1_fully_convertible": sorted(tier_1_modules),
            "tier_2_convertible_with_effort": sorted(tier_2_modules),
            "tier_3_jvm_only": sorted(tier_3_modules)
        },
        "modules": assessments
    }


def generate_recommendation(
    tier1_count: int,
    tier2_count: int,
    tier3_count: int,
    regex_count: int,
    blocking_deps: set
) -> str:
    """Generate a text recommendation based on analysis."""
    convertible = tier1_count + tier2_count
    total = tier1_count + tier2_count + tier3_count
    pct = (convertible / total * 100) if total > 0 else 0

    lines = [
        f"Approximately {convertible} of {total} modules ({pct:.0f}%) are candidates for KMP conversion.",
        "",
        f"Primary effort: Migrate {regex_count} Pattern/Matcher usages to kotlin.text.Regex.",
    ]

    if blocking_deps:
        lines.append(f"Modules with blocking deps ({len(blocking_deps)} unique) must remain JVM-only: DOCX, PDF converters.")

    lines.append("")
    lines.append("Recommended approach: Phased conversion starting with flexmark-util-* modules.")

    return "\n".join(lines)


def print_summary(report: dict) -> None:
    """Print a human-readable summary to console."""
    print("\n" + "=" * 70)
    print("MODULE FEASIBILITY ANALYSIS - SUMMARY")
    print("=" * 70)

    summary = report["summary"]
    print(f"\nTotal modules: {summary['total_modules']}")

    print("\nTier Breakdown:")
    breakdown = summary["tier_breakdown"]
    print(f"  Tier 1 (Fully Convertible):       {breakdown['tier_1_fully_convertible']} modules")
    print(f"  Tier 2 (Convertible with Effort): {breakdown['tier_2_convertible_with_effort']} modules")
    print(f"  Tier 3 (JVM-Only):                {breakdown['tier_3_jvm_only']} modules")

    print(f"\nKey Metrics:")
    print(f"  Total regex usages:   {summary['total_regex_usages']}")
    print(f"  Total API blockers:   {summary['total_api_blockers']}")
    print(f"  Blocking deps:        {len(summary['unique_blocking_deps'])}")
    print(f"  Replaceable deps:     {len(summary['unique_replaceable_deps'])}")

    print("\n" + "-" * 70)
    print("MODULES BY TIER")
    print("-" * 70)

    tiers = report["tiers"]

    print("\n[TIER 1] Fully Convertible (no external blockers):")
    for module in tiers["tier_1_fully_convertible"]:
        print(f"  + {module}")

    print("\n[TIER 2] Convertible with Effort (replaceable deps or API migration):")
    for module in tiers["tier_2_convertible_with_effort"]:
        data = report["modules"][module]
        extras = []
        if data["regex_usage_count"] > 0:
            extras.append(f"regex: {data['regex_usage_count']}")
        if data["replaceable_deps"]:
            extras.append(f"deps: {len(data['replaceable_deps'])}")
        extra_str = f" ({', '.join(extras)})" if extras else ""
        print(f"  ~ {module}{extra_str}")

    print("\n[TIER 3] JVM-Only (cannot convert for Web/JS):")
    for module in tiers["tier_3_jvm_only"]:
        data = report["modules"][module]
        if data["blocking_deps"]:
            print(f"  X {module} - {', '.join(data['blocking_deps'])}")
        else:
            print(f"  X {module}")

    print("\n" + "-" * 70)
    print("RECOMMENDATION")
    print("-" * 70)
    print(summary["conversion_recommendation"])
    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate analysis to produce module-level KMP feasibility assessment"
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
        help="Output JSON file path (default: .ai_out/.../module_feasibility.json)"
    )
    parser.add_argument(
        "--skip-prerequisites",
        action="store_true",
        help="Skip running prerequisite scripts (assume reports exist)"
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    scripts_dir = Path(__file__).parent

    if args.output:
        output_path = args.output
    else:
        output_dir = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "module_feasibility.json"

    # Run prerequisite scripts if needed
    if not args.skip_prerequisites:
        if not run_prerequisite_scripts(repo_root, scripts_dir):
            print("Failed to run prerequisite scripts")
            sys.exit(1)

    # Load prerequisite reports
    api_report_path = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis" / "java_api_blockers.json"
    deps_report_path = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis" / "external_deps.json"

    api_report = load_json_report(api_report_path) or {"by_module": {}}
    deps_report = load_json_report(deps_report_path) or {"modules": {}}

    if not api_report.get("by_module") and not deps_report.get("modules"):
        print("Error: No analysis reports found. Run prerequisite scripts first.")
        sys.exit(1)

    # Get all unique module names
    all_modules = set(api_report.get("by_module", {}).keys())
    all_modules.update(deps_report.get("modules", {}).keys())
    all_modules.update(RESEARCH_TIERS.keys())
    all_modules = sorted(all_modules)

    print(f"Aggregating feasibility analysis for {len(all_modules)} modules...")

    report = generate_report(api_report, deps_report, all_modules)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nJSON report written to: {output_path}")
    print_summary(report)


if __name__ == "__main__":
    main()
