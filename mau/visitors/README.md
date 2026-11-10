# Visitors

This module renders the AST into output formats. It is the third and final stage of the Mau processing pipeline.

## Overview

Visitors traverse the node tree using the Visitor pattern. Each node's `accept()` method calls the corresponding `_visit_*` method on the visitor. The base visitor returns Python dictionaries; specialised visitors transform these into concrete formats (HTML via Jinja templates, YAML, etc.).

## Files

- `base_visitor.py` - `BaseVisitor` with default implementations for all node types.
- `jinja_visitor.py` - `JinjaVisitor` renders nodes through Jinja2 templates.
- `yaml_visitor.py` - `YamlVisitor` serialises the node tree to YAML.

## Key classes

### `BaseVisitor`

Base class, usable on its own (it returns Python dictionaries). Provides:

- `format_code` - Output format identifier.
- `extension` - File extension for the output. In the Jinja visitor and its subclasses it is also the extension of the template files.
- `process(node, **kwargs)` - Main entry point. Calls `_preprocess()`, `visit()`, and `_postprocess()` in sequence.
- `visit(node, **kwargs)` - Visits a single node by dispatching to `_visit_<type>()`.
- `visit_data(node, **kwargs)` - Visits a node and returns the data produced by its `_visit_*` method.
- `visitlist(current_node, nodes_list, **kwargs)` - Visits a list of nodes.
- `visitdict(current_node, nodes_dict, **kwargs)` - Visits a dictionary of nodes.
- `visitdictlist(current_node, nodes_dict, **kwargs)` - Visits a dictionary of node lists.
- `_get_node_data(node)` - Extracts common metadata (type, arguments, tags, internal tags, subtype) from a node. Labels and content are added by `_add_visit_labels` and `_add_visit_content`.

Default `_visit_*` methods return dictionaries of node data. Subclasses override these to produce format-specific output.

### `JinjaVisitor(BaseVisitor)`

Renders nodes using Jinja2 templates. Features:

- **Template discovery** - Templates are loaded from four sources, each one overriding the previous: the `default_templates` of the visitor class, the providers listed in `mau.visitor.templates.providers` (entry point group `mau.templates`), the files in the directories listed in `mau.visitor.templates.paths`, and the dictionary `mau.visitor.templates.custom`. Only templates with the visitor's `extension` are used.
- **Specificity matching** - Templates are matched by node type, custom fields, subtype, prefix, parent type, parent custom fields, parent subtype, and tags, and sorted by specificity to select the most specific match. Templates with the prefixes listed in `mau.visitor.templates.prefixes` are tried first.
- **No fallback** - If no template matches a node, the visitor raises an error (`Cannot find a suitable template.`).

External visitor packages (like `mau-html-visitor`) extend `JinjaVisitor` and provide their own template sets.

### `YamlVisitor(BaseVisitor)`

Serialises the visitor output to YAML. Uses a no-alias YAML dumper for clean output. This visitor is built into the core package and useful for debugging and inspecting the AST.

## Extending with plugins

Visitor plugins are discovered via Python entry points under the group `mau.visitors`. A plugin registers its visitor class, which is then available as a `-t` option in the CLI under the name given by the entry point value.

The core visitors are always available (they are added by `load_visitors`, not registered as entry points):
- `core:YamlVisitor`
- `core:JinjaVisitor`

External packages add entries like:
- `mau_html_visitor:HtmlVisitor` (from `mau-html-visitor`)
- `mau_tex_visitor:TexVisitor` (from `mau-tex-visitor`)

## How it connects

```
Node tree --> Visitor --> Output (HTML, YAML, TeX, ...)
                |
                +-- Environment (template paths, configuration)
```
