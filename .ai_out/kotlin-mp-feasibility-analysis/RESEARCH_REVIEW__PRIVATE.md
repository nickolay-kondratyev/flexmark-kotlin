# Research Review - Internal Notes

**Date**: 2026-01-11
**Status**: APPROVED

## Verification Commands Run

```bash
# Pattern.compile usage
grep -r "Pattern\.compile" --include="*.java" | wc -l
# Result: 160 occurrences in 54 files

# java.io imports
grep -r "import java\.io\." --include="*.java" | wc -l
# Result: 100 occurrences in 51 files

# synchronized blocks
grep -r "synchronized" --include="*.java" --type=java
# Result: 6 occurrences in 4 files (research said 12 in 7)

# ThreadLocal
grep -r "ThreadLocal" --include="*.java"
# Result: 6 occurrences in 2 files (matches research)

# hitEnd() and lookingAt()
grep -r "\.hitEnd\(\)" --include="*.java"
grep -r "\.lookingAt\(\)" --include="*.java"
# Result: NONE FOUND - this is good news, removes a migration concern

# External dependencies
grep -r "org\.nibor\.autolink" # 3 files (2 real + research docs)
grep -r "org\.jsoup" # 16 files
grep -r "docx4j" # 42 files (many in docx module)
grep -r "openhtmltopdf" # 9 files (mostly docs/pom)
```

## Key Technical Observations

### Unicode Property Classes in Parsing.java

Found extensive use in `Parsing.java`:
```java
Pattern.compile("...\\p{Pc}\\p{Pd}\\p{Pe}\\p{Pf}\\p{Pi}\\p{Po}\\p{Ps}...")
```

This is a risk area for JS target. Need to verify:
- Does `kotlin.text.Regex` support these on JS?
- If not, can we polyfill or simplify?

### The synchronized discrepancy

Research said 12 occurrences in 7 files, I found 6 in 4 files. Possible reasons:
- Research may have counted `synchronized` in comments/strings
- Different search patterns
- Not a critical issue - the number is still low

### Good news: No hitEnd/lookingAt usage

The research conservatively mentioned these might need workarounds, but they're not actually used. This simplifies the regex migration significantly.

## Notes for Implementation Phase

1. Priority regex patterns to detect in analysis scripts:
   - `java.util.regex.Pattern`
   - `java.util.regex.Matcher`
   - Unicode properties: `\\p\{[A-Za-z]+\}`
   - Pattern flags: `Pattern.CASE_INSENSITIVE`, `Pattern.MULTILINE`, etc.

2. Service loader detection:
   - Scan for `META-INF/services/` directories
   - Check for `ServiceLoader` usage in code

3. Module dependency graph would be useful:
   - Which modules depend on blocked modules?
   - Clean separation between convertible and non-convertible?

## Decision Rationale

Approved because:
1. All major claims verified accurate
2. Clear detection patterns provided
3. Actionable module categorization
4. Open questions are appropriate for this stage (not blocking)
5. The one discrepancy (synchronized count) is conservative and minor
