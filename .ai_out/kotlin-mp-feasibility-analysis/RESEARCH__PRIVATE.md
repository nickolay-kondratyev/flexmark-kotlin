# Research Notes - Kotlin MP Feasibility Analysis (Private)

## Raw Data Collection

### Codebase Statistics

- **Total Java files**: 1,416
- **Total modules**: 60+
- **Java version**: 11+ (was Java 8+ until 0.62.2)

### Java Import Analysis (grep counts)

```
java.awt imports: 18 occurrences across 11 files
java.io imports: 100 occurrences across 51 files
java.nio imports: 16 occurrences across 13 files
java.util.regex imports: 101 occurrences across 65 files
java.lang.reflect imports: 3 occurrences across 3 files
ThreadLocal usage: 6 occurrences across 2 files
synchronized usage: 12 occurrences across 7 files
Pattern.compile/matches/quote: 157 occurrences across 52 files
```

### Key Files Examined

1. `/pom.xml` - Root POM with 60+ modules
2. `/flexmark/pom.xml` - Core module (no external deps!)
3. `/flexmark-docx-converter/pom.xml` - docx4j, commons-io, xmlgraphics
4. `/flexmark-html2md-converter/pom.xml` - jsoup only
5. `/flexmark-pdf-converter/pom.xml` - openhtmltopdf, jsoup, icu4j
6. `/flexmark-ext-autolink/pom.xml` - org.nibor.autolink
7. `/flexmark-profile-pegdown/pom.xml` - pegdown (test only)

### External Dependencies Summary

**Runtime dependencies that block KMP:**
- docx4j-JAXB-ReferenceImpl (11.4.9) - DOCX module
- openhtmltopdf-* (1.0.10) - PDF module
- xmlgraphics-commons (2.7) - DOCX module
- commons-io (2.11.0) - DOCX module
- jsoup (1.15.4) - html2md and pdf modules
- org.nibor.autolink (0.6.0) - ext-autolink
- icu4j (72.1) - PDF module (RTL support)

**Test-only dependencies (don't block):**
- junit (4.13.2)
- jmh-core (1.13)
- pegdown (1.6.0)
- log4j-* (2.20.0)

### Regex Patterns Analysis

The `Parsing.java` file (flexmark/src/main/java/com/vladsch/flexmark/ast/util/Parsing.java) contains 35+ statically compiled Pattern objects. These are fundamental to the parsing pipeline.

Key patterns include:
- Link labels, destinations, titles
- Punctuation detection
- HTML comment parsing
- Escaped characters

Most use standard regex features, but some use Unicode categories like `\p{Pc}` (Connector Punctuation).

### Web Search Findings

#### Kotlin-MP General Blockers
1. No java.io.File - use kotlinx-io
2. No java.util.concurrent.atomic - use atomicfu
3. No synchronized - use atomicfu.locks
4. No ThreadLocal - use CoroutineContext or @ThreadLocal annotation
5. No JUnit - use kotlin.test

#### Regex in Kotlin-MP
- `kotlin.text.Regex` is multiplatform
- On JVM, it wraps `java.util.regex.Pattern`
- On JS/Native, it uses platform-native regex
- Most features work, but some Matcher methods missing (hitEnd, region)

#### jsoup Alternatives
- fleeksoft/ksoup - Full port, nearly API-compatible
- MohamedRejeb/Ksoup - Lightweight alternative, different API

#### docx4j Alternatives
- None found for KMP
- DocxKtm exists but wraps docx4j (still JVM-only)

### Module Categorization Logic

**Tier 1 criteria**: No external deps, only standard Java APIs that have KMP equivalents
**Tier 2 criteria**: External deps have KMP alternatives
**Tier 3 criteria**: External deps have NO KMP alternatives OR fundamentally JVM-only

### Risk Assessment

**Low Risk**:
- util modules (pure data structures)
- simple extensions (no I/O, just parsing)

**Medium Risk**:
- Core parser (regex-heavy)
- html2md-converter (jsoup migration)

**High Risk**:
- ext-autolink (need to reimplement or port dependency)
- Any module with java.awt usage

**Not Feasible**:
- DOCX converter (docx4j is massive, deeply JVM)
- PDF converter (needs native PDF libraries)

### Notes for Follow-up

1. Need to verify kotlin.text.Regex supports all Unicode categories used in Parsing.java
2. Ksoup compatibility should be tested with actual html2md-converter usage
3. BasedSequence abstraction is sophisticated - may need careful porting
4. Extension loading mechanism uses Java ServiceLoader pattern - needs KMP alternative

### Alternative Libraries Considered

**JetBrains markdown** (https://github.com/JetBrains/markdown):
- Already Kotlin Multiplatform
- CommonMark compliant
- Different API than flexmark
- Fewer extensions
- Used by IntelliJ products

**CommonMarK** (https://github.com/matt-belisle/CommonMarK):
- Kotlin implementation
- Claims similar performance to flexmark
- Appears less maintained

### Decision Factors

For vs Against KMP conversion:

**For:**
- Enable Web/JS usage of flexmark
- Single codebase maintenance
- Kotlin ecosystem alignment

**Against:**
- Massive effort (1400+ files)
- Some modules impossible (DOCX/PDF)
- Risk of subtle behavior differences (regex edge cases)
- Alternative exists (JetBrains markdown)

### Conversation Notes

- Initial scope: feasibility analysis
- User context: evaluating whether to convert flexmark-java to Kotlin-MP
- Key deliverable: Which modules can be converted, which cannot
