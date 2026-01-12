# PLAN_REVIEWER Private Notes

**Date**: 2026-01-12
**Reviewing**: PLANNER__PUBLIC.md (Kotlin Conversion Plan)

## Analysis Summary

### Module Counts Verification
- pom.xml lists 59 modules
- Plan says 17 KEEP + 44 REMOVE = 61 modules
- Directory count: 62 (includes java-samples if it exists)
- MINOR DISCREPANCY: Math is slightly off but not blocking

### Module List Verification (17 to KEEP)
Verified against feasibility report (thorgCore subset):
1. flexmark - YES (core)
2. flexmark-util - YES (aggregator)
3. flexmark-util-ast - YES
4. flexmark-util-builder - YES
5. flexmark-util-collection - YES
6. flexmark-util-data - YES
7. flexmark-util-dependency - YES
8. flexmark-util-format - YES
9. flexmark-util-html - YES
10. flexmark-util-misc - YES
11. flexmark-util-options - YES
12. flexmark-util-sequence - YES
13. flexmark-util-visitor - YES
14. flexmark-ext-tables - YES
15. flexmark-ext-footnotes - YES
16. flexmark-ext-yaml-front-matter - YES
17. flexmark-test-util - YES
18. flexmark-test-specs - YES (ADDED)
19. flexmark-core-test - YES (ADDED)

ISSUE: Plan module table shows 17 modules + 3 test modules = 20 lines, but says "17 modules"
Actually, the table shows 19 modules if we count. Test modules are listed separately.

### Dependency Order Issues Found

The plan's "Conversion Order" has problems:

**Plan says:**
Round 1: misc, data, options, visitor, builder (leaf modules)
Round 2: collection (deps: misc), dependency (deps: misc), ast (deps: misc, data, visitor), format (deps: misc, data, sequence), sequence (deps: collection, data, misc), html (deps: misc, sequence)

**PROBLEM:**
- flexmark-util-ast depends on flexmark-util-sequence
- flexmark-util-format depends on flexmark-util-ast and flexmark-util-html
- So the order should have sequence BEFORE ast, and ast BEFORE format

**Correct dependency graph (verified from pom.xml):**
- misc: no deps
- data: no deps (likely)
- options: no deps (likely)
- visitor: no deps
- builder: no deps
- collection: deps on misc
- dependency: deps on misc
- sequence: deps on collection, data, misc
- html: deps on misc, sequence
- ast: deps on collection, misc, data, sequence, visitor
- format: deps on ast, collection, data, html, misc, sequence

**CORRECTED ORDER:**
Round 1: misc, data, options, visitor, builder (true leaves)
Round 2: collection (deps: misc), dependency (deps: misc)
Round 3: sequence (deps: collection, data, misc)
Round 4: html (deps: misc, sequence), ast (deps: collection, misc, data, sequence, visitor)
Round 5: format (deps: ast, collection, data, html, misc, sequence)
Round 6: util (aggregator)

### Test Dependency Issue
flexmark-ext-tables has test dependency on flexmark-ext-typographic (being removed).
Plan acknowledges this and says "Remove this test dependency in Phase 0"
This is CORRECT approach.

### Regex Migration Approach
The plan proposes scripting the regex migration. This is ambitious.
167 regex usages is substantial but patterns are repetitive.
Semi-automated (script + manual review) is more realistic than fully automated.

### PARETO Assessment
Plan is appropriately scoped for thorgCore subset.
Does NOT try to convert all 61 modules (good).
Focuses on the 17 modules actually needed.
