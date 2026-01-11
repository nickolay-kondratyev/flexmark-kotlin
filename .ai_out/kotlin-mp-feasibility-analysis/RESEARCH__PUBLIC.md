# Kotlin Multiplatform Feasibility Analysis for flexmark-java

**Date**: 2026-01-11
**Subject**: Converting flexmark-java to Kotlin Multiplatform with Web/JS target support

---

## Summary

- **Core parser and most extensions are FEASIBLE** for Kotlin-MP conversion with moderate effort; the main blockers are `java.util.regex.Pattern/Matcher` (157+ usages) which require migration to `kotlin.text.Regex`
- **Converter modules (DOCX, PDF) are NOT FEASIBLE** for Web/JS target due to hard dependencies on JVM-only libraries (docx4j, openhtmltopdf, JAXB)
- **HTML-to-Markdown converter has a viable path** using Ksoup (multiplatform jsoup port) as a replacement for jsoup
- **External dependencies block 3 modules**: autolink (org.nibor.autolink), html2md-converter (jsoup), docx/pdf converters
- **Java I/O usage is limited** and primarily in test utilities; can be abstracted via kotlinx-io or expect/actual pattern

---

## Research Questions

1. What Java APIs used in flexmark-java lack Kotlin-MP equivalents?
2. Which external dependencies block conversion?
3. What patterns (reflection, synchronization, ThreadLocal) are problematic?
4. Which modules are feasible to convert vs. must be excluded?

---

## Findings

### 1. Java API Usage Analysis

Based on codebase analysis of 1,416 Java files across 60+ modules:

| Java API | Usage Count | Files Affected | Impact |
|----------|-------------|----------------|--------|
| `java.util.regex.Pattern/Matcher` | 157+ Pattern.compile calls | 65 files | **HIGH** - Core to parsing |
| `java.io.*` | 100+ imports | 51 files | **MEDIUM** - Mostly test utils |
| `java.nio.*` | 16 imports | 13 files | **LOW** - Limited to file utilities |
| `java.awt.*` (Font, Color) | 18 imports | 11 files | **LOW** - Only in DOCX/UI modules |
| `java.lang.reflect.*` | 3 imports | 3 files | **LOW** - Minimal reflection |
| `synchronized` blocks | 12 occurrences | 7 files | **LOW** - Minimal concurrency |
| `ThreadLocal` | 6 occurrences | 2 files | **LOW** - Sample code + sequence tree |

### 2. External Dependencies Impact

| Dependency | Module(s) | KMP Alternative | Conversion Feasibility |
|------------|-----------|-----------------|------------------------|
| **jsoup** (1.15.4) | html2md-converter, pdf-converter | [Ksoup (fleeksoft)](https://github.com/fleeksoft/ksoup) - full port | **POSSIBLE** - API compatible |
| **docx4j** (11.4.9) | docx-converter | None | **NOT POSSIBLE** - JVM-only |
| **openhtmltopdf** (1.0.10) | pdf-converter | None | **NOT POSSIBLE** - JVM-only |
| **org.nibor.autolink** (0.6.0) | ext-autolink | None / Manual impl | **POSSIBLE** - Simple algo |
| **pegdown** (1.6.0) | profile-pegdown (test only) | N/A | **N/A** - Test scope only |
| **JMH** (1.13) | flexmark (test only) | N/A | **N/A** - Test scope only |
| **log4j** (2.20.0) | various (test only) | N/A | **N/A** - Test scope only |
| **commons-io** (2.11.0) | docx-converter | kotlinx-io | **POSSIBLE** - If module converted |

### 3. Pattern Blockers

#### 3.1 Regex Usage (Critical)

The parser relies heavily on `java.util.regex.Pattern` and `Matcher`. Key facts:

- **35+ compiled patterns** in `Parsing.java` alone
- Heavy use of advanced regex features: Unicode categories (`\p{Pc}`, `\p{Pd}`), named groups
- `kotlin.text.Regex` is available in Kotlin-MP and wraps native regex on each platform

**Migration Path**:
- `kotlin.text.Regex` supports most features needed
- Some Matcher-specific methods (`hitEnd()`, `lookingAt()`) need workarounds
- Pattern compilation is similar: `Regex(pattern)` vs `Pattern.compile(pattern)`

#### 3.2 File I/O Usage

Primary uses:
- **Test utilities**: Resource loading, spec file reading
- **FileUriContentResolver**: HTML renderer file resolution
- **ImageUtils**: Image loading (DOCX module)

**Migration Path**:
- Use [kotlinx-io](https://github.com/Kotlin/kotlinx-io) for cross-platform file operations
- Test utilities can use platform-specific expect/actual declarations
- Web/JS target typically doesn't need file system access

#### 3.3 Synchronization

Minimal usage found:
- `synchronized` in emoji loading
- One experimental sequence manager

**Migration Path**:
- Use [kotlinx-atomicfu](https://github.com/Kotlin/kotlinx-atomicfu) for locks
- Or kotlinx.coroutines `Mutex` for suspending contexts

---

## Approaches Comparison Table

| Approach | Description | Pros | Cons | Complexity | Best For |
|----------|-------------|------|------|------------|----------|
| **Full KMP Conversion** | Convert all modules to Kotlin-MP | Complete multiplatform support, single codebase | Massive effort (1400+ files), converter modules impossible | **Very High** | Not recommended |
| **Core-Only KMP** | Convert core parser + extensions, exclude converters | 80% of value, avoids impossible modules, proven path | Loses DOCX/PDF support on Web | **High** | Large-scale KMP projects |
| **Targeted KMP (Recommended)** | Convert only: flexmark-util-*, flexmark core, select extensions | Minimal blocker surface, achievable, Web-viable | May need API abstraction layer | **Medium** | Web/JS markdown parsing |
| **JVM + JS Wrapper** | Keep Java, create JS wrapper via Dukat or manual | Preserves existing codebase, quicker | Not true multiplatform, maintenance burden | **Medium** | Existing JVM projects needing quick JS support |
| **Alternative Library** | Use [JetBrains markdown](https://github.com/JetBrains/markdown) | Already multiplatform, CommonMark compliant | Different API, fewer extensions | **Low** | New projects, simpler needs |

---

## Java APIs - Kotlin-MP Compatibility Table

| Java API | Kotlin-MP Support | Web/JS Support | Suggested Alternative | Notes |
|----------|-------------------|----------------|----------------------|-------|
| `java.util.regex.Pattern` | Partial | Yes | `kotlin.text.Regex` | Core Kotlin stdlib, works on all targets |
| `java.util.regex.Matcher` | Partial | Yes | `MatchResult`, `Sequence<MatchResult>` | Some methods (hitEnd) unavailable |
| `java.io.File` | None | No | `kotlinx.io.files.Path` | Or expect/actual for platform-specific |
| `java.io.InputStream` | None | Partial | `kotlinx.io.Source` | Web may use fetch/ArrayBuffer |
| `java.io.Reader/Writer` | None | Partial | `kotlinx.io` streams | String-based alternatives for Web |
| `java.nio.charset.Charset` | None | Yes | Platform encoding | JS uses UTF-16 natively |
| `java.awt.Font` | None | No | CSS font descriptors (Web) | Platform-specific styling |
| `java.awt.Color` | None | Partial | Custom data class / CSS colors | Simple RGB class works |
| `java.lang.reflect.Array` | None | No | `Array<T>` generics | Avoid reflection patterns |
| `synchronized` | None | N/A (single-threaded) | `kotlinx.atomicfu.locks` | JS is single-threaded anyway |
| `ThreadLocal` | None | N/A (single-threaded) | CoroutineContext or direct | Not needed for JS target |
| `System.currentTimeMillis()` | None | Yes | `Clock.System.now()` (kotlinx-datetime) | Or platform expect/actual |

---

## Library Blockers

### Completely Blocking (No KMP Alternative)

| Library | Used In | Functionality | Assessment |
|---------|---------|---------------|------------|
| **docx4j** | flexmark-docx-converter | DOCX generation via JAXB | No multiplatform alternative exists. DOCX format requires complex XML/ZIP handling. Module must be JVM-only. |
| **openhtmltopdf** | flexmark-pdf-converter | HTML to PDF rendering | Requires JVM for PDF generation (PDFBox, iText). Module must be JVM-only. |
| **xmlgraphics-commons** | flexmark-docx-converter | XML/graphics utilities | Apache library, JVM-only. |

### Replaceable (KMP Alternatives Exist)

| Library | Used In | KMP Alternative | Migration Effort |
|---------|---------|-----------------|------------------|
| **jsoup** | html2md-converter | [Ksoup](https://github.com/fleeksoft/ksoup) | Medium - API is nearly identical |
| **org.nibor.autolink** | ext-autolink | Custom implementation or port | Low-Medium - Algorithm is documented |
| **commons-io** | docx-converter | kotlinx-io | Low - Basic file utilities |

---

## Module-Level Assessment

### Tier 1: Fully Convertible (No External Blockers)

| Module | External Deps | Blocking APIs | Feasibility |
|--------|---------------|---------------|-------------|
| flexmark-util-ast | None | None | **FEASIBLE** |
| flexmark-util-builder | None | None | **FEASIBLE** |
| flexmark-util-collection | None | None | **FEASIBLE** |
| flexmark-util-data | None | None | **FEASIBLE** |
| flexmark-util-dependency | None | None | **FEASIBLE** |
| flexmark-util-format | None | Regex | **FEASIBLE** |
| flexmark-util-html | None | java.awt.Color/Font | **FEASIBLE** (abstract styling) |
| flexmark-util-misc | None | java.awt.Color, ImageUtils | **PARTIAL** (exclude ImageUtils) |
| flexmark-util-sequence | None | Regex, java.nio.charset | **FEASIBLE** |
| flexmark-util-visitor | None | None | **FEASIBLE** |
| flexmark-util-options | None | None | **FEASIBLE** |
| flexmark (core) | None | Regex, java.io | **FEASIBLE** |

### Tier 2: Convertible with Dependency Replacement

| Module | External Deps | Replacement | Feasibility |
|--------|---------------|-------------|-------------|
| flexmark-ext-abbreviation | None | - | **FEASIBLE** |
| flexmark-ext-admonition | None | - | **FEASIBLE** |
| flexmark-ext-anchorlink | None | - | **FEASIBLE** |
| flexmark-ext-aside | None | - | **FEASIBLE** |
| flexmark-ext-attributes | None | - | **FEASIBLE** |
| flexmark-ext-autolink | org.nibor.autolink | Custom impl | **FEASIBLE** (med effort) |
| flexmark-ext-definition | None | - | **FEASIBLE** |
| flexmark-ext-emoji | None | - | **FEASIBLE** |
| flexmark-ext-footnotes | None | - | **FEASIBLE** |
| flexmark-ext-gfm-* | None | - | **FEASIBLE** |
| flexmark-ext-tables | None | - | **FEASIBLE** |
| flexmark-ext-toc | None | - | **FEASIBLE** |
| flexmark-ext-wikilink | None | - | **FEASIBLE** |
| flexmark-ext-yaml-front-matter | None | - | **FEASIBLE** |
| flexmark-html2md-converter | jsoup | Ksoup | **FEASIBLE** (med effort) |

### Tier 3: JVM-Only (Cannot Convert for Web/JS)

| Module | Blocking Dependency | Reason |
|--------|---------------------|--------|
| **flexmark-docx-converter** | docx4j, xmlgraphics | DOCX format requires JAXB, complex XML |
| **flexmark-pdf-converter** | openhtmltopdf, jsoup | PDF generation needs native libraries |
| **flexmark-osgi** | OSGi framework | JVM deployment model |
| **flexmark-test-util** | JUnit, java.io | Test framework, could create KMP version |

---

## Open Questions

1. **Regex Unicode Categories**: Does `kotlin.text.Regex` support `\p{Pc}`, `\p{Pd}` on JS target? May need testing or polyfills.

2. **Performance on JS**: Flexmark's design prioritizes performance. Need to validate JS target performance is acceptable.

3. **Character Sequence Abstraction**: Flexmark has sophisticated `BasedSequence` classes. Need to verify these translate well to Kotlin-MP.

4. **Extension Loading**: Current extension system uses service loader pattern. May need rethinking for KMP.

5. **Ksoup Maturity**: Is fleeksoft/ksoup production-ready? Has 300+ GitHub stars, actively maintained, but verify compatibility with flexmark's jsoup usage patterns.

---

## Recommendations

### Recommended Approach: Targeted KMP Conversion

**Scope**: Convert the following modules to Kotlin Multiplatform:

1. **Phase 1 - Utilities** (Foundation)
   - `flexmark-util-ast`
   - `flexmark-util-builder`
   - `flexmark-util-collection`
   - `flexmark-util-data`
   - `flexmark-util-dependency`
   - `flexmark-util-format`
   - `flexmark-util-html` (abstract away AWT types)
   - `flexmark-util-misc` (exclude ImageUtils)
   - `flexmark-util-sequence`
   - `flexmark-util-visitor`
   - `flexmark-util-options`

2. **Phase 2 - Core Parser**
   - `flexmark` core module
   - Migrate all `Pattern`/`Matcher` to `kotlin.text.Regex`

3. **Phase 3 - Popular Extensions**
   - Tables, GFM-strikethrough, GFM-tasklist
   - Footnotes, TOC, YAML front matter
   - Emoji (may need asset loading strategy for Web)

4. **Phase 4 - Additional Converters**
   - `flexmark-html2md-converter` (with Ksoup)
   - `flexmark-jira-converter`, `flexmark-youtrack-converter`

### Modules to Exclude from KMP

- `flexmark-docx-converter` - Keep JVM-only
- `flexmark-pdf-converter` - Keep JVM-only
- `flexmark-osgi` - Keep JVM-only
- `flexmark-profile-pegdown` - Compatibility layer, JVM-only is fine

### Alternative Consideration

If the conversion effort seems too high, consider using **JetBrains markdown** library which is already:
- Written in pure Kotlin
- Multiplatform (JVM, JS, Native)
- CommonMark compliant
- Used by IntelliJ IDEs

However, this would mean losing flexmark's extensive extension ecosystem and specific AST capabilities.

---

## Sources

- [Kotlin Multiplatform Compatibility Guide](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html)
- [Kotlin Multiplatform Development Roadmap 2025](https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/)
- [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/)
- [Kotlin Multiplatform Supported Platforms](https://www.jetbrains.com/help/kotlin-multiplatform-dev/supported-platforms.html)
- [Migrating Applications to Kotlin Multiplatform Guide](https://proandroiddev.com/migrating-applications-to-kotlin-multiplatform-a-step-by-step-guide-47b365634924)
- [Kotlin Multiplatform Scalability Challenges](https://proandroiddev.com/kotlin-multiplatform-scalability-challenges-on-a-large-project-b3140e12da9d)
- [kotlinx-io GitHub](https://github.com/Kotlin/kotlinx-io)
- [kotlinx-atomicfu GitHub](https://github.com/Kotlin/kotlinx-atomicfu)
- [Ksoup (fleeksoft) - jsoup port](https://github.com/fleeksoft/ksoup)
- [JetBrains markdown library](https://github.com/JetBrains/markdown)
- [Stately - Kotlin Multiplatform State Library](https://github.com/touchlab/Stately)
- [kotlin.text.Regex API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.text/-regex/)
- [Baeldung - Regular Expressions in Kotlin](https://www.baeldung.com/kotlin/regular-expressions)
