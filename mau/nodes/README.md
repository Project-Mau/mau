# Nodes

This module defines the abstract syntax tree (AST) structure. Nodes represent every element in a Mau document and implement the Visitor pattern for rendering.

## Overview

After parsing, the document is represented as a tree of `Node` objects rooted at a `DocumentNode`. Each node carries its type, arguments, labels, source context, and child content. Visitors traverse the tree by calling `node.accept(visitor)`, which dispatches to the appropriate `_visit_*` method.

## Files

- `node.py` - Base `Node` class, `ValueNode`, `WrapperNode`, mixins (`NodeContentMixin`, `NodeLabelsMixin`), and `NodeInfo`.
- `node_arguments.py` - `NodeArguments` container for tags, subtypes, named/unnamed arguments.
- `document.py` - `DocumentNode` (root) and `HorizontalRuleNode`.
- `header.py` - `HeaderNode` with level, internal ID, and source text.
- `paragraph.py` - `ParagraphNode` and `ParagraphLineNode`.
- `inline.py` - `WordNode`, `TextNode`, `VerbatimNode`, `StyleNode`.
- `block.py` - `BlockNode` for generic content blocks.
- `source.py` - `SourceNode` for source code blocks.
- `raw.py` - `RawNode` and `RawLineNode` for unprocessed content.
- `macro.py` - `MacroNode` and specialisations: `MacroLinkNode`, `MacroImageNode`, `MacroHeaderNode`, `MacroFootnoteNode`, `MacroClassNode`, `MacroRawNode`, `MacroUnicodeNode`.
- `include.py` - `IncludeNode`, `IncludeImageNode`, `IncludeMauNode`, `IncludeRawNode`, `TocNode`, `FootnotesNode`, `BlockGroupNode`.
- `list.py` - `ListNode` with nested items.
- `footnote.py` - `FootnoteNode`.
- `condition.py` - `ConditionNode`.

## Key classes

### `Node`

Base class for all nodes:

- `type` - String identifier (e.g. `"header"`, `"paragraph"`).
- `parent` - Reference to the parent node.
- `arguments` - `NodeArguments` instance.
- `info` - `NodeInfo` with source context.
- `accept(visitor, **kwargs)` - Dispatches to the visitor.
- `template_type` - Property used by the Jinja visitor for template lookup. Returns the node type with dots replaced by hyphens.

### `NodeArguments`

Argument container attached to every node:

- `unnamed_args` - Positional arguments.
- `named_args` - Keyword arguments.
- `tags` - Semantic tags (from `#tag` syntax).
- `internal_tags` - System tags (e.g. `"debug"`).
- `subtype` - Optional subtype string.

### Mixins

- `NodeContentMixin` - Adds a `content` list for container nodes.
- `NodeLabelsMixin` - Adds a `labels` dict for labeled nodes (headers, blocks).

## Node hierarchy

```
Node
├── ValueNode (text, verbatim, word)
├── WrapperNode (document, generic container)
│   └── DocumentNode
├── HeaderNode
├── ParagraphNode
│   └── ParagraphLineNode
├── BlockNode
├── SourceNode
├── RawNode / RawLineNode
├── StyleNode
├── ListNode
├── MacroNode
│   ├── MacroLinkNode
│   ├── MacroImageNode
│   ├── MacroHeaderNode
│   ├── MacroFootnoteNode
│   ├── MacroClassNode
│   ├── MacroRawNode
│   └── MacroUnicodeNode
├── IncludeNode
│   ├── IncludeImageNode
│   ├── IncludeMauNode
│   ├── IncludeRawNode
│   ├── TocNode
│   ├── FootnotesNode
│   └── BlockGroupNode
├── FootnoteNode
├── ConditionNode
└── HorizontalRuleNode
```

## How it connects

Nodes are created by the parsers and consumed by the visitors:

```
Parsers --> Node tree --> Visitors
```
