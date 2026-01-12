# Detailed Implementation Plan: Phase 0 and Phase 1

## Overview

This document provides a complete, actionable implementation plan for:
1. **Phase 0**: Remove 44 unused Maven modules
2. **Phase 1**: Convert remaining modules from Maven to Gradle with Kotlin DSL

---

## Module Inventory

### Current State: 60 Modules in pom.xml

The root `pom.xml` defines 60 modules:

```
flexmark
flexmark-all
flexmark-core-test
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
flexmark-ext-footnotes
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
flexmark-ext-tables
flexmark-ext-toc
flexmark-ext-typographic
flexmark-ext-wikilink
flexmark-ext-xwiki-macros
flexmark-ext-yaml-front-matter
flexmark-ext-youtube-embedded
flexmark-ext-zzzzzz
flexmark-html2md-converter
flexmark-integration-test
flexmark-jira-converter
flexmark-osgi
flexmark-pdf-converter
flexmark-profile-pegdown
flexmark-test-specs
flexmark-test-util
flexmark-tree-iteration
flexmark-util
flexmark-util-ast
flexmark-util-builder
flexmark-util-collection
flexmark-util-data
flexmark-util-dependency
flexmark-util-experimental
flexmark-util-format
flexmark-util-html
flexmark-util-misc
flexmark-util-options
flexmark-util-sequence
flexmark-util-visitor
flexmark-youtrack-converter
```

### Directories Present But Not in pom.xml

Found in filesystem but NOT in pom.xml (these can be deleted along with removal):
- `flexmark-formatter-test-suite` - EXISTS on filesystem, NOT in pom.xml
- `flexmark-java-samples` - Directory exists but NOT in pom.xml
- `flexmark-test-suite` - EXISTS on filesystem, NOT in pom.xml

### Modules to KEEP (20 total)

#### Utility Modules (12 modules)
1. `flexmark-util-misc` - No project deps (base)
2. `flexmark-util-visitor` - No project deps (base)
3. `flexmark-util-data` - deps: flexmark-util-misc
4. `flexmark-util-collection` - deps: flexmark-util-misc
5. `flexmark-util-sequence` - deps: flexmark-util-collection, flexmark-util-data, flexmark-util-misc
6. `flexmark-util-html` - deps: flexmark-util-misc, flexmark-util-sequence
7. `flexmark-util-options` - deps: flexmark-util-misc, flexmark-util-sequence
8. `flexmark-util-builder` - deps: flexmark-util-misc, flexmark-util-data
9. `flexmark-util-dependency` - deps: flexmark-util-collection, flexmark-util-misc, flexmark-util-data
10. `flexmark-util-ast` - deps: flexmark-util-collection, flexmark-util-misc, flexmark-util-data, flexmark-util-sequence, flexmark-util-visitor
11. `flexmark-util-format` - deps: flexmark-util-ast, flexmark-util-collection, flexmark-util-data, flexmark-util-html, flexmark-util-misc, flexmark-util-sequence
12. `flexmark-util` - aggregate module, deps on all above

#### Core Module (1 module)
13. `flexmark` - deps: flexmark-util-ast, flexmark-util-builder, flexmark-util-collection, flexmark-util-data, flexmark-util-dependency, flexmark-util-format, flexmark-util-html, flexmark-util-misc, flexmark-util-sequence, flexmark-util-visitor

#### Test Infrastructure (3 modules)
14. `flexmark-test-util` - deps: flexmark-util-misc, flexmark-util-data, flexmark-util-ast, flexmark-util-format, flexmark-util-sequence
15. `flexmark-test-specs` - deps: flexmark-test-util
16. `flexmark-core-test` - deps: flexmark, flexmark-util, flexmark-test-util, flexmark-test-specs

#### Extensions (4 modules)
17. `flexmark-ext-tables` - deps: flexmark-util, flexmark
18. `flexmark-ext-footnotes` - deps: flexmark-util, flexmark
19. `flexmark-ext-yaml-front-matter` - deps: flexmark-util, flexmark

**ISSUE IDENTIFIED**: The original plan says 20 modules (17 production + 3 test). By my count:
- 12 utility modules
- 1 core module (flexmark)
- 3 test modules
- 3 extension modules

That's 19 modules. The plan mentioned `flexmark-util-options` is in the settings.gradle.kts example but I've included it above. That makes 19 modules.

#QUESTION_FOR_HUMAN: The high-level plan mentions "20 modules (17 production + 3 test)" but my analysis shows 19 modules (16 production + 3 test). Should we keep exactly these 19, or is there another module that should be kept?

### Modules to REMOVE (44 total)

As listed in the high-level plan:
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
flexmark-jira-converter
flexmark-osgi
flexmark-pdf-converter
flexmark-profile-pegdown
flexmark-tree-iteration
flexmark-util-experimental
flexmark-youtrack-converter
```

**Additional directories to remove** (not in pom.xml but exist on filesystem):
```
flexmark-formatter-test-suite
flexmark-java-samples
flexmark-test-suite
```

---

## Phase 0: Module Removal - Detailed Steps

### Step 0.1: Handle flexmark-ext-tables Test Dependency

**Problem**: `flexmark-ext-tables` has a test dependency on `flexmark-ext-typographic` (which is being removed).

**Impact Analysis**:
- There is exactly **1 test case** using the typographic option: `DoNotDecorate: 2` in `/flexmark-ext-tables/src/test/resources/ext_tables_ast_spec.md` (line 3611)
- The test option is defined in `ComboTableSpecTest.java` line 36

**Resolution Strategy**:
1. Remove the `typographic` option from `ComboTableSpecTest.java`
2. Remove the import of `TypographicExtension`
3. Remove the test case `DoNotDecorate: 2` from `ext_tables_ast_spec.md`
4. Remove the `flexmark-ext-typographic` test dependency from `flexmark-ext-tables/pom.xml`

**Files to modify**:
- `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-tables/src/test/java/com/vladsch/flexmark/ext/tables/ComboTableSpecTest.java`
- `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-tables/src/test/resources/ext_tables_ast_spec.md`
- `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-tables/pom.xml`

### Step 0.2: Update Root pom.xml

Remove all 44 modules from the `<modules>` section, keeping only:
```xml
<modules>
    <module>flexmark-util-misc</module>
    <module>flexmark-util-visitor</module>
    <module>flexmark-util-data</module>
    <module>flexmark-util-collection</module>
    <module>flexmark-util-sequence</module>
    <module>flexmark-util-html</module>
    <module>flexmark-util-options</module>
    <module>flexmark-util-builder</module>
    <module>flexmark-util-dependency</module>
    <module>flexmark-util-ast</module>
    <module>flexmark-util-format</module>
    <module>flexmark-util</module>
    <module>flexmark</module>
    <module>flexmark-test-util</module>
    <module>flexmark-test-specs</module>
    <module>flexmark-core-test</module>
    <module>flexmark-ext-tables</module>
    <module>flexmark-ext-footnotes</module>
    <module>flexmark-ext-yaml-front-matter</module>
</modules>
```

### Step 0.3: Update Root pom.xml dependencyManagement

Remove all 44 dependencies from `<dependencyManagement>` that correspond to removed modules.

Keep only dependencies for:
- All `flexmark-util-*` modules
- `flexmark`
- `flexmark-test-util`
- `flexmark-test-specs`
- `flexmark-core-test`
- `flexmark-ext-tables`
- `flexmark-ext-footnotes`
- `flexmark-ext-yaml-front-matter`
- External deps: `junit:junit`, `org.openjdk.jmh:*`

### Step 0.4: Delete Module Directories

Delete the following 44 directories (+ 3 extra directories not in pom.xml):

```bash
# Modules in pom.xml to remove
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-all
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-docx-converter
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-abbreviation
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-admonition
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-anchorlink
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-aside
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-attributes
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-autolink
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-definition
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-emoji
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-enumerated-reference
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-escaped-character
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-gfm-issues
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-gfm-strikethrough
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-gfm-tasklist
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-gfm-users
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-gitlab
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-ins
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-jekyll-front-matter
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-jekyll-tag
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-macros
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-media-tags
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-resizable-image
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-spec-example
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-superscript
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-toc
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-typographic
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-wikilink
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-xwiki-macros
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-youtube-embedded
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-ext-zzzzzz
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-html2md-converter
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-integration-test
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-jira-converter
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-osgi
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-pdf-converter
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-profile-pegdown
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-tree-iteration
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-util-experimental
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-youtrack-converter

# Extra directories not in pom.xml
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-formatter-test-suite
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-java-samples
rm -rf /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/flexmark-test-suite
```

### Step 0.5: Verification

```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify module count
ls -d flexmark*/ | wc -l
# Expected: 19 directories

# Verify build compiles
mvn clean compile -DskipTests 2>&1 | tee .tmp/phase0_compile.log
grep "BUILD SUCCESS" .tmp/phase0_compile.log

# Verify tests pass
mvn test -Dsurefire.useFile=false 2>&1 | tee .tmp/phase0_test.log
grep "BUILD SUCCESS" .tmp/phase0_test.log
```

---

## Phase 1: Maven to Gradle Conversion - Detailed Steps

### Step 1.1: Initialize Gradle Wrapper

```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin
gradle wrapper --gradle-version 8.5
```

This creates:
- `gradlew` (Unix wrapper script)
- `gradlew.bat` (Windows wrapper script)
- `gradle/wrapper/gradle-wrapper.jar`
- `gradle/wrapper/gradle-wrapper.properties`

### Step 1.2: Create settings.gradle.kts

**File**: `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/settings.gradle.kts`

```kotlin
rootProject.name = "flexmark-kotlin"

// Utility modules (in dependency order)
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

// Test infrastructure
include("flexmark-test-util")
include("flexmark-test-specs")
include("flexmark-core-test")

// Extensions
include("flexmark-ext-tables")
include("flexmark-ext-footnotes")
include("flexmark-ext-yaml-front-matter")
```

### Step 1.3: Create Root build.gradle.kts

**File**: `/home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin/build.gradle.kts`

```kotlin
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

    tasks.withType<JavaCompile> {
        options.encoding = "UTF-8"
    }

    dependencies {
        testImplementation("junit:junit:4.13.2")
    }
}
```

### Step 1.4: Create Module build.gradle.kts Files

Each module needs its own `build.gradle.kts`. Here are all 19 modules:

---

#### 1. flexmark-util-misc/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 2. flexmark-util-visitor/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 3. flexmark-util-data/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 4. flexmark-util-collection/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 5. flexmark-util-sequence/build.gradle.kts
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

---

#### 6. flexmark-util-html/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-sequence"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 7. flexmark-util-options/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-sequence"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 8. flexmark-util-builder/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 9. flexmark-util-dependency/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-collection"))
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 10. flexmark-util-ast/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-collection"))
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    api(project(":flexmark-util-sequence"))
    api(project(":flexmark-util-visitor"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 11. flexmark-util-format/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-ast"))
    api(project(":flexmark-util-collection"))
    api(project(":flexmark-util-data"))
    api(project(":flexmark-util-html"))
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-sequence"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 12. flexmark-util/build.gradle.kts
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
    api(project(":flexmark-util-options"))
    api(project(":flexmark-util-sequence"))
    api(project(":flexmark-util-visitor"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 13. flexmark/build.gradle.kts
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
    testImplementation("org.openjdk.jmh:jmh-core:1.13")
    testImplementation("org.openjdk.jmh:jmh-generator-annprocess:1.13")
    testImplementation("org.apache.logging.log4j:log4j-api:2.20.0")
    testImplementation("org.apache.logging.log4j:log4j-core:2.20.0")
    testImplementation("org.apache.logging.log4j:log4j-1.2-api:2.20.0")
}
```

---

#### 14. flexmark-test-util/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    api(project(":flexmark-util-ast"))
    api(project(":flexmark-util-format"))
    api(project(":flexmark-util-sequence"))
    api("junit:junit:4.13.2")
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 15. flexmark-test-specs/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-test-util"))
    implementation("org.jetbrains:annotations:24.0.1")
}
```

---

#### 16. flexmark-core-test/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark"))
    api(project(":flexmark-util"))
    api(project(":flexmark-test-util"))
    api(project(":flexmark-test-specs"))

    testImplementation("org.openjdk.jmh:jmh-core:1.13")
    testImplementation("org.openjdk.jmh:jmh-generator-annprocess:1.13")
}
```

---

#### 17. flexmark-ext-tables/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util"))
    api(project(":flexmark"))

    testImplementation(project(":flexmark-test-util"))
    testImplementation(project(":flexmark-core-test"))
}
```

---

#### 18. flexmark-ext-footnotes/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util"))
    api(project(":flexmark"))

    testImplementation(project(":flexmark-test-util"))
    testImplementation(project(":flexmark-ext-tables"))
    testImplementation(project(":flexmark-core-test"))
}
```

---

#### 19. flexmark-ext-yaml-front-matter/build.gradle.kts
```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util"))
    api(project(":flexmark"))

    testImplementation(project(":flexmark-test-util"))
    testImplementation(project(":flexmark-core-test"))
}
```

---

### Step 1.5: Remove Maven Files

After Gradle verification succeeds, remove Maven artifacts:

```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Remove all pom.xml files
find . -name "pom.xml" -delete

# Remove .mvn directory if exists
rm -rf .mvn
```

### Step 1.6: Verification

```bash
cd /home/nickolaykondratyev/git_repos/nickolay-kondratyev_flexmark-kotlin

# Verify Gradle build compiles
./gradlew clean build -x test 2>&1 | tee .tmp/phase1_compile.log
grep "BUILD SUCCESSFUL" .tmp/phase1_compile.log

# Verify tests pass
./gradlew test 2>&1 | tee .tmp/phase1_test.log
grep "BUILD SUCCESSFUL" .tmp/phase1_test.log

# List all projects
./gradlew projects
```

---

## Implementation Order

### Phase 0 Execution Order:
1. Modify `flexmark-ext-tables/src/test/java/com/vladsch/flexmark/ext/tables/ComboTableSpecTest.java`
2. Modify `flexmark-ext-tables/src/test/resources/ext_tables_ast_spec.md`
3. Modify `flexmark-ext-tables/pom.xml`
4. Modify root `pom.xml` (modules section)
5. Modify root `pom.xml` (dependencyManagement section)
6. Delete 47 module directories
7. Run verification

### Phase 1 Execution Order:
1. Run `gradle wrapper --gradle-version 8.5`
2. Create `settings.gradle.kts`
3. Create root `build.gradle.kts`
4. Create module `build.gradle.kts` files (in dependency order):
   - Base modules first: flexmark-util-misc, flexmark-util-visitor
   - Then dependent modules working up the dependency tree
5. Run Gradle build verification
6. Delete Maven files (pom.xml)
7. Run final verification

---

## Testing Strategy

### Phase 0 Testing:
- Compile all remaining modules: `mvn clean compile -DskipTests`
- Run all tests: `mvn test -Dsurefire.useFile=false`
- Expected: All tests pass except any that were removed with typographic dependency

### Phase 1 Testing:
- Compile with Gradle: `./gradlew clean build -x test`
- Run tests with Gradle: `./gradlew test`
- Expected: All tests pass

---

## Risks & Mitigations

### Risk 1: Hidden Dependencies
**Risk**: Modules may have implicit dependencies not captured in pom.xml.
**Mitigation**: Compile first, then run tests. If compilation fails, analyze error and add missing dependency.

### Risk 2: Typographic Test Removal Breaks Other Tests
**Risk**: Removing the typographic test case may have dependencies in other test files.
**Mitigation**: Search for any references to "DoNotDecorate: 2" before removing. Already searched - no additional references found.

### Risk 3: Gradle Dependency Resolution Differences
**Risk**: Gradle may resolve transitive dependencies differently than Maven.
**Mitigation**: Use `api()` for dependencies that should be transitively exposed, `implementation()` for internal dependencies.

### Risk 4: Test Resource Loading
**Risk**: Test resources may be loaded differently in Gradle.
**Mitigation**: Ensure test resources are in `src/test/resources` directory. The existing structure already follows this convention.

---

## Open Questions

#QUESTION_FOR_HUMAN: The high-level plan mentions keeping "20 modules (17 production + 3 test)" but my analysis shows 19 modules. Is there a module I'm missing, or should the plan be updated to 19?

---

## Script Location

The high-level plan mentions creating Python scripts at:
- `kotlin-conversion/scripts/migrate/phase_0_remove/remove_modules.py`
- `kotlin-conversion/scripts/migrate/phase_1_gradle/convert_to_gradle.py`

Given the simplicity of the operations (mostly file deletions and creations), the IMPLEMENTOR can choose to:
1. Create these scripts for repeatability
2. Execute the changes directly using shell commands

**Recommendation**: For Phase 0, direct shell commands are simpler. For Phase 1, creating template files and copying them is straightforward enough that a script may be overkill.
