# IMPLEMENTATION_PLANNER Private Notes

## Analysis Summary

### Module Count Verification

**Modules in pom.xml**: 60
**Directories on filesystem**: 63 (includes `_full_source` which is not a module, and 3 extra test directories)

**Extra directories NOT in pom.xml**:
- `flexmark-formatter-test-suite` - EXISTS
- `flexmark-java-samples` - EXISTS (exit code showed error but directory confirmed in ls output)
- `flexmark-test-suite` - EXISTS

These should be deleted as part of Phase 0 cleanup.

### Dependency Analysis Complete

All 19 kept module pom.xml files have been read and dependencies extracted:

| Module | Dependencies |
|--------|--------------|
| flexmark-util-misc | (none - base) |
| flexmark-util-visitor | (none - base) |
| flexmark-util-data | flexmark-util-misc |
| flexmark-util-collection | flexmark-util-misc |
| flexmark-util-sequence | flexmark-util-collection, flexmark-util-data, flexmark-util-misc |
| flexmark-util-html | flexmark-util-misc, flexmark-util-sequence |
| flexmark-util-options | flexmark-util-misc, flexmark-util-sequence |
| flexmark-util-builder | flexmark-util-misc, flexmark-util-data |
| flexmark-util-dependency | flexmark-util-collection, flexmark-util-misc, flexmark-util-data |
| flexmark-util-ast | flexmark-util-collection, flexmark-util-misc, flexmark-util-data, flexmark-util-sequence, flexmark-util-visitor |
| flexmark-util-format | flexmark-util-ast, flexmark-util-collection, flexmark-util-data, flexmark-util-html, flexmark-util-misc, flexmark-util-sequence |
| flexmark-util | (aggregate - depends on all util-*) |
| flexmark | flexmark-util-ast, flexmark-util-builder, flexmark-util-collection, flexmark-util-data, flexmark-util-dependency, flexmark-util-format, flexmark-util-html, flexmark-util-misc, flexmark-util-sequence, flexmark-util-visitor |
| flexmark-test-util | flexmark-util-misc, flexmark-util-data, flexmark-util-ast, flexmark-util-format, flexmark-util-sequence + junit (NOT test scope) |
| flexmark-test-specs | flexmark-test-util |
| flexmark-core-test | flexmark, flexmark-util, flexmark-test-util, flexmark-test-specs |
| flexmark-ext-tables | flexmark-util, flexmark |
| flexmark-ext-footnotes | flexmark-util, flexmark + test dep on flexmark-ext-tables |
| flexmark-ext-yaml-front-matter | flexmark-util, flexmark |

### Typographic Dependency Impact

The `flexmark-ext-tables` module has exactly 1 test case using the typographic extension:

**Location in spec file**: Line 3611 of `ext_tables_ast_spec.md`
```
```````````````````````````````` example(DoNotDecorate: 2) options(typographic)
```

**Test option definition**: Line 36 of `ComboTableSpecTest.java`
```java
optionsMap.put("typographic", new MutableDataSet().set(Parser.EXTENSIONS, Arrays.asList(TablesExtension.create(), TypographicExtension.create())));
```

**Import statement**: Line 4 of `ComboTableSpecTest.java`
```java
import com.vladsch.flexmark.ext.typographic.TypographicExtension;
```

### Key Decisions Made

1. **api() vs implementation()**: Using `api()` for all project dependencies since these are library modules where transitive dependencies should be exposed to consumers.

2. **JetBrains annotations**: Kept as `implementation()` since these are compile-time only annotations.

3. **JUnit in flexmark-test-util**: Using `api()` because this module IS the test utility module that provides JUnit capabilities to other modules.

4. **Gradle version**: Using 8.5 as specified in the high-level plan.

### Potential Issues Identified

1. **flexmark-util is aggregate module**: It simply re-exports all other util modules. In Gradle, this is done via `api()` dependencies.

2. **flexmark-test-util has JUnit as compile dependency** (not test): This is intentional since this module provides test utilities.

3. **flexmark-ext-footnotes has test dependency on flexmark-ext-tables**: This is kept since flexmark-ext-tables is being kept.

### Files to Examine for Typographic Test Removal

Need to remove from `ext_tables_ast_spec.md`:
- The entire `DoNotDecorate: 2` example block starting at line 3611
- This includes the test case markdown, expected HTML, and expected AST

The block appears to span from line 3611 to approximately line 3650 (based on the AST output seen in grep).

### Implementation Notes for IMPLEMENTOR

1. **Phase 0 should be done FIRST** and verified before starting Phase 1.

2. **Git commit after Phase 0**: Create commit "Remove unused modules (44 modules deleted)"

3. **Git commit after Phase 1**: Create commit "Convert to Gradle with Kotlin DSL"

4. **Keep both build systems temporarily**: During Phase 1, keep pom.xml files until Gradle is verified working. Then delete them.

### Verification Commands Summary

**Phase 0**:
```bash
# After module removal
mvn clean compile -DskipTests
mvn test -Dsurefire.useFile=false
```

**Phase 1**:
```bash
# After Gradle setup
./gradlew clean build -x test
./gradlew test
./gradlew projects
```

### Rollback Strategies

**Phase 0 rollback**:
```bash
git checkout -- pom.xml
git checkout -- flexmark-ext-tables/
# For deleted directories: git checkout -- flexmark-*/ (won't restore them)
# Better: use git stash or work on a branch
```

**Phase 1 rollback**:
```bash
git checkout -- .
# Or if on branch, just switch back to previous branch
```

### Module Count Discrepancy

The high-level plan says "20 modules (17 production + 3 test)".

My analysis:
- 12 utility modules (production)
- 1 core module (flexmark) (production)
- 3 test modules (flexmark-test-util, flexmark-test-specs, flexmark-core-test)
- 3 extension modules (production)

Total: 16 production + 3 test = 19 modules

This is flagged as #QUESTION_FOR_HUMAN in the public plan.

The difference might be:
1. A typo in the high-level plan
2. A module I missed
3. Different counting methodology

Looking at the settings.gradle.kts in the high-level plan, it lists:
- flexmark-util-misc
- flexmark-util-visitor
- flexmark-util-data
- flexmark-util-collection
- flexmark-util-sequence
- flexmark-util-html
- flexmark-util-options
- flexmark-util-builder
- flexmark-util-dependency
- flexmark-util-ast
- flexmark-util-format
- flexmark-util
- flexmark
- flexmark-ext-tables
- flexmark-ext-footnotes
- flexmark-ext-yaml-front-matter
- flexmark-test-util
- flexmark-test-specs
- flexmark-core-test

That's exactly 19 modules, matching my count. So the "20 modules" in the high-level plan appears to be a minor error.
