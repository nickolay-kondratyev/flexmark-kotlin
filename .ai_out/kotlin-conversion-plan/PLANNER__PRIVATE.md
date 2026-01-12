# PLANNER Private State

**Last Updated**: 2026-01-12
**Status**: COMPLETE - Initial plan created

## Context Summary

### Modules to KEEP (17 modules total)
Production code (14):
- `flexmark` - core parser (135 regex)
- `flexmark-util` - aggregator
- `flexmark-util-ast` - AST utilities (0 regex)
- `flexmark-util-builder` - builder utilities (0 regex)
- `flexmark-util-collection` - collection utilities (0 regex)
- `flexmark-util-data` - data utilities (0 regex)
- `flexmark-util-dependency` - dependency utilities (0 regex)
- `flexmark-util-format` - format utilities (5 regex)
- `flexmark-util-html` - HTML utilities (5 regex)
- `flexmark-util-misc` - misc utilities (7 regex)
- `flexmark-util-options` - options utilities (0 regex)
- `flexmark-util-sequence` - sequence utilities (32 regex)
- `flexmark-util-visitor` - visitor utilities (0 regex)
- `flexmark-ext-tables` - tables extension (4 regex)
- `flexmark-ext-footnotes` - footnotes extension (6 regex)
- `flexmark-ext-yaml-front-matter` - YAML front matter (14 regex)

Test infrastructure (3):
- `flexmark-test-util` - test utilities
- `flexmark-test-specs` - spec files
- `flexmark-core-test` - core tests

### Modules to REMOVE (44 modules)
See PLAN_PART_1_PRE_HUMAN.md for complete list.

### Key Dependencies Identified
- JUnit 4.13.2 (for tests)
- org.jetbrains:annotations:24.0.1 (for nullability)
- No external JVM blockers for kept modules

### Total Regex Migrations Required
~167 usages across thorgCore modules

## Decision Log

1. **Keep flexmark-test-specs** - Required by flexmark and flexmark-core-test for test resources
2. **Phase 0 before Maven->Gradle** - Simpler to remove modules while still Maven
3. **Human does IntelliJ conversion** - Non-negotiable per requirements
4. **Gradle Multi-Project** - Standard Kotlin-MP structure
5. **JVM-only tests initially** - Run tests via JVM target, expand to JS later

## Open Questions (Resolved)

1. Q: Should flexmark-ext-typographic be kept for tables tests?
   A: No - test dependency only, tests can be updated to not require it

2. Q: How to handle flexmark-test-specs?
   A: Keep it - contains CommonMark spec files needed by tests
