# Kotlin Multiplatform Conversion Plan (REVISED)

**Project**: flexmark-java -> flexmark-kotlin
**Scope**: thorgCore subset (17 production modules + 3 test modules = 20 total)
**Date**: 2026-01-12
**Revision**: Addresses PLAN_REVIEWER feedback

---

## Overview

This plan converts a subset of flexmark-java to Kotlin Multiplatform, targeting the modules required by thorgCore. The conversion is split into three phases:

1. **Pre-Human Work** (automated): Remove unused modules, convert Maven to Gradle
2. **Human Work** (manual): Run IntelliJ Java-to-Kotlin converter
3. **Post-Human Work** (automated): Migrate regex patterns, set up KMP structure

### Key Constraints
- Human uses IntelliJ's Java-to-Kotlin converter (NON-NEGOTIABLE)
- Each phase is independently verifiable
- Tests must pass at each checkpoint
- ~167 regex usages need migration for KMP compatibility

### Module Inventory

**KEEP (17 production + 3 test = 20 total modules)**:

| Module | Type | Regex Count | Internal Deps |
|--------|------|-------------|---------------|
| flexmark-util-misc | Util | 7 | NONE |
| flexmark-util-visitor | Util | 0 | NONE |
| flexmark-util-data | Util | 0 | misc |
| flexmark-util-collection | Util | 0 | misc |
| flexmark-util-sequence | Util | 32 | collection, data, misc |
| flexmark-util-html | Util | 5 | misc, sequence |
| flexmark-util-options | Util | 0 | misc, sequence |
| flexmark-util-builder | Util | 0 | misc, data |
| flexmark-util-dependency | Util | 0 | collection, misc, data |
| flexmark-util-ast | Util | 0 | collection, misc, data, sequence, visitor |
| flexmark-util-format | Util | 5 | ast, collection, data, html, misc, sequence |
| flexmark-util | Aggregator | 8 | all util-* |
| flexmark | Core | 135 | all util-* |
| flexmark-ext-tables | Extension | 4 | flexmark, flexmark-util |
| flexmark-ext-footnotes | Extension | 6 | flexmark, flexmark-util |
| flexmark-ext-yaml-front-matter | Extension | 14 | flexmark, flexmark-util |
| flexmark-test-util | Test | N/A | util-* |
| flexmark-test-specs | Test | N/A | test-util |
| flexmark-core-test | Test | N/A | flexmark, test-util, test-specs |

---

## PLAN_PART_1_PRE_HUMAN.md Content

```markdown
# Phase 0 & 1: Pre-Human Automation

## Overview
This phase prepares the codebase for human-driven Kotlin conversion by:
1. Removing unnecessary modules
2. Converting from Maven to Gradle
3. Ensuring build/test infrastructure works

---

## Phase 0: Module Removal

### Goal
Remove 44 unused modules to simplify the codebase before Kotlin conversion.

### Components Affected
- Root pom.xml
- 44 module directories
- `flexmark-ext-tables/pom.xml` (remove test dependency on removed module)

### Delegation Pattern
```
TOP_LEVEL_AGENT delegates to:
  -> IMPLEMENTOR: Creates removal script, executes removal
  -> IMPLEMENTATION_REVIEWER: Verifies removal is complete, build succeeds
```

### Key Steps

1. **Create module removal script**
   - Location: `kotlin-conversion/scripts/migrate/phase_0_remove/remove_modules.py`
   - Script must:
     - Delete module directories
     - Update root pom.xml to remove module references
     - Update root pom.xml dependencyManagement to remove unused deps
     - Be idempotent (can run multiple times safely)

2. **Modules to REMOVE** (44 total):
   ```
   flexmark-all
   flexmark-docx-converter
   flexmark-ext-abbreviation
   flexmark-ext-admonition
   flexmark-ext-anchorlink
   flexmark-ext-aside
   flexmark-ext-attributes
   flexmark-ext-autolink
   flexmark-ext-definition
   flexmark-ext-emoji
   flexmark-ext-enumerated-reference
   flexmark-ext-escaped-character
   flexmark-ext-gfm-issues
   flexmark-ext-gfm-strikethrough
   flexmark-ext-gfm-tasklist
   flexmark-ext-gfm-users
   flexmark-ext-gitlab
   flexmark-ext-ins
   flexmark-ext-jekyll-front-matter
   flexmark-ext-jekyll-tag
   flexmark-ext-macros
   flexmark-ext-media-tags
   flexmark-ext-resizable-image
   flexmark-ext-spec-example
   flexmark-ext-superscript
   flexmark-ext-toc
   flexmark-ext-typographic
   flexmark-ext-wikilink
   flexmark-ext-xwiki-macros
   flexmark-ext-youtube-embedded
   flexmark-ext-zzzzzz
   flexmark-html2md-converter
   flexmark-integration-test
   flexmark-java-samples (if exists)
   flexmark-jira-converter
   flexmark-osgi
   flexmark-pdf-converter
   flexmark-profile-pegdown
   flexmark-tree-iteration
   flexmark-util-experimental
   flexmark-youtrack-converter
   flexmark-formatter-test-suite (if exists)
   ```

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

   **NOTE**: Some tests may fail after this removal. If so, those specific tests should be removed or updated as part of Phase 0.

### Dependencies
- None (first phase)

### Verification
```bash
# Run from repo root
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify module directories are gone
ls -d flexmark-ext-abbreviation 2>/dev/null && echo "FAIL: Module still exists" || echo "OK: Module removed"

# Verify typographic test dependency removed
grep -q "flexmark-ext-typographic" flexmark-ext-tables/pom.xml && echo "FAIL: Test dep still present" || echo "OK: Test dep removed"

# Verify build works
mvn clean compile -DskipTests 2>&1 | tee .tmp/phase0_compile.log
grep -q "BUILD SUCCESS" .tmp/phase0_compile.log && echo "OK: Build succeeded" || echo "FAIL: Build failed"

# Verify tests pass
mvn test -Dsurefire.useFile=false 2>&1 | tee .tmp/phase0_test.log
grep -q "BUILD SUCCESS" .tmp/phase0_test.log && echo "OK: Tests passed" || echo "FAIL: Tests failed"
```

### Rollback Strategy
```bash
git checkout -- pom.xml
git checkout -- flexmark-*/
```

---

## Phase 1: Maven to Gradle Conversion

### Goal
Convert the Maven multi-module project to Gradle with Kotlin DSL, structured for eventual Kotlin Multiplatform.

### Components Affected
- Build system (Maven -> Gradle)
- All kept modules

### Delegation Pattern
```
TOP_LEVEL_AGENT delegates to:
  -> IMPLEMENTOR: Creates Gradle build files
  -> IMPLEMENTATION_REVIEWER: Verifies build/tests work, structure is correct
```

### Key Steps

1. **Initialize Gradle wrapper**
   ```bash
   cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin
   gradle wrapper --gradle-version 8.5
   ```

2. **Create root build.gradle.kts**
   ```kotlin
   // Location: build.gradle.kts
   plugins {
       java
       `java-library`
   }

   allprojects {
       group = "com.vladsch.flexmark"
       version = "0.64.8-KMP"

       repositories {
           mavenCentral()
       }
   }

   subprojects {
       apply(plugin = "java-library")

       java {
           sourceCompatibility = JavaVersion.VERSION_11
           targetCompatibility = JavaVersion.VERSION_11
       }

       dependencies {
           testImplementation("junit:junit:4.13.2")
       }
   }
   ```

3. **Create settings.gradle.kts**
   ```kotlin
   // Location: settings.gradle.kts
   rootProject.name = "flexmark-kotlin"

   // Utility modules (in dependency order for reference)
   include("flexmark-util-misc")
   include("flexmark-util-visitor")
   include("flexmark-util-data")
   include("flexmark-util-collection")
   include("flexmark-util-sequence")
   include("flexmark-util-html")
   include("flexmark-util-options")
   include("flexmark-util-builder")
   include("flexmark-util-dependency")
   include("flexmark-util-ast")
   include("flexmark-util-format")
   include("flexmark-util")

   // Core
   include("flexmark")

   // Extensions
   include("flexmark-ext-tables")
   include("flexmark-ext-footnotes")
   include("flexmark-ext-yaml-front-matter")

   // Test infrastructure
   include("flexmark-test-util")
   include("flexmark-test-specs")
   include("flexmark-core-test")
   ```

4. **Create module build.gradle.kts files**

   Each module needs a `build.gradle.kts` based on its pom.xml dependencies.

   Example for `flexmark-util-sequence/build.gradle.kts`:
   ```kotlin
   plugins {
       `java-library`
   }

   dependencies {
       api(project(":flexmark-util-collection"))
       api(project(":flexmark-util-data"))
       api(project(":flexmark-util-misc"))

       implementation("org.jetbrains:annotations:24.0.1")
   }
   ```

   Example for `flexmark/build.gradle.kts`:
   ```kotlin
   plugins {
       `java-library`
   }

   dependencies {
       api(project(":flexmark-util-ast"))
       api(project(":flexmark-util-builder"))
       api(project(":flexmark-util-collection"))
       api(project(":flexmark-util-data"))
       api(project(":flexmark-util-dependency"))
       api(project(":flexmark-util-format"))
       api(project(":flexmark-util-html"))
       api(project(":flexmark-util-misc"))
       api(project(":flexmark-util-sequence"))
       api(project(":flexmark-util-visitor"))

       testImplementation(project(":flexmark-test-util"))
       testImplementation(project(":flexmark-test-specs"))
   }
   ```

5. **Create conversion script**
   - Location: `kotlin-conversion/scripts/migrate/phase_1_gradle/convert_to_gradle.py`
   - Script should:
     - Parse each module's pom.xml
     - Generate corresponding build.gradle.kts
     - Handle test vs compile dependencies correctly
     - Be idempotent

6. **Remove Maven files after verification**
   - Delete all pom.xml files
   - Delete .mvn directory (if exists)

### Dependencies
- Phase 0 must be complete

### Verification
```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify Gradle build works
./gradlew clean build 2>&1 | tee .tmp/phase1_build.log
grep -q "BUILD SUCCESSFUL" .tmp/phase1_build.log && echo "OK: Gradle build succeeded" || echo "FAIL: Gradle build failed"

# Verify tests pass
./gradlew test 2>&1 | tee .tmp/phase1_test.log
grep -q "BUILD SUCCESSFUL" .tmp/phase1_test.log && echo "OK: Tests passed" || echo "FAIL: Tests failed"

# Verify module structure
./gradlew projects
```

### Rollback Strategy
```bash
git checkout -- .
```

---

## Checkpoint: Pre-Human Complete

Before proceeding to human work, verify:
- [ ] Only 20 modules remain (17 production + 3 test)
- [ ] `./gradlew build` succeeds
- [ ] `./gradlew test` passes all tests
- [ ] No pom.xml files remain
- [ ] Git commit created: "Convert to Gradle, remove unused modules"
```

---

## HUMAN_WORK.md Content

```markdown
# Human Work: Java to Kotlin Conversion

## Overview
Use IntelliJ IDEA's built-in Java-to-Kotlin converter to convert all Java files to Kotlin.

**IMPORTANT**: This is manual work. The LLM does NOT do this conversion.

---

## Prerequisites
- IntelliJ IDEA 2024.x or later (with Kotlin plugin)
- Project imported as Gradle project
- All tests passing before starting

---

## Dependency Graph (Verified from pom.xml)

```
Level 0 (Leaves - NO internal deps):
  flexmark-util-misc
  flexmark-util-visitor

Level 1 (deps on Level 0 only):
  flexmark-util-data         -> misc
  flexmark-util-collection   -> misc

Level 2 (deps on Level 0-1):
  flexmark-util-sequence     -> collection, data, misc
  flexmark-util-builder      -> misc, data

Level 3 (deps on Level 0-2):
  flexmark-util-html         -> misc, sequence
  flexmark-util-options      -> misc, sequence
  flexmark-util-dependency   -> collection, misc, data

Level 4 (deps on Level 0-3):
  flexmark-util-ast          -> collection, misc, data, sequence, visitor

Level 5 (deps on Level 0-4):
  flexmark-util-format       -> ast, collection, data, html, misc, sequence

Level 6 (aggregator):
  flexmark-util              -> all util-*

Level 7 (test infrastructure):
  flexmark-test-util         -> util-*

Level 8:
  flexmark-test-specs        -> test-util

Level 9 (core):
  flexmark                   -> util-*, test-util, test-specs

Level 10 (extensions):
  flexmark-ext-tables        -> flexmark, flexmark-util
  flexmark-ext-footnotes     -> flexmark, flexmark-util
  flexmark-ext-yaml-front-matter -> flexmark, flexmark-util

Level 11 (core tests):
  flexmark-core-test         -> flexmark, test-util, test-specs
```

---

## Conversion Order (MUST FOLLOW)

Convert modules in strict dependency order. A module can ONLY be converted after ALL its dependencies are converted.

### Round 1: Leaf Utility Modules (no internal deps)
| # | Module | Dependencies |
|---|--------|--------------|
| 1 | `flexmark-util-misc` | NONE |
| 2 | `flexmark-util-visitor` | NONE |

### Round 2: First-Level Dependents
| # | Module | Dependencies |
|---|--------|--------------|
| 3 | `flexmark-util-data` | misc |
| 4 | `flexmark-util-collection` | misc |

### Round 3: Second-Level Dependents
| # | Module | Dependencies |
|---|--------|--------------|
| 5 | `flexmark-util-sequence` | collection, data, misc |
| 6 | `flexmark-util-builder` | misc, data |

### Round 4: Third-Level Dependents
| # | Module | Dependencies |
|---|--------|--------------|
| 7 | `flexmark-util-html` | misc, sequence |
| 8 | `flexmark-util-options` | misc, sequence |
| 9 | `flexmark-util-dependency` | collection, misc, data |

### Round 5: Fourth-Level Dependents
| # | Module | Dependencies |
|---|--------|--------------|
| 10 | `flexmark-util-ast` | collection, misc, data, sequence, visitor |

### Round 6: Fifth-Level Dependents
| # | Module | Dependencies |
|---|--------|--------------|
| 11 | `flexmark-util-format` | ast, collection, data, html, misc, sequence |

### Round 7: Aggregator
| # | Module | Dependencies |
|---|--------|--------------|
| 12 | `flexmark-util` | all util-* |

### Round 8: Test Infrastructure
| # | Module | Dependencies |
|---|--------|--------------|
| 13 | `flexmark-test-util` | util-* |
| 14 | `flexmark-test-specs` | test-util |

### Round 9: Core Parser
| # | Module | Dependencies |
|---|--------|--------------|
| 15 | `flexmark` | util-*, test-util, test-specs |

### Round 10: Extensions
| # | Module | Dependencies |
|---|--------|--------------|
| 16 | `flexmark-ext-tables` | flexmark, util |
| 17 | `flexmark-ext-footnotes` | flexmark, util |
| 18 | `flexmark-ext-yaml-front-matter` | flexmark, util |

### Round 11: Core Tests
| # | Module | Dependencies |
|---|--------|--------------|
| 19 | `flexmark-core-test` | flexmark, test-util, test-specs |

---

## Step-by-Step Instructions

### For Each Module:

1. **Open module in IntelliJ Project view**
   - Navigate to `src/main/java`

2. **Select all Java files**
   - Right-click on the `com.vladsch.flexmark` package
   - Or select all .java files

3. **Convert to Kotlin**
   - Menu: Code -> Convert Java File to Kotlin File
   - Or: Ctrl+Alt+Shift+K (Cmd+Alt+Shift+K on Mac)

4. **Handle conversion dialogs**
   - "Correct code after conversion": Yes
   - "Configure Kotlin": Accept defaults (Kotlin version 1.9.x)

5. **Move Kotlin files**
   - Move converted .kt files from `src/main/java` to `src/main/kotlin`
   - Create `src/main/kotlin` if it doesn't exist
   - Maintain package directory structure

6. **Repeat for test sources**
   - Convert `src/test/java` -> `src/test/kotlin`

7. **Build and fix errors**
   ```bash
   ./gradlew :module-name:build
   ```
   - Fix any compilation errors (IntelliJ will highlight them)
   - Common fixes:
     - Add `!!` for null assertions
     - Fix visibility modifiers
     - Handle Java interop issues

8. **Run tests**
   ```bash
   ./gradlew :module-name:test
   ```

9. **Commit after each module**
   ```bash
   git add .
   git commit -m "Convert module-name to Kotlin"
   ```

---

## Common Conversion Issues

### 1. Nullable Types
IntelliJ may not correctly infer nullability. Watch for:
- Parameters marked `@Nullable` in Java -> should be `Type?` in Kotlin
- Parameters marked `@NotNull` in Java -> should be `Type` in Kotlin

### 2. Static Members
Java static members become:
- `companion object` for constants
- Top-level functions/properties for utilities

### 3. Getters/Setters
Java getters/setters become Kotlin properties:
```java
// Java
public String getName() { return name; }
public void setName(String name) { this.name = name; }

// Kotlin (auto-converted)
var name: String
```

### 4. Checked Exceptions
Kotlin doesn't have checked exceptions. `@Throws` annotation may be needed for Java interop.

### 5. Pattern/Matcher (DO NOT FIX YET)
The converter will leave `java.util.regex.Pattern` and `Matcher` as-is.
**DO NOT manually fix these** - Phase 2 automation handles this.

---

## Verification After Each Round

```bash
# After converting each round of modules
./gradlew build
./gradlew test

# Verify no Java files remain in converted modules
find flexmark-util-misc/src -name "*.java" | wc -l  # Should be 0
```

---

## Checkpoint: Human Work Complete

Before proceeding to Phase 2:
- [ ] All .java files converted to .kt
- [ ] All files moved to src/main/kotlin and src/test/kotlin
- [ ] `./gradlew build` succeeds
- [ ] `./gradlew test` passes
- [ ] Git commit: "Convert all modules to Kotlin"

---

## Estimated Time
- Per module: 15-30 minutes
- Total: 8-12 hours (19 conversion units, some rounds have multiple modules)

---

## Troubleshooting

### Build fails after conversion
1. Check IntelliJ "Problems" view for errors
2. Most issues are nullability-related
3. Look for `!!` suggestions from IntelliJ

### Tests fail after conversion
1. Check if test resources are in correct location
2. Verify test class names match file names
3. Check for reflection-based test discovery issues

### Module won't compile but dependency order seems right
1. Verify that ALL dependencies (direct AND transitive) are converted
2. Check the dependency table above - some modules have more deps than expected
3. Run `./gradlew :module-name:dependencies` to see full dependency tree
```

---

## PLAN_PART_2_POST_HUMAN.md Content

```markdown
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
       kotlin("multiplatform") version "1.9.22" apply false
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
```

---

## Open Questions (Addressed)

1. **flexmark-ext-tables test dependency on flexmark-ext-typographic**
   - RESOLVED: Explicit step added to Phase 0 to remove this test dependency from `flexmark-ext-tables/pom.xml`

2. **flexmark-util-options dependencies**
   - RESOLVED: Verified from pom.xml that it depends on `misc` and `sequence`. It is NOT a leaf module. Placed in Round 4 (third-level dependents).

3. **Module count**
   - RESOLVED: Clarified as "17 production + 3 test = 20 total modules to KEEP"

4. **Test resource loading**
   - flexmark-test-specs contains CommonMark spec files loaded at test time
   - RESOLUTION: Keep in JVM test resources initially. Can be moved to commonTest resources when JS target is enabled.

5. **Unicode regex categories**
   - Some patterns use `\p{Pc}`, `\p{Pd}` which may behave differently in JS
   - RESOLUTION: Flag for testing when JS target is enabled. Not a blocker for JVM.

6. **ThreadLocal and synchronized**
   - Feasibility report mentions 10 usages
   - RESOLUTION: Investigate during Phase 2/3. May need expect/actual or refactoring for KMP.

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
