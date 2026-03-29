# Parsers

This module converts a token stream into an abstract syntax tree (AST) of `Node` objects. It is the second stage of the Mau processing pipeline.

## Overview

Parsers consume tokens produced by the lexers and build a tree of nodes representing the document structure. The `DocumentParser` orchestrates the process, delegating to specialised processors for each element type and to `TextParser` for inline content.

## Files

- `base_parser.py` - Abstract `BaseParser` with the core parsing loop, token navigation via `TokensManager`, and infinite-loop detection.
- `document_parser.py` - `DocumentParser` orchestrates full document parsing.
- `text_parser.py` - `TextParser` recursively parses inline content (styles, macros, links, etc.).
- `arguments_parser.py` - `ArgumentsParser` parses named/unnamed arguments and handles the alias system.
- `condition_parser.py` - `ConditionParser` evaluates `@if`/`@unless` conditions.
- `preprocess_variables_parser.py` - `PreprocessVariablesParser` handles variable definitions during preprocessing.

### `document_processors/`

Modular processors, each handling one document element type:

- `header.py` - Headers (`= Title`)
- `block.py` - Blocks (delimited by four identical characters)
- `paragraph.py` - Paragraphs (sequences of text lines)
- `list.py` - Lists (`*` and `#` items)
- `include.py` - Include directives (`<< type:args`)
- `label.py` - Labels (`.title`, `.role title`)
- `control.py` - Conditional rendering (`@if`, `@unless`, `@else`, `@elseif`)
- `variable_definition.py` - Variable definitions (`:name:value`)
- `arguments.py` - Argument lines (`[arguments]`)
- `horizontal_rule.py` - Horizontal rules (`---`)

### `document_processors/block_engines/`

Each block engine determines how block content is processed:

- `default.py` - Content is parsed as Mau (produces a `BlockNode`).
- `raw.py` - Content is passed through unchanged (produces a `RawNode`).
- `source.py` - Content is treated as source code with optional highlighting markers (produces a `SourceNode`).

### `buffers/`

State buffers that hold pending data between parser steps:

- `arguments_buffer.py` - Stores arguments from `[...]` lines until the next element consumes them.
- `control_buffer.py` - Stores control conditions from `@if`/`@unless` lines.
- `label_buffer.py` - Stores labels from `.label` lines.

### `managers/`

Stateful managers that track cross-cutting concerns:

- `toc_manager.py` - Collects headers for table of contents generation.
- `footnotes_manager.py` - Tracks footnote definitions and references.
- `header_links_manager.py` - Manages internal links to headers.
- `blockgroup_manager.py` - Groups blocks by name for later inclusion.

## Key classes

### `DocumentParser(BaseParser)`

The main parser. It:
1. Preprocesses variable definitions.
2. Runs the `DocumentLexer` on the input.
3. Iterates over tokens, dispatching to processors based on token type.
4. Manages buffers (arguments, labels, control) and managers (TOC, footnotes, headers, block groups).
5. Handles recursive `<< mau` includes with cycle detection.

Default aliases defined in `DEFAULT_ARGUMENT_ALIASES`:
- `source` - Sets `engine=source`, names the first positional arg `language`.

### `TextParser(BaseParser)`

Recursively parses inline content. Produces nodes for:
- Plain text (`TextNode`)
- Styles (`StyleNode`) for `*bold*`, `_underline_`, `~strikethrough~`, `^superscript^`
- Verbatim text (`VerbatimNode`) for `` `code` ``
- Macros: `[link]`, `[image]`, `[header]`, `[footnote]`, `[mailto]`, `[class]`, `[unicode]`, `[raw]`, `[if:...]`, `[ifeval:...]`

### `ArgumentsParser`

Parses argument lists and applies the alias system:
- `#tag` - Tags
- `*subtype` - Subtypes
- `@alias` - Aliases (looks up `mau.parser.aliases` in the environment)
- `key=value` - Named arguments
- Positional arguments

## How it connects

```
list[Token] --> DocumentParser --> list[Node] (AST)
                    |                   |
                    |                   v
                    |              Visitors
                    |
                    +-- TextParser (inline content)
                    +-- ArgumentsParser (argument lists)
                    +-- ConditionParser (conditions)
```
