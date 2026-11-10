# Lexers

This module converts raw text into a stream of tokens. It is the first stage of the Mau processing pipeline.

## Overview

Lexers scan input text character by character and line by line, recognising patterns and emitting `Token` objects. Each token carries a type, a string value, and a `Context` recording its source location.

## Files

- `base_lexer.py` - Abstract `BaseLexer` with the core lexing loop, position tracking, infinite-loop detection, and token creation helpers.
- `document_lexer.py` - `DocumentLexer` recognises document-level constructs (headers, blocks, lists, variables, includes, comments, etc.).
- `text_lexer.py` - `TextLexer` recognises inline constructs (styles, macros, escape sequences, verbatim text).
- `arguments_lexer.py` - `ArgumentsLexer` tokenises comma-separated argument lists inside `[...]`.
- `condition_lexer.py` - `ConditionLexer` tokenises conditional expressions after `@if` and in the `[if]`/`[ifeval]` macros.
- `preprocess_variables_lexer.py` - `PreprocessVariablesLexer` tokenises text to find `{name}` variables to replace, handling the `\` and backtick escapes.

## Key classes

### `BaseLexer`

Abstract base class. Subclasses implement `_process_functions()` returning a list of callables, each of which tries to match and consume the current input. The base loop calls them in order until one succeeds, then restarts from the top.

### `DocumentLexer(BaseLexer)`

Recognises top-level document elements:

| Syntax | Token type |
|---|---|
| `////...////` | (consumed, no token) |
| `// comment` | (consumed, no token) |
| `---` | `HORIZONTAL_RULE` |
| `----...----` (exactly 4 identical characters, e.g. `----`, `####`, `@@@@`) | `BLOCK` |
| `@operator condition` | `CONTROL` |
| `<< type:args` | `INCLUDE` |
| `:name:value` | `VARIABLE` |
| `[arguments]` | `ARGUMENTS` |
| `.label text` | `LABEL` |
| `* item` / `# item` | `LIST` |
| `= Header` | `HEADER` |
| text | `TEXT` |

### `TextLexer(BaseLexer)`

Recognises inline syntax within text lines:

| Syntax | Meaning |
|---|---|
| `*`, `_`, `~`, `^` | Style delimiters (`star`, `underscore`, `tilde`, `caret`; the rendering depends on the templates) |
| `` ` `` | Verbatim text |
| `[name](args)` | Macro call |
| `$...$`, `%...%` | Escape whole spans |
| `\` | Escapes the next character |
| `"` | Quotes macro arguments |

## How it connects

```
Raw text --> DocumentLexer --> list[Token]
                                  |
                                  v
                             DocumentParser
```

The `DocumentLexer` produces a flat list of tokens consumed by the `DocumentParser`. The parser in turn uses `TextLexer` internally to lex inline content within paragraphs and headers.
