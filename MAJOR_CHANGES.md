# Major changes in Mau v5

This document lists the breaking changes between Mau v4 and Mau v5. Each entry includes a pointer to the relevant documentation chapter.

## Alias system replaces subtype prefix for blocks

The `*subtype` syntax for block specialisation (e.g. `[*source, python]`) has been replaced by the `@alias` syntax (e.g. `[@source, python]`). Aliases can inject default named arguments and assign positional names to unnamed arguments. Custom aliases are defined through the environment under `mau.parser.aliases`. The `*subtype` syntax still works for pure subtypes like `*quote`.

See chapters 9 (Arguments) and 14 (Blocks).

## Commands merged into includes

The `::` command syntax for inserting table of contents, footnotes, and block groups has been removed. These are now part of the include system using `<<`.

| v4                     | v5                      |
|------------------------|-------------------------|
| `::toc:`               | `<< toc`                |
| `::footnotes:`         | `<< footnotes`          |
| `::blockgroup:mygroup` | `<< blockgroup:mygroup` |

See chapters 16 (Include), 18 (Table of contents), 19 (Footnotes), and 20 (Block groups).

## Node type naming uses hyphens

Node types use hyphenated names instead of dot notation. This affects template file names.

| v4              | v5              |
|-----------------|-----------------|
| `macro.link`    | `macro-link`    |
| `macro.image`   | `macro-image`   |
| `include.image` | `include-image` |
| `include.mau`   | `include-mau`   |

See chapter 26 (List of nodes) for the complete list.

## Template naming and matching system

The Jinja visitor template system has been rewritten. Templates are matched using a specificity-based system. Template file names encode claims about the node they target using a dot-separated convention:

```
TYPE[.SUBTYPE][.KEY__VALUE][.tg_TAG][.pt_PARENT][.pts_PARENTSUBTYPE][.pf_PREFIX].j2
```

Templates are sorted by specificity and the most specific match wins. Custom template fields allow nodes to expose additional matching criteria beyond type and subtype.

See chapters 22 (Introduction to templates) and 23 (How templates work).

## Labels replace title

The `.title` syntax (`. Some title`) has been generalised into a label system. Labels have a role and content: `.role text`. The default role is `title`, so `. Some title` still works. Multiple labels with different roles can precede a node.

See chapter 8 (Labels).

## Condition syntax

Conditions now use `==` and `!=` operators instead of the v4 colon-separated format.

| v4                       | v5                       |
|--------------------------|--------------------------|
| `@if:variable:&true`     | `@if variable==true`     |
| `[ifeval:website:&true]` | `[ifeval:website==true]` |

See chapter 10 (Control).

## Variables are always strings

All variables are strings. Boolean-like values `True` and `False` do not exist; use `"true"` and `"false"`. The shortcuts `:+flag:` and `:-flag:` set the value to the string `"true"` or `"false"`.

See chapter 7 (Variables).

## Footnote blocks use named argument

Footnote blocks use the `footnote` named argument instead of the `*footnote` subtype.

| v4                  | v5                |
|---------------------|-------------------|
| `[*footnote, name]` | `[footnote=name]` |

See chapter 19 (Footnotes).

## Blockgroup naming

The internal naming changed from `block_group` to `blockgroup` (single word). This affects environment keys and template file names.

See chapter 20 (Block groups).

## Error handling and message system

Errors use a message handler pattern. `MauException` wraps a message object with types `MauLexerErrorMessage`, `MauParserErrorMessage`, `MauVisitorErrorMessage`, and `MauVisitorDebugMessage`. Code that catches Mau exceptions should access the `.message` attribute.

See chapter 28 (Python interface), section "Error handling" and "Message handlers".

## Source highlight style aliases

Default style aliases for source code highlighting have been added: `+` (add), `-` (remove), `!` (important), `x` (error). These are configurable through `mau.parser.source_highlight_style_aliases`.

See chapter 15 (Source blocks).

## Visitor plugin system

Visitors are discovered at runtime through the `mau.visitors` entry point group. Template providers use the `mau.templates` entry point group. The two core visitors (`core:YamlVisitor` and `core:JinjaVisitor`) are always available.

See chapters 24 (Existing visitors), 25 (Create a custom visitor), and 28 (Python interface).
