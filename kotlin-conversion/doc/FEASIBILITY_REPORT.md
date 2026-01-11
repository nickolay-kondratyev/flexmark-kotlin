# Kotlin Multiplatform Conversion Feasibility Report

**Project**: flexmark-java
**Date**: 2026-01-11
**Target**: Kotlin Multiplatform with Web/JS support

---

## thorgCore Use Case Assessment

**VERDICT: HIGHLY FEASIBLE**

Your project uses only modules that are fully convertible to Kotlin-MP:

| Library | Tier | Regex Usages | Blocking Deps | Status |
|---------|------|--------------|---------------|--------|
| `flexmark` | 2 | 135 | None | CONVERTIBLE |
| `flexmark-util-ast` | 1 | 0 | None | CONVERTIBLE |
| `flexmark-util` | 1 | 8 | None | CONVERTIBLE |
| `flexmark-ext-yaml-front-matter` | 2 | 14 | None | CONVERTIBLE |
| `flexmark-ext-tables` | 2 | 4 | None | CONVERTIBLE |
| `flexmark-ext-footnotes` | 2 | 6 | None | CONVERTIBLE |

### thorgCore-Specific Metrics

| Metric | Full Project | thorgCore Subset |
|--------|--------------|------------------|
| Modules needed | 61 | ~15 (with transitive) |
| Regex migrations | 425 | **~167** |
| Blocking deps | 4 | **0** |
| Feasibility | 82% | **100%** |

### Recommended Conversion for thorgCore

Since you don't use DOCX/PDF/HTML-to-MD converters, your conversion path is straightforward:

1. **Phase 1**: flexmark-util-* modules (foundation)
2. **Phase 2**: `flexmark` core (135 regex migrations - main effort)
3. **Phase 3**: Your 3 extensions (24 regex migrations total)
   - flexmark-ext-yaml-front-matter
   - flexmark-ext-tables
   - flexmark-ext-footnotes

**No external dependency blockers affect your usage.**

---

## Executive Summary

**Conversion to Kotlin Multiplatform is FEASIBLE** for the core parser and most extensions. Approximately **82% of modules** (50 of 61) can be converted. The primary effort involves migrating 425 `Pattern`/`Matcher` usages to `kotlin.text.Regex`. Converter modules (DOCX, PDF) must remain JVM-only due to hard dependencies on JVM-specific libraries.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Java files | 1,416 |
| Total modules | 61 |
| Convertible modules | 50 (82%) |
| JVM-only modules | 11 (18%) |
| Pattern/Matcher usages | 425 |
| Blocking external deps | 4 |
| Replaceable external deps | 3 |

---

## Module Tiers

### Tier 1: Fully Convertible (13 modules)
No external dependency blockers, minimal API migration needed.

| Module | Regex Usages | Notes |
|--------|--------------|-------|
| flexmark-util-ast | 0 | Ready for conversion |
| flexmark-util-builder | 0 | Ready for conversion |
| flexmark-util-collection | 0 | Ready for conversion |
| flexmark-util-data | 0 | Ready for conversion |
| flexmark-util-dependency | 0 | Ready for conversion |
| flexmark-util-format | 5 | Regex migration needed |
| flexmark-util-html | 5 | Regex migration, abstract away AWT types |
| flexmark-util-misc | 7 | Regex migration needed |
| flexmark-util-options | 0 | Ready for conversion |
| flexmark-util-sequence | 32 | Regex migration needed |
| flexmark-util-visitor | 0 | Ready for conversion |
| flexmark-util | 8 | Aggregator module |

### Tier 2: Convertible with Effort (37 modules)
Requires regex migration and/or dependency replacement.

**Core Parser**:
- `flexmark` - 135 regex usages (main parser, requires significant regex migration)

**Extensions** (all have 0-20 regex usages, no external blockers):
- flexmark-ext-abbreviation (10)
- flexmark-ext-admonition (5)
- flexmark-ext-anchorlink (0)
- flexmark-ext-aside (0)
- flexmark-ext-attributes (9)
- flexmark-ext-autolink (8) - needs `org.nibor.autolink` replacement
- flexmark-ext-definition (0)
- flexmark-ext-emoji (0)
- flexmark-ext-enumerated-reference (11)
- flexmark-ext-escaped-character (0)
- flexmark-ext-footnotes (6)
- flexmark-ext-gfm-issues (2)
- flexmark-ext-gfm-strikethrough (0)
- flexmark-ext-gfm-tasklist (0)
- flexmark-ext-gfm-users (2)
- flexmark-ext-gitlab (13)
- flexmark-ext-ins (0)
- flexmark-ext-jekyll-front-matter (9)
- flexmark-ext-jekyll-tag (9)
- flexmark-ext-macros (12)
- flexmark-ext-media-tags (0)
- flexmark-ext-resizable-image (2)
- flexmark-ext-spec-example (5)
- flexmark-ext-superscript (0)
- flexmark-ext-tables (4)
- flexmark-ext-toc (14)
- flexmark-ext-typographic (0)
- flexmark-ext-wikilink (0)
- flexmark-ext-xwiki-macros (20)
- flexmark-ext-yaml-front-matter (14)
- flexmark-ext-youtube-embedded (0)

**Converters**:
- flexmark-html2md-converter (29) - needs jsoup -> Ksoup replacement
- flexmark-jira-converter (0)
- flexmark-youtrack-converter (0)

### Tier 3: JVM-Only (11 modules)
Cannot be converted to Kotlin-MP due to hard blockers.

| Module | Blocking Reason |
|--------|-----------------|
| flexmark-docx-converter | docx4j, xmlgraphics-commons (no KMP alternatives) |
| flexmark-pdf-converter | openhtmltopdf (no KMP alternative) |
| flexmark-osgi | OSGi framework (JVM deployment model) |
| flexmark-all | Aggregator including blocked modules |
| flexmark-test-util | JUnit, heavy java.io usage |
| flexmark-core-test | Test module |
| flexmark-integration-test | Test module |
| flexmark-test-specs | Test module |
| flexmark-profile-pegdown | Legacy pegdown compatibility |
| flexmark-tree-iteration | Experimental |
| flexmark-util-experimental | Experimental |

---

## Blockers Analysis

### External Dependency Blockers

| Dependency | Used By | Status | Alternative |
|------------|---------|--------|-------------|
| org.docx4j:docx4j-JAXB-ReferenceImpl | docx-converter | BLOCKING | None |
| com.openhtmltopdf:openhtmltopdf-core | pdf-converter | BLOCKING | None |
| com.openhtmltopdf:openhtmltopdf-pdfbox | pdf-converter | BLOCKING | None |
| org.apache.xmlgraphics:xmlgraphics-commons | docx-converter | BLOCKING | None |

### Replaceable Dependencies

| Dependency | Used By | Replacement | Effort |
|------------|---------|-------------|--------|
| org.jsoup:jsoup | html2md-converter, pdf-converter | [Ksoup](https://github.com/fleeksoft/ksoup) | Medium |
| org.nibor.autolink:autolink | ext-autolink | Custom implementation | Low-Medium |
| commons-io:commons-io | docx-converter | kotlinx-io | Low |

### Java API Migration Requirements

| Java API | Usage Count | Kotlin-MP Alternative |
|----------|-------------|----------------------|
| java.util.regex.Pattern/Matcher | 425 | kotlin.text.Regex |
| java.io.* | 87 | kotlinx-io or expect/actual |
| java.awt.* | 26 | Custom abstractions |
| synchronized/ThreadLocal | 10 | kotlinx-atomicfu (or not needed for JS) |
| java.lang.reflect.* | 3 | Refactor to avoid reflection |

---

## Recommended Conversion Strategy

### Phase 1: Foundation (flexmark-util-* modules)
Convert utility modules first as they form the foundation:
1. flexmark-util-ast
2. flexmark-util-builder
3. flexmark-util-collection
4. flexmark-util-data
5. flexmark-util-dependency
6. flexmark-util-visitor
7. flexmark-util-options

Then migrate regex-using utilities:
8. flexmark-util-format
9. flexmark-util-html (abstract AWT types)
10. flexmark-util-misc
11. flexmark-util-sequence

### Phase 2: Core Parser
Convert `flexmark` core module with full Pattern/Matcher -> Regex migration.

### Phase 3: Popular Extensions
Convert high-value extensions:
- flexmark-ext-tables
- flexmark-ext-gfm-strikethrough
- flexmark-ext-gfm-tasklist
- flexmark-ext-footnotes
- flexmark-ext-yaml-front-matter
- flexmark-ext-toc

### Phase 4: Additional Extensions & Converters
- Remaining extensions
- flexmark-html2md-converter (with Ksoup)
- flexmark-jira-converter
- flexmark-youtrack-converter

### Excluded from KMP
Keep as JVM-only:
- flexmark-docx-converter
- flexmark-pdf-converter
- flexmark-osgi
- All test modules

---

## Open Questions & Risks

1. **Regex Unicode Categories**: The parser uses `\p{Pc}`, `\p{Pd}` in patterns. JS regex support for Unicode categories should be verified.

2. **Performance on JS**: Flexmark prioritizes performance. Benchmark JS target performance to validate acceptable parsing speed.

3. **BasedSequence Abstraction**: Flexmark's sophisticated sequence classes need validation that they translate well to Kotlin-MP.

4. **Extension Loading**: Current service loader pattern may need rethinking for KMP.

---

## Alternative Consideration

If conversion effort seems too high, consider [JetBrains markdown](https://github.com/JetBrains/markdown):
- Already multiplatform (JVM, JS, Native)
- CommonMark compliant
- Used by IntelliJ IDEs

Trade-off: Different API, fewer extensions than flexmark.

---

## Analysis Scripts

Analysis scripts are available in `/kotlin-conversion/scripts/`:

| Script | Purpose |
|--------|---------|
| `analyze_java_api_blockers.py` | Detect problematic Java API usage |
| `analyze_external_deps.py` | Analyze Maven dependencies per module |
| `analyze_module_feasibility.py` | Aggregate results into module tiers |
| `run_all_analysis.sh` | Run complete analysis pipeline |

### Running the Analysis

```bash
cd kotlin-conversion/scripts
./run_all_analysis.sh
```

Output files are written to `.ai_out/kotlin-mp-feasibility-analysis/`:
- `java_api_blockers.json`
- `external_deps.json`
- `module_feasibility.json`

---

## Conclusion

Converting flexmark-java to Kotlin Multiplatform with Web/JS support is **feasible** for the core functionality. The recommended "targeted conversion" approach achieves ~82% module coverage while avoiding the impossible (DOCX/PDF converters).

Primary effort: Migrating 425 `Pattern`/`Matcher` usages to `kotlin.text.Regex` across ~50 files.

The phased approach starting with utility modules minimizes risk and enables incremental validation.
