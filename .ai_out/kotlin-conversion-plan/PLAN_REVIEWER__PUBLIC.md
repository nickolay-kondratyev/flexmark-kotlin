# Plan Review: Iteration 2

**Reviewer**: PLAN_REVIEWER
**Date**: 2026-01-12
**Document Reviewed**: `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/.ai_out/kotlin-conversion-plan/PLANNER__PUBLIC.md`
**Previous Review**: Iteration 1 (same file, now replaced)

---

## Verification of Previous Issues

### CRITICAL: Human Conversion Order
**FIXED**

The PLANNER has completely restructured the human conversion order to respect the dependency DAG. The revised plan now correctly shows:

- **Round 1** (Leaves): `flexmark-util-misc`, `flexmark-util-visitor` - both have NO internal deps
- **Round 2**: `flexmark-util-data`, `flexmark-util-collection` - both depend only on `misc`
- **Round 3**: `flexmark-util-sequence`, `flexmark-util-builder` - `sequence` depends on collection, data, misc
- **Round 4**: `flexmark-util-html`, `flexmark-util-options`, `flexmark-util-dependency` - all depend on modules from Round 1-3
- **Round 5**: `flexmark-util-ast` - correctly placed AFTER `sequence` (verified: depends on collection, misc, data, sequence, visitor)
- **Round 6**: `flexmark-util-format` - correctly placed AFTER `ast` AND `html` (verified: depends on ast, collection, data, html, misc, sequence)

I verified these dependencies against the actual pom.xml files:
- `flexmark-util-ast/pom.xml`: depends on collection, misc, data, **sequence**, visitor - CORRECT placement
- `flexmark-util-format/pom.xml`: depends on **ast**, collection, data, **html**, misc, sequence - CORRECT placement

The Dependency Graph diagram (lines 385-428) now accurately reflects the actual module dependencies.

### MAJOR: Module Count
**FIXED**

The plan now clearly states (line 4):
> **Scope**: thorgCore subset (17 production modules + 3 test modules = 20 total)

And in the Module Inventory section (line 26):
> **KEEP (17 production + 3 test = 20 total modules)**

The checkpoint also correctly states (line 355):
> - [ ] Only 20 modules remain (17 production + 3 test)

### MAJOR: flexmark-util-options placement
**FIXED**

I verified from `flexmark-util-options/pom.xml` that it depends on:
- `flexmark-util-misc`
- `flexmark-util-sequence`

The plan now correctly:
1. Documents these dependencies in the Module Inventory table (line 36): `flexmark-util-options | Util | 0 | misc, sequence`
2. Places it in Round 4 (line 458), which is AFTER Round 3 where `flexmark-util-sequence` is converted
3. Notes in Open Questions (line 959-960): "RESOLVED: Verified from pom.xml that it depends on `misc` and `sequence`. It is NOT a leaf module. Placed in Round 4."

### MAJOR: flexmark-ext-typographic removal step
**FIXED**

The plan now includes an explicit, detailed step in Phase 0 (lines 138-151):

```markdown
3. **CRITICAL: Remove test dependency from flexmark-ext-tables/pom.xml**

   The `flexmark-ext-tables` module has a test dependency on `flexmark-ext-typographic` which is being removed.

   **Action**: Remove this block from `flexmark-ext-tables/pom.xml`:
   ```xml
   <dependency>
       <groupId>com.vladsch.flexmark</groupId>
       <artifactId>flexmark-ext-typographic</artifactId>
       <scope>test</scope>
   </dependency>
   ```
```

I verified that this dependency exists in the current `flexmark-ext-tables/pom.xml` (lines 31-33), so this step is necessary and correctly documented.

The verification script also includes (lines 165-166):
```bash
grep -q "flexmark-ext-typographic" flexmark-ext-tables/pom.xml && echo "FAIL: Test dep still present" || echo "OK: Test dep removed"
```

---

## Final Verdict

**APPROVED**

All critical and major issues from the first review have been addressed:

| Issue | Status |
|-------|--------|
| Human conversion order respects DAG | FIXED |
| `flexmark-util-ast` after `flexmark-util-sequence` | FIXED |
| `flexmark-util-format` after `flexmark-util-ast` and `flexmark-util-html` | FIXED |
| Module count clarified (17+3=20) | FIXED |
| `flexmark-util-options` placement verified | FIXED |
| `flexmark-ext-typographic` removal step explicit | FIXED |

The plan is now ready for implementation.

---

## Any New Issues Found

None. The revisions are comprehensive and address all previously identified concerns without introducing new problems.

---

## Summary

The revised plan demonstrates thorough attention to the dependency graph and clear documentation of module relationships. The split into 11 rounds for human conversion ensures that each module is converted only after all its dependencies are complete. The explicit handling of the `flexmark-ext-typographic` test dependency removal prevents a predictable build failure during Phase 0.

The plan follows PARETO principles by targeting only the thorgCore subset and provides clear verification checkpoints at each phase.
