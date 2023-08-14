import yaml

import logging

from mau.parsers.toc import create_toc

_logger = logging.getLogger(__name__)


class VisitorError(ValueError):
    """This is a detailed visitor error"""

    def __init__(self, message, node=None):
        super().__init__(message)

        self.node = node

    def __repr__(self):
        return f"{super().__str__()} - Node: {self.node}"

    def __str__(self):
        return self.__repr__()


class BaseVisitor:
    format_code = "dump"
    extension = ""
    transform = yaml.dump

    # pylint: disable=unused-argument
    def __init__(self, *args, **kwds):
        self.toc = None
        self.footnotes = None

        self._join_with = {}

    def visit(self, node, *args, **kwargs):
        # The visitor has to define functions for each node type.
        # Those shall return a dictionary with the key "data" that
        # contains the result of the visit.
        # This is done to provide space for metadata or other values
        # like templates used to render the node.

        if node is None:
            return {}

        return node.accept(self, *args, **kwargs)

    def visitlist(self, nodes, *args, **kwargs):
        join_with = kwargs.pop("join_with", None)

        visited_nodes = [self.visit(i, *args, **kwargs) for i in nodes]

        if join_with is not None:
            return join_with.join(visited_nodes)

        return visited_nodes

    def _error(self, message, node=None):
        raise VisitorError(message, node)

    def _visit_default(self, node):
        self._error("Cannot find visit function", node)

    # Inline nodes

    def _visit_text(self, node):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
            },
        }

    def _visit_verbatim(self, node):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
            },
        }

    def _visit_sentence(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(node.content, join_with=join_with),
            },
        }

    def _visit_style(self, node):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
                "content": self.visit(node.content),
            },
        }

    def _visit_macro(self, node):
        return {
            "data": {
                "type": node.node_type,
                "name": node.name,
                "args": node.args,
                "kwargs": node.kwargs,
            },
        }

    def _visit_footnote(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(node.content, join_with=join_with),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_class(self, node):
        return {
            "data": {
                "type": node.node_type,
                "classes": node.classes,
                "content": self.visit(node.content),
            },
        }

    def _visit_link(self, node):
        return {
            "data": {
                "type": node.node_type,
                "target": node.target,
                "text": node.text,
            },
        }

    def _visit_image(self, node):
        return {
            "data": {
                "type": node.node_type,
                "uri": node.uri,
                "alt_text": node.alt_text,
                "width": node.width,
                "height": node.height,
            },
        }

    def _visit_list_item(self, node):
        return {
            "data": {
                "type": node.node_type,
                "level": int(node.level),
                "content": self.visit(node.content),
            },
        }

    # Page nodes

    def _visit_horizontal_rule(self, node):
        return {
            "data": {
                "type": node.node_type,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_paragraph(self, node):
        return {
            "data": {
                "type": node.node_type,
                "content": self.visit(node.content),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_header(self, node):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
                "level": int(node.level),
                "anchor": node.anchor,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_list(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "ordered": node.ordered,
                "items": self.visitlist(node.items, join_with=join_with),
                "main_node": node.main_node,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_content(self, node):
        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "title": self.visit(node.title),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_content_image(self, node):
        return {
            "data": {
                "type": node.node_type,
                "uri": node.uri,
                "alt_text": node.alt_text,
                "classes": node.classes,
                "title": self.visit(node.title),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_block(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "blocktype": node.blocktype,
                "content": self.visitlist(node.content, join_with=join_with),
                "secondary_content": self.visitlist(
                    node.secondary_content, join_with=join_with
                ),
                "classes": node.classes,
                "title": self.visit(node.title),
                "engine": node.engine,
                "preprocessor": node.preprocessor,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            }
        }

    def _visit_source(self, node):
        for method_name in [
            "_visit_source__default",
            f"_visit_source_{node.language}",
        ]:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                continue

        return method(node)

    def _visit_source__default(self, node):
        code = self.visitlist(node.code)

        # This is a list of callouts for each line
        # None if the callout is not present, otherwise
        # the rendered callout
        markers = [None] * len(code)

        for marker in node.markers:
            markers[marker.line] = self.visit(marker)

        return {
            "data": {
                "type": node.node_type,
                "blocktype": node.blocktype,
                "code": code,
                "language": node.language,
                "callouts": self.visitlist(node.callouts),
                "highlights": node.highlights,
                "markers": markers,
                "classes": node.classes,
                "title": self.visit(node.title),
                "preprocessor": node.preprocessor,
                "lines": len(node.code),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_callout(self, node):
        return {
            "data": {
                "type": node.node_type,
                "line": node.line,
                "marker": node.marker,
            },
        }

    def _visit_callouts_entry(self, node):
        return {
            "data": {
                "type": node.node_type,
                "marker": node.marker,
                "value": node.value,
            },
        }

    def _visit_toc_entry(self, node, exclude_tag=None):
        join_with = self._join_with.get(node.node_type, None)

        children = [i for i in node.children if exclude_tag not in i.tags]

        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
                "anchor": node.anchor,
                "children": self.visitlist(children, join_with=join_with),
                "args": self.toc.args,
                "kwargs": self.toc.kwargs,
                "tags": self.toc.tags,
            },
        }

    def _visit_command_toc(self, node):
        join_with = self._join_with.get(node.node_type, None)

        if self.toc is None:
            self.toc = create_toc(
                node.entries, args=node.args, kwargs=node.kwargs, tags=node.tags
            )

        entries = [
            i for i in self.toc.entries if node.kwargs.get("exclude_tag") not in i.tags
        ]

        return {
            "data": {
                "type": node.node_type,
                "entries": self.visitlist(
                    entries,
                    exclude_tag=self.toc.kwargs.get("exclude_tag"),
                    join_with=join_with,
                ),
                "args": self.toc.args,
                "kwargs": self.toc.kwargs,
                "tags": self.toc.tags,
            },
        }

    def _visit_command_footnotes(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "entries": self.visitlist(node.entries, join_with=join_with),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_footnotes_entry(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(node.content, join_with=join_with),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_container(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(node.content, join_with=join_with),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_document(self, node):
        return self._visit_container(node)

    def _visit_reference(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "name": node.name,
                "category": node.category,
                "content": self.visitlist(node.content, join_with=join_with),
                "number": node.number,
                "title": self.visit(node.title),
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_command_references(self, node):
        join_with = self._join_with.get(node.node_type, None)

        entries = [
            i for i in node.entries.values() if i.content_type == node.content_type
        ]

        if node.category is not None:
            entries = [i for i in entries if i.category == node.category]

        if node.name is not None:
            entries = [i for i in entries if i.name == node.name]

        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "category": node.category,
                "name": node.name,
                "entries": self.visitlist(entries, join_with=join_with),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_references_entry(self, node):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "name": node.name,
                "category": node.category,
                "content": self.visitlist(node.content, join_with=join_with),
                "number": node.number,
                "title": self.visit(node.title),
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }
