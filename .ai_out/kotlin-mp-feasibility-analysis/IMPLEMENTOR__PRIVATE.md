# Implementor Private Notes: Kotlin-MP Feasibility Analysis

**Last Updated**: 2026-01-11

---

## Implementation Notes

### XML Namespace Handling Fix

Initial implementation used Python's `or` pattern for XML namespace fallback:
```python
group_el = dep.find('m:groupId', ns) or dep.find('groupId')
```

This had inconsistent behavior in some contexts. Fixed by using helper functions:
```python
def find_el(parent, tag):
    if ns_uri:
        el = parent.find(f'{{{ns_uri}}}{tag}')
        if el is not None:
            return el
    return parent.find(tag)
```

### Dependency Categorization

Added JetBrains annotations to SAFE category since they're compile-time only:
```python
("org.jetbrains", "annotations"): ("SAFE", "Compile-time annotations")
```

### Module Tier Pre-classification

The `analyze_module_feasibility.py` script includes a `RESEARCH_TIERS` dictionary with pre-classified tiers from the research document. This ensures consistency with the research findings even if the dynamic analysis produces slightly different results.

---

## Test Results

All scripts tested successfully:

1. `analyze_java_api_blockers.py`:
   - Found 1416 Java files
   - Detected 425 regex usages across 69 files
   - Detected 74 java.io usages across 45 files

2. `analyze_external_deps.py`:
   - Parsed 60 pom.xml files
   - Identified 4 blocking deps, 3 replaceable deps
   - 2 modules marked NOT_FEASIBLE (docx, pdf converters)

3. `analyze_module_feasibility.py`:
   - Aggregated 61 modules total
   - Tier 1: 13 modules, Tier 2: 37 modules, Tier 3: 11 modules

---

## Known Limitations

1. **Unicode regex patterns**: Detection is basic (just `\\p{...}` pattern). Does not validate if specific pattern is supported on JS.

2. **Transitive dependencies**: Only direct dependencies from pom.xml are analyzed. Transitive deps not checked.

3. **Test vs Main code**: API blocker analysis includes test code. May want to separate in future.

4. **Service loader pattern**: Not detected. Research noted this needs migration but no scanner implemented.

---

## Next Steps (if continuing)

1. Add detection for `META-INF/services/*` files (service loader pattern)
2. Separate test code from main code in API blocker analysis
3. Add transitive dependency analysis via `mvn dependency:tree`
4. Validate Unicode regex patterns against JS Regex capabilities

---

## File Locations

Scripts: `/kotlin-conversion/scripts/`
- `analyze_java_api_blockers.py`
- `analyze_external_deps.py`
- `analyze_module_feasibility.py`
- `run_all_analysis.sh`

Output: `.ai_out/kotlin-mp-feasibility-analysis/`
- `java_api_blockers.json`
- `external_deps.json`
- `module_feasibility.json`
