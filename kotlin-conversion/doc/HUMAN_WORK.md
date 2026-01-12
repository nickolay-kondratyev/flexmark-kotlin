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
