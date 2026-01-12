# Phase 2 & 3: Post-Human Automation

## Overview
After human converts Java to Kotlin:
1. Phase 2: Migrate regex from `java.util.regex` to `kotlin.text.Regex`
2. Phase 3: Restructure for Kotlin Multiplatform

---

## Phase 2: Regex Migration

### Goal
Replace all `java.util.regex.Pattern`/`Matcher` usages with `kotlin.text.Regex` for KMP compatibility.

### Components Affected
- All modules with regex usage (~167 occurrences)

### Delegation Pattern
```
TOP_LEVEL_AGENT delegates to:
  -> IMPLEMENTOR: Creates regex migration script, applies to each module
  -> IMPLEMENTATION_REVIEWER: Verifies correctness, tests pass
```

### Realistic Expectations

The regex migration is split into two parts:
- **Automated (~80%)**: Script handles simple, well-defined patterns
- **Manual review (~20%)**: Human reviews edge cases flagged by script

### Key Steps

1. **Analyze regex usage patterns**

   Common patterns in flexmark:
   ```kotlin
   // Pattern A: Compiled pattern field
   private static final Pattern PATTERN = Pattern.compile("...");
   // Becomes:
   private val PATTERN = Regex("...")

   // Pattern B: Pattern.matcher(input).find()
   if (PATTERN.matcher(input).find()) { ... }
   // Becomes:
   if (PATTERN.containsMatchIn(input)) { ... }

   // Pattern C: Pattern.matcher(input).matches()
   if (PATTERN.matcher(input).matches()) { ... }
   // Becomes:
   if (PATTERN.matches(input)) { ... }

   // Pattern D: Matcher groups
   Matcher m = PATTERN.matcher(input);
   if (m.find()) {
       String group = m.group(1);
   }
   // Becomes:
   val match = PATTERN.find(input)
   if (match != null) {
       val group = match.groupValues[1]
   }

   // Pattern E: replaceAll
   input.replaceAll(PATTERN, replacement)
   // Becomes:
   PATTERN.replace(input, replacement)

   // Pattern F: split
   PATTERN.split(input)
   // Becomes:
   PATTERN.split(input) // Same in Kotlin!
   ```

2. **Create migration script**
   - Location: `kotlin-conversion/scripts/migrate/phase_2_regex/migrate_regex.py`
   - Script must:
     - Parse Kotlin files for Java regex patterns
     - Apply safe transformations for simple cases
     - FLAG complex cases for manual review (multiline patterns, complex Matcher state, etc.)
     - Generate report of changes AND flagged items
     - Be idempotent

3. **Handle regex flags**
   ```kotlin
   // Java flags -> Kotlin RegexOption
   Pattern.CASE_INSENSITIVE -> RegexOption.IGNORE_CASE
   Pattern.MULTILINE -> RegexOption.MULTILINE
   Pattern.DOTALL -> RegexOption.DOT_MATCHES_ALL
   Pattern.UNIX_LINES -> RegexOption.UNIX_LINES
   Pattern.LITERAL -> RegexOption.LITERAL
   Pattern.COMMENTS -> RegexOption.COMMENTS
   ```

4. **Module-by-module migration**

   Order by regex count (lowest first for practice):
   | Module | Regex Count |
   |--------|-------------|
   | flexmark-ext-tables | 4 |
   | flexmark-util-format | 5 |
   | flexmark-util-html | 5 |
   | flexmark-ext-footnotes | 6 |
   | flexmark-util-misc | 7 |
   | flexmark-ext-yaml-front-matter | 14 |
   | flexmark-util-sequence | 32 |
   | flexmark | 135 |

5. **Manual review step after each module**
   - Review flagged items from script
   - Fix edge cases
   - Run tests
   - Commit

6. **Remove java.util.regex imports**
   ```bash
   # Verify no Java regex imports remain
   grep -r "import java.util.regex" --include="*.kt" .
   ```

### Dependencies
- Human Kotlin conversion must be complete

### Verification
```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify no java.util.regex imports
grep -r "import java.util.regex" --include="*.kt" . && echo "FAIL: Java regex still present" || echo "OK: No Java regex"

# Verify build
./gradlew build 2>&1 | tee .tmp/phase2_build.log
grep -q "BUILD SUCCESSFUL" .tmp/phase2_build.log && echo "OK: Build succeeded" || echo "FAIL: Build failed"

# Verify tests
./gradlew test 2>&1 | tee .tmp/phase2_test.log
grep -q "BUILD SUCCESSFUL" .tmp/phase2_test.log && echo "OK: Tests passed" || echo "FAIL: Tests failed"
```

### Rollback Strategy
```bash
git checkout -- "*.kt"
```

---

## Phase 3: Kotlin Multiplatform Structure

### Goal
Restructure the project for Kotlin Multiplatform with commonMain source set.

### Components Affected
- Build files (Gradle)
- Source set structure
- All modules

### Delegation Pattern
```
TOP_LEVEL_AGENT delegates to:
  -> IMPLEMENTOR: Updates build files, moves sources
  -> IMPLEMENTATION_REVIEWER: Verifies structure, tests pass on JVM
```

### Key Steps

1. **Update root build.gradle.kts for KMP**
   ```kotlin
   plugins {
       kotlin("multiplatform") version "2.1.20" apply false
   }

   allprojects {
       group = "com.vladsch.flexmark"
       version = "0.64.8-KMP"

       repositories {
           mavenCentral()
       }
   }
   ```

2. **Update module build.gradle.kts files**

   Example for `flexmark-util-misc/build.gradle.kts`:
   ```kotlin
   plugins {
       kotlin("multiplatform")
   }

   kotlin {
       jvm {
           compilations.all {
               kotlinOptions.jvmTarget = "11"
           }
           testRuns["test"].executionTask.configure {
               useJUnit()
           }
       }
       // JS target (future)
       // js(IR) {
       //     browser()
       //     nodejs()
       // }

       sourceSets {
           val commonMain by getting {
               dependencies {
                   // Common dependencies
               }
           }
           val commonTest by getting {
               dependencies {
                   implementation(kotlin("test"))
               }
           }
           val jvmMain by getting {
               dependencies {
                   // JVM-specific deps
               }
           }
           val jvmTest by getting
       }
   }
   ```

3. **Move sources to commonMain**
   ```bash
   # For each module
   mkdir -p src/commonMain/kotlin
   mkdir -p src/commonTest/kotlin
   mv src/main/kotlin/* src/commonMain/kotlin/
   mv src/test/kotlin/* src/commonTest/kotlin/
   rmdir src/main/kotlin src/main
   rmdir src/test/kotlin src/test
   ```

4. **Handle expect/actual declarations (if needed)**

   Potential areas requiring expect/actual:
   - File I/O (if any remains)
   - Thread synchronization (if any)
   - System properties access

   For flexmark core, most code should be pure computation and work in commonMain.

5. **Create migration script**
   - Location: `kotlin-conversion/scripts/migrate/phase_3_kmp/setup_kmp_structure.py`
   - Script must:
     - Update build.gradle.kts files
     - Move source files to correct source sets
     - Handle resource files
     - Be idempotent

6. **Update test resource handling**
   ```kotlin
   // In build.gradle.kts
   sourceSets {
       val commonTest by getting {
           resources.srcDir("src/commonTest/resources")
       }
   }
   ```

### Dependencies
- Phase 2 (regex migration) must be complete

### Verification
```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify source structure
ls */src/commonMain/kotlin 2>/dev/null | head -5

# Verify JVM target builds
./gradlew jvmJar 2>&1 | tee .tmp/phase3_jvmjar.log
grep -q "BUILD SUCCESSFUL" .tmp/phase3_jvmjar.log && echo "OK: JVM jar built" || echo "FAIL: JVM jar failed"

# Verify JVM tests pass
./gradlew jvmTest 2>&1 | tee .tmp/phase3_jvmtest.log
grep -q "BUILD SUCCESSFUL" .tmp/phase3_jvmtest.log && echo "OK: JVM tests passed" || echo "FAIL: JVM tests failed"
```

### Rollback Strategy
```bash
git checkout -- .
```

---

## Final Checkpoint: KMP Complete

After all phases:
- [ ] No .java files in any module
- [ ] No java.util.regex imports
- [ ] All sources in commonMain/commonTest
- [ ] `./gradlew jvmBuild` succeeds
- [ ] `./gradlew jvmTest` passes
- [ ] Git commit: "Complete Kotlin Multiplatform conversion"

---

## Future Work (Out of Scope)

1. **Enable JS target**
   - Uncomment JS target in build files
   - Verify browser/Node.js compatibility
   - Address any JS-specific issues

2. **Enable Native targets** (if desired)
   - Add native target configurations
   - Handle expect/actual for native platform APIs

3. **Publishing**
   - Configure Maven publishing for KMP artifacts
   - Set up CI/CD for multi-platform builds

---

## Summary

| Phase | Automation | Deliverable | Verification |
|-------|------------|-------------|--------------|
| 0 | Script | Remove 44 modules, fix test deps | Maven build passes |
| 1 | Script | Gradle build files | Gradle build passes |
| Human | Manual | Kotlin source files | Gradle build passes |
| 2 | Script + Manual | KMP-compatible regex | No java.util.regex imports |
| 3 | Script | commonMain structure | jvmTest passes |

Total estimated effort:
- Automated phases: 2-4 hours implementation
- Human conversion: 8-12 hours (more rounds than originally estimated)
- Review and fixes: 2-4 hours
- **Total: 12-20 hours**

---

## Dependency Verification Summary

All dependencies verified from actual pom.xml files:

| Module | Verified Dependencies |
|--------|----------------------|
| flexmark-util-misc | NONE |
| flexmark-util-visitor | NONE |
| flexmark-util-data | misc |
| flexmark-util-collection | misc |
| flexmark-util-sequence | collection, data, misc |
| flexmark-util-html | misc, sequence |
| flexmark-util-options | misc, sequence |
| flexmark-util-builder | misc, data |
| flexmark-util-dependency | collection, misc, data |
| flexmark-util-ast | collection, misc, data, sequence, visitor |
| flexmark-util-format | ast, collection, data, html, misc, sequence |
