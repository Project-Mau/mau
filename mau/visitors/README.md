# Visitors

This module renders the AST into output formats. It is the third and final stage of the Mau processing pipeline.

## Overview

Visitors traverse the node tree using the Visitor pattern. Each node's `accept()` method calls the corresponding `_visit_*` method on the visitor. The base visitor returns Python dictionaries; specialised visitors transform these into concrete formats (HTML via Jinja templates, YAML, etc.).

## Files

- `base_visitor.py` - Abstract `BaseVisitor` with default implementations for all node types.
- `jinja_visitor.py` - `JinjaVisitor` renders nodes through Jinja2 templates.
- `yaml_visitor.py` - `YamlVisitor` serialises the node tree to YAML.

## Key classes

### `BaseVisitor`

Abstract base class. Provides:

- `format_code` - Output format identifier.
- `extension` - File extension for the output.
- `process(node, **kwargs)` - Main entry point. Calls `_preprocess()`, `visit()`, and `_postprocess()` in sequence.
- `visit(node, **kwargs)` - Visits a single node by dispatching to `_visit_<type>()`.
- `visitlist(nodes)` - Visits a list of nodes.
- `visitdict(nodes_dict)` - Visits a dictionary of nodes.
- `visitdictlist(nodes_dict)` - Visits a dictionary of node lists.
- `_get_node_data(node)` - Extracts common metadata (arguments, tags, labels) from a node.

Default `_visit_*` methods return dictionaries of node data. Subclasses override these to produce format-specific output.

### `JinjaVisitor(BaseVisitor)`

Renders nodes using Jinja2 templates. Features:

- **Template discovery** - Templates are loaded from providers registered in the environment.
- **Specificity matching** - Templates are matched by node type, subtype, parent type, and tags, with a scoring system to select the most specific match.
- **Fallback chain** - If no specific template matches, falls back to the generic type template, then to a default template.

External visitor packages (like `mau-html-visitor`) extend `JinjaVisitor` and provide their own template sets.

### `YamlVisitor(BaseVisitor)`

Serialises the visitor output to YAML. Uses a no-alias YAML dumper for clean output. This visitor is built into the core package and useful for debugging and inspecting the AST.

## Extending with plugins

Visitor plugins are discovered via Python entry points under the group `mau.visitors`. A plugin registers its visitor class, which is then available as a `-t` option in the CLI.

The core package registers:
- `core:YamlVisitor`
- `core:JinjaVisitor`

External packages add entries like:
- `core:HtmlVisitor` (from `mau-html-visitor`)
- `core:TexVisitor` (from `mau-tex-visitor`)

## How it connects

```
Node tree --> Visitor --> Output (HTML, YAML, TeX, ...)
                |
                +-- Environment (template paths, configuration)
```
