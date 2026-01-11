#!/usr/bin/env python3
"""
Analyze Java API usage that blocks Kotlin Multiplatform conversion.

This script scans Java source files for usage of APIs that lack Kotlin-MP equivalents
and generates a JSON report of findings.

Detects:
- java.util.regex.Pattern/Matcher - Core regex, requires migration to kotlin.text.Regex
- java.io.* / java.nio.* - File I/O, needs kotlinx-io or expect/actual
- java.awt.* - AWT dependencies, platform-specific styling
- java.lang.reflect.* - Reflection, needs redesign
- synchronized / ThreadLocal - Concurrency primitives

Usage:
    python analyze_java_api_blockers.py [--repo-root PATH] [--output PATH]

Output:
    JSON report with file locations and counts per category.
"""

import argparse
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class Finding:
    """A single occurrence of a blocking API usage."""
    file: str
    line_number: int
    line_content: str
    pattern_matched: str


@dataclass
class CategoryReport:
    """Report for a single API category."""
    count: int = 0
    files: Set[str] = field(default_factory=set)
    findings: List[Finding] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "file_count": len(self.files),
            "files": sorted(self.files),
            "findings": [
                {
                    "file": f.file,
                    "line_number": f.line_number,
                    "line_content": f.line_content.strip(),
                    "pattern_matched": f.pattern_matched
                }
                for f in self.findings
            ]
        }


# API categories and their detection patterns
API_CATEGORIES = {
    "regex_pattern_matcher": {
        "description": "java.util.regex.Pattern/Matcher usage - requires kotlin.text.Regex migration",
        "impact": "HIGH",
        "patterns": [
            (r'Pattern\.compile\s*\(', "Pattern.compile()"),
            (r'import\s+java\.util\.regex\.Pattern\b', "import Pattern"),
            (r'import\s+java\.util\.regex\.Matcher\b', "import Matcher"),
            (r'import\s+java\.util\.regex\.\*', "import java.util.regex.*"),
            (r'\bMatcher\s+\w+\s*=', "Matcher variable declaration"),
            (r'\.matcher\s*\(', ".matcher() call"),
        ]
    },
    "java_io": {
        "description": "java.io.* usage - needs kotlinx-io or expect/actual",
        "impact": "MEDIUM",
        "patterns": [
            (r'import\s+java\.io\.File\b', "import java.io.File"),
            (r'import\s+java\.io\.InputStream\b', "import java.io.InputStream"),
            (r'import\s+java\.io\.OutputStream\b', "import java.io.OutputStream"),
            (r'import\s+java\.io\.Reader\b', "import java.io.Reader"),
            (r'import\s+java\.io\.Writer\b', "import java.io.Writer"),
            (r'import\s+java\.io\.BufferedReader\b', "import java.io.BufferedReader"),
            (r'import\s+java\.io\.BufferedWriter\b', "import java.io.BufferedWriter"),
            (r'import\s+java\.io\.IOException\b', "import java.io.IOException"),
            (r'import\s+java\.io\.\*', "import java.io.*"),
        ]
    },
    "java_nio": {
        "description": "java.nio.* usage - needs kotlinx-io or expect/actual",
        "impact": "LOW",
        "patterns": [
            (r'import\s+java\.nio\.file\.\w+', "import java.nio.file.*"),
            (r'import\s+java\.nio\.charset\.\w+', "import java.nio.charset.*"),
            (r'import\s+java\.nio\.\*', "import java.nio.*"),
        ]
    },
    "java_awt": {
        "description": "java.awt.* usage - platform-specific styling",
        "impact": "LOW",
        "patterns": [
            (r'import\s+java\.awt\.Color\b', "import java.awt.Color"),
            (r'import\s+java\.awt\.Font\b', "import java.awt.Font"),
            (r'import\s+java\.awt\.\w+', "import java.awt.*"),
        ]
    },
    "reflection": {
        "description": "java.lang.reflect.* usage - needs redesign",
        "impact": "LOW",
        "patterns": [
            (r'import\s+java\.lang\.reflect\.\w+', "import java.lang.reflect.*"),
            (r'\.getClass\s*\(\s*\)\s*\.getMethod', "getClass().getMethod()"),
            (r'\.getDeclaredMethod\s*\(', ".getDeclaredMethod()"),
            (r'\.getField\s*\(', ".getField()"),
            (r'\.getDeclaredField\s*\(', ".getDeclaredField()"),
            (r'Method\.invoke\s*\(', "Method.invoke()"),
        ]
    },
    "concurrency": {
        "description": "Concurrency primitives - needs kotlinx.atomicfu or platform-specific",
        "impact": "LOW",
        "patterns": [
            (r'\bsynchronized\s*\(', "synchronized block"),
            (r'\bsynchronized\s+\w+\s*\(', "synchronized method"),
            (r'ThreadLocal<', "ThreadLocal usage"),
            (r'import\s+java\.util\.concurrent\.\w+', "import java.util.concurrent.*"),
        ]
    },
    "unicode_regex_patterns": {
        "description": "Unicode property patterns in regex - may have JS compatibility issues",
        "impact": "HIGH",
        "patterns": [
            (r'\\\\p\{[A-Za-z]+\}', "Unicode property pattern \\p{...}"),
        ]
    }
}


def find_java_files(repo_root: Path) -> List[Path]:
    """Find all Java source files in the repository, excluding test directories."""
    java_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('target', 'build')]

        for file in files:
            if file.endswith('.java'):
                java_files.append(Path(root) / file)

    return java_files


def get_module_name(file_path: Path, repo_root: Path) -> str:
    """Extract module name from file path."""
    rel_path = file_path.relative_to(repo_root)
    parts = rel_path.parts
    if parts and parts[0].startswith('flexmark'):
        return parts[0]
    return "unknown"


def analyze_file(file_path: Path, repo_root: Path) -> Dict[str, CategoryReport]:
    """Analyze a single Java file for blocking API usage."""
    results = {cat: CategoryReport() for cat in API_CATEGORIES}
    rel_path = str(file_path.relative_to(repo_root))

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return results

    for line_num, line in enumerate(lines, start=1):
        for category, config in API_CATEGORIES.items():
            for pattern_str, pattern_name in config["patterns"]:
                if re.search(pattern_str, line):
                    results[category].count += 1
                    results[category].files.add(rel_path)
                    results[category].findings.append(Finding(
                        file=rel_path,
                        line_number=line_num,
                        line_content=line,
                        pattern_matched=pattern_name
                    ))

    return results


def merge_reports(reports: List[Dict[str, CategoryReport]]) -> Dict[str, CategoryReport]:
    """Merge multiple file reports into a single report."""
    merged = {cat: CategoryReport() for cat in API_CATEGORIES}

    for report in reports:
        for category, category_report in report.items():
            merged[category].count += category_report.count
            merged[category].files.update(category_report.files)
            merged[category].findings.extend(category_report.findings)

    return merged


def analyze_by_module(java_files: List[Path], repo_root: Path) -> Dict[str, Dict[str, CategoryReport]]:
    """Analyze files grouped by module."""
    module_reports = defaultdict(list)

    for file_path in java_files:
        module = get_module_name(file_path, repo_root)
        report = analyze_file(file_path, repo_root)
        module_reports[module].append(report)

    return {
        module: merge_reports(reports)
        for module, reports in module_reports.items()
    }


def generate_report(module_reports: Dict[str, Dict[str, CategoryReport]]) -> dict:
    """Generate the final JSON report structure."""
    # Aggregate totals
    totals = {cat: CategoryReport() for cat in API_CATEGORIES}
    for module, categories in module_reports.items():
        for category, report in categories.items():
            totals[category].count += report.count
            totals[category].files.update(report.files)
            totals[category].findings.extend(report.findings)

    return {
        "summary": {
            category: {
                "description": API_CATEGORIES[category]["description"],
                "impact": API_CATEGORIES[category]["impact"],
                "total_occurrences": totals[category].count,
                "files_affected": len(totals[category].files)
            }
            for category in API_CATEGORIES
        },
        "by_module": {
            module: {
                category: report.to_dict()
                for category, report in categories.items()
                if report.count > 0
            }
            for module, categories in sorted(module_reports.items())
            if any(r.count > 0 for r in categories.values())
        },
        "totals": {
            category: totals[category].to_dict()
            for category in API_CATEGORIES
        }
    }


def print_summary(report: dict) -> None:
    """Print a human-readable summary to console."""
    print("\n" + "=" * 70)
    print("JAVA API BLOCKERS ANALYSIS - SUMMARY")
    print("=" * 70)

    for category, data in report["summary"].items():
        if data["total_occurrences"] > 0:
            print(f"\n[{data['impact']}] {category}")
            print(f"  Description: {data['description']}")
            print(f"  Occurrences: {data['total_occurrences']}")
            print(f"  Files affected: {data['files_affected']}")

    print("\n" + "-" * 70)
    print("BY MODULE (modules with blockers):")
    print("-" * 70)

    for module, categories in report["by_module"].items():
        total = sum(c["count"] for c in categories.values())
        print(f"\n  {module}: {total} occurrences")
        for cat, data in categories.items():
            if data["count"] > 0:
                print(f"    - {cat}: {data['count']} in {data['file_count']} files")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Java API usage that blocks Kotlin Multiplatform conversion"
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
        help="Output JSON file path (default: .ai_out/.../java_api_blockers.json)"
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.output:
        output_path = args.output
    else:
        output_dir = repo_root / ".ai_out" / "kotlin-mp-feasibility-analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "java_api_blockers.json"

    print(f"Analyzing Java files in: {repo_root}")

    java_files = find_java_files(repo_root)
    print(f"Found {len(java_files)} Java files")

    module_reports = analyze_by_module(java_files, repo_root)
    report = generate_report(module_reports)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nJSON report written to: {output_path}")
    print_summary(report)


if __name__ == "__main__":
    main()
