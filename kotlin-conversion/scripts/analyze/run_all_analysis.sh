#!/bin/bash
#
# Run all Kotlin Multiplatform feasibility analysis scripts.
#
# This script executes the analysis pipeline:
# 1. analyze_java_api_blockers.py - Detect problematic Java API usage
# 2. analyze_external_deps.py - Analyze Maven dependencies
# 3. analyze_module_feasibility.py - Aggregate and produce final assessment
#
# Usage:
#     ./run_all_analysis.sh [--repo-root PATH]
#
# Output:
#     All JSON reports are written to: <repo-root>/.ai_out/kotlin-mp-feasibility-analysis/
#
# Requirements:
#     Python 3.8+
#

set -e  # Exit on error

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default repo root is two levels up from script directory
REPO_ROOT="${SCRIPT_DIR}/../.."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo-root)
            REPO_ROOT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--repo-root PATH]"
            echo ""
            echo "Run all Kotlin Multiplatform feasibility analysis scripts."
            echo ""
            echo "Options:"
            echo "  --repo-root PATH    Path to repository root (default: two levels up from script)"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Resolve absolute path
REPO_ROOT="$(cd "${REPO_ROOT}" && pwd)"

# Output directory
OUTPUT_DIR="${REPO_ROOT}/.ai_out/kotlin-mp-feasibility-analysis"

echo "=============================================="
echo "Kotlin Multiplatform Feasibility Analysis"
echo "=============================================="
echo ""
echo "Repository: ${REPO_ROOT}"
echo "Output dir: ${OUTPUT_DIR}"
echo ""

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"

# Check Python version
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi

# Verify Python version is 3.8+
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python ${PYTHON_VERSION}"

# Step 1: Analyze Java API blockers
echo ""
echo "----------------------------------------------"
echo "Step 1/3: Analyzing Java API blockers..."
echo "----------------------------------------------"
$PYTHON_CMD "${SCRIPT_DIR}/analyze_java_api_blockers.py" --repo-root "${REPO_ROOT}"

# Step 2: Analyze external dependencies
echo ""
echo "----------------------------------------------"
echo "Step 2/3: Analyzing external dependencies..."
echo "----------------------------------------------"
$PYTHON_CMD "${SCRIPT_DIR}/analyze_external_deps.py" --repo-root "${REPO_ROOT}"

# Step 3: Aggregate module feasibility
echo ""
echo "----------------------------------------------"
echo "Step 3/3: Aggregating module feasibility..."
echo "----------------------------------------------"
$PYTHON_CMD "${SCRIPT_DIR}/analyze_module_feasibility.py" --repo-root "${REPO_ROOT}" --skip-prerequisites

# Summary
echo ""
echo "=============================================="
echo "Analysis Complete"
echo "=============================================="
echo ""
echo "Output files:"
echo "  - ${OUTPUT_DIR}/java_api_blockers.json"
echo "  - ${OUTPUT_DIR}/external_deps.json"
echo "  - ${OUTPUT_DIR}/module_feasibility.json"
echo ""
echo "View the module_feasibility.json for the consolidated assessment."
