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
