# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**flexmark-java** is a Java implementation of the CommonMark (spec 0.28) Markdown parser. It's designed as a high-performance, extensible replacement for pegdown, primarily used in the "Markdown Navigator" JetBrains IDE plugin.

Key characteristics:
- **Language**: Java 11+ (versions 0.62.2 and below support Java 8+)
- **Build system**: Maven multi-module project with 60+ modules
- **Version**: 0.64.8
- **License**: BSD 2-Clause

## Build Commands

```bash
# Run all tests
mvn test -Dsurefire.useFile=false

# Build and install (skip tests for faster iteration)
mvn clean install -DskipTests

# Run tests for a specific module
mvn test -pl flexmark-core-test -Dsurefire.useFile=false

# Run a single test class
mvn test -pl flexmark-core-test -Dtest=ComboCoreSpecTest -Dsurefire.useFile=false
```

## Architecture

### Parsing Pipeline
The parser uses a "blocks first, inlines after" architecture:
1. **Block parsing**: Identifies block-level elements (paragraphs, lists, code blocks, etc.)
2. **Inline parsing**: Parses inline elements (emphasis, links, code spans) within blocks
3. **Rendering**: Visitor pattern traverses AST to produce output

### Module Organization

**Core modules:**
- `flexmark/` - Core parser, HTML renderer, and formatter
- `flexmark-util-*` - Utility modules (ast, data, sequence, collection, dependency, etc.)
- `flexmark-test-util/` - Test framework and utilities

**Extension modules** (`flexmark-ext-*`):
- 32 extensions implementing various Markdown flavors
- Each follows the same pattern: AST nodes, block/inline parsers, renderers

**Converter modules:**
- `flexmark-html2md-converter` - HTML to Markdown
- `flexmark-docx-converter` - DOCX output
- `flexmark-pdf-converter` - PDF output
- `flexmark-jira-converter`, `flexmark-youtrack-converter` - Issue tracker formats

**Aggregation:**
- `flexmark-all/` - Uber JAR containing core + all extensions + converters

### Key Patterns

**Configuration system:**
```java
MutableDataSet options = new MutableDataSet();
options.set(Parser.EXTENSIONS, Arrays.asList(TablesExtension.create()));
Parser parser = Parser.builder(options).build();
```

**Extension interface:**
Extensions implement `Parser.ParserExtension`, `HtmlRenderer.HtmlRendererExtension`, and/or `Formatter.FormatterExtension`. See `flexmark-ext-tables/` for a reference implementation.

**AST structure:**
- All nodes extend from classes in `flexmark-util-ast`
- Nodes track exact source positions including individual character positions
- Visitor pattern for traversal (`NodeVisitor`, `VisitHandler`)

### Test Framework

Tests use a spec-based approach with `.md` files containing test cases:
- Spec files in `src/test/resources/` (e.g., `ast_spec.md`)
- Test classes extend spec test base classes and reference `SPEC_RESOURCE`
- Format: markdown input, expected HTML output, and optionally expected AST

Example test class pattern:
```java
public class ComboCoreSpecTest extends CoreRendererSpecTest {
    static final String SPEC_RESOURCE = "/ast_spec.md";
    // ...
}
```

## Key Files

- `flexmark/src/main/java/com/vladsch/flexmark/parser/` - Parser implementation
- `flexmark/src/main/java/com/vladsch/flexmark/html/` - HTML renderer
- `flexmark/src/main/java/com/vladsch/flexmark/formatter/` - Markdown formatter
- `flexmark-core-test/src/test/resources/ast_spec.md` - Core specification tests
- `flexmark-java-samples/src/` - Usage examples

## Parser Emulation Profiles

The parser can emulate different Markdown processors via `ParserEmulationProfile`:
- `COMMONMARK` (default)
- `GITHUB_DOC`
- `KRAMDOWN`
- `MARKDOWN` (Markdown.pl)
- `MULTI_MARKDOWN`
- `PEGDOWN` / `PEGDOWN_STRICT`

For pegdown migration, use `PegdownOptionsAdapter` from `flexmark-profile-pegdown`.
