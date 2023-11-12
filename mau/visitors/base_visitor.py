import copy
import logging

import yaml
from mau.errors import MauError, MauErrorException
from mau.parsers.toc import create_toc

_logger = logging.getLogger(__name__)


class MauVisitorError(MauError):
    source = "visitor"

    def print_details(self):  # pragma: no cover
        super().print_details()

        print("Node:")
        print(self.details["node"])


class BaseVisitor:
    format_code = "dump"
    extension = ""
    transform = yaml.dump

    # pylint: disable=unused-argument
    def __init__(self, *args, config=None, **kwds):
        self.toc = None
        self.footnotes = None
        self.config = copy.deepcopy(config) if config else {}

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
        error = MauVisitorError(
            message=message,
            details={
                "node": node,
            },
        )

        raise MauErrorException(error)

    def _visit_default(self, node, *args, **kwargs):
        self._error("Cannot find visit function", node)

    # Inline nodes

    def _visit_raw(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
            },
        }

    def _visit_text(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
            },
        }

    def _visit_verbatim(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
            },
        }

    def _visit_sentence(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
            },
        }

    def _visit_style(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
                "content": self.visit(node.content, *args, **kwargs),
            },
        }

    def _visit_macro(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "name": node.name,
                "args": node.args,
                "kwargs": node.kwargs,
            },
        }

    def _visit_footnote(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_class(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "classes": node.classes,
                "content": self.visit(node.content, *args, **kwargs),
            },
        }

    def _visit_link(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "target": node.target,
                "text": node.text,
            },
        }

    def _visit_image(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "uri": node.uri,
                "alt_text": node.alt_text,
                "width": node.width,
                "height": node.height,
            },
        }

    def _visit_list_item(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "level": int(node.level),
                "content": self.visit(node.content, *args, **kwargs),
            },
        }

    # Page nodes

    def _visit_horizontal_rule(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_paragraph(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "content": self.visit(node.content, *args, **kwargs),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_header(self, node, *args, **kwargs):
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

    def _visit_list(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "ordered": node.ordered,
                "items": self.visitlist(
                    node.items, *args, join_with=join_with, **kwargs
                ),
                "main_node": node.main_node,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_content(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "title": self.visit(node.title, *args, **kwargs),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_content_image(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "uri": node.uri,
                "alt_text": node.alt_text,
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_block(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "blocktype": node.blocktype,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "secondary_content": self.visitlist(
                    node.secondary_content, *args, join_with=join_with, **kwargs
                ),
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
                "engine": node.engine,
                "preprocessor": node.preprocessor,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            }
        }

    def _visit_source(self, node, *args, **kwargs):
        for method_name in [
            "_visit_source__default",
            f"_visit_source_{node.language}",
        ]:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                continue

        return method(node)

    def _visit_source__default(self, node, *args, **kwargs):
        code = self.visitlist(node.code, *args, **kwargs)

        # This is a list of callouts for each line
        # None if the callout is not present, otherwise
        # the rendered callout
        markers = [None] * len(code)

        for marker in node.markers:
            markers[marker.line] = self.visit(marker, *args, **kwargs)

        return {
            "data": {
                "type": node.node_type,
                "blocktype": node.blocktype,
                "code": code,
                "language": node.language,
                "callouts": self.visitlist(node.callouts, *args, **kwargs),
                "highlights": node.highlights,
                "markers": markers,
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
                "preprocessor": node.preprocessor,
                "lines": len(node.code),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_callout(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "line": node.line,
                "marker": node.marker,
            },
        }

    def _visit_callouts_entry(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "marker": node.marker,
                "value": node.value,
            },
        }

    def _visit_toc_entry(self, node, *args, exclude_tag=None, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        children = [i for i in node.children if exclude_tag not in i.tags]

        return {
            "data": {
                "type": node.node_type,
                "value": node.value,
                "anchor": node.anchor,
                "children": self.visitlist(
                    children, *args, join_with=join_with, **kwargs
                ),
                "args": self.toc.args,
                "kwargs": self.toc.kwargs,
                "tags": self.toc.tags,
            },
        }

    def _visit_command_toc(self, node, *args, **kwargs):
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
                    *args,
                    **kwargs,
                ),
                "args": self.toc.args,
                "kwargs": self.toc.kwargs,
                "tags": self.toc.tags,
            },
        }

    def _visit_command_footnotes(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "entries": self.visitlist(
                    node.entries, *args, join_with=join_with, **kwargs
                ),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_footnotes_entry(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_container(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_document(self, node, *args, **kwargs):
        return self._visit_container(node)

    def _visit_reference(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "name": node.name,
                "category": node.category,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "number": node.number,
                "title": self.visit(node.title, *args, **kwargs),
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }

    def _visit_command_references(self, node, *args, **kwargs):
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
                "entries": self.visitlist(
                    entries, *args, join_with=join_with, **kwargs
                ),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_references_entry(self, node, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, None)

        return {
            "data": {
                "type": node.node_type,
                "content_type": node.content_type,
                "name": node.name,
                "category": node.category,
                "content": self.visitlist(
                    node.content, *args, join_with=join_with, **kwargs
                ),
                "number": node.number,
                "title": self.visit(node.title, *args, **kwargs),
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            },
        }
