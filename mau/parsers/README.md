# Parsers

This module converts a token stream into an abstract syntax tree (AST) of `Node` objects. It is the second stage of the Mau processing pipeline.

## Overview

Parsers consume tokens produced by the lexers and build a tree of nodes representing the document structure. The `DocumentParser` orchestrates the process, delegating to specialised processors for each element type and to `TextParser` for inline content.

## Files

- `base_parser.py` - Abstract `BaseParser` with the core parsing loop, token navigation via `TokensManager`, and infinite-loop detection.
- `document_parser.py` - `DocumentParser` orchestrates full document parsing.
- `text_parser.py` - `TextParser` recursively parses inline content (styles, macros, links, etc.).
- `arguments_parser.py` - `ArgumentsParser` parses named/unnamed arguments and handles the alias system.
- `condition_parser.py` - `ConditionParser` parses `@if` conditions and the conditions of the `[if]`/`[ifeval]` macros (`==`, `!=`). The evaluation is done by the control buffer and by the macros.
- `preprocess_variables_parser.py` - `PreprocessVariablesParser` replaces `{name}` variables in text before it is parsed.
- `jinja_preprocessor.py` - `render_jinja_source` renders the text of an included Mau file as a Jinja template before it is parsed (`<< mau:URI, preprocess=jinja`).

### `document_processors/`

Modular processors, each handling one document element type:

- `header.py` - Headers (`= Title`)
- `block.py` - Blocks (delimited by four identical characters)
- `paragraph.py` - Paragraphs (sequences of text lines)
- `list.py` - Lists (`*` and `#` items)
- `include.py` - Include directives (`<< type:args`)
- `label.py` - Labels (`.title`, `.role title`)
- `control.py` - Conditional rendering (`@if`)
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
- `control_buffer.py` - Stores control conditions from `@if` lines.
- `label_buffer.py` - Stores labels from `.label` lines.

### `managers/`

Stateful managers that track cross-cutting concerns:

- `toc_manager.py` - Collects headers for table of contents generation.
- `footnotes_manager.py` - Tracks footnote definitions and references.
- `header_links_manager.py` - Manages internal links to headers.
- `blockgroup_manager.py` - Groups blocks by name for later inclusion.
- `tokens_manager.py` - `TokensManager`, used by `BaseParser` to navigate the token stream.

## Key classes

### `DocumentParser(BaseParser)`

The main parser. It:
1. Receives the tokens produced by the `DocumentLexer`.
2. Replaces `{name}` variables in each piece of text (with `PreprocessVariablesParser`) before passing it to the `TextParser`.
3. Iterates over tokens, dispatching to processors based on token type.
4. Manages buffers (arguments, labels, control) and managers (TOC, footnotes, headers, block groups).
5. Handles recursive `<< mau` includes with cycle detection.
6. Supports non-isolated content (blocks and `<< mau` includes with `isolate=false`). The child parser is created with `isolate=False`, so it doesn't process its ToC, footnotes, and header links. The parent merges them with `merge_managers()` and processes them together with its own.
7. Reads `mau.parser.include_paths_strategy` (`cwd` or `file`), which sets how relative paths in `<< mau` and `<< raw` are resolved. Child parsers for included files and blocks receive the value of their parent through the argument `include_paths_strategy`, so the setting applies to the whole document.

Default aliases defined in `DEFAULT_ARGUMENT_ALIASES` (custom ones are read from `mau.parser.aliases`):
- `source` - Sets `engine=source`, names the first positional arg `language`.

An alias can set named arguments (`args`), names for the positional arguments (`names`), and a `subtype`.

Default source highlight style aliases defined in `DEFAULT_STYLE_ALIASES` (custom ones are read from `mau.parser.source_highlight_style_aliases`): `+` (add), `-` (remove), `!` (important), `x` (error).

### `TextParser(BaseParser)`

Recursively parses inline content. Produces nodes for:
- Plain text (`TextNode`, `WordNode`)
- Styles (`StyleNode`) for `*star*`, `_underscore_`, `~tilde~`, `^caret^`
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
