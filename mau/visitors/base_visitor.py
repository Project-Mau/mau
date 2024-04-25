import functools
import logging

import yaml
from mau.errors import MauError, MauErrorException

_logger = logging.getLogger(__name__)


class MauVisitorError(MauError):
    source = "visitor"

    def print_details(self):  # pragma: no cover
        super().print_details()

        print("Node:")
        print(self.details["node"])


class NoAliasDumper(yaml.SafeDumper):  # pragma: no cover
    # pylint: disable=unused-argument
    def ignore_aliases(self, data):
        return True


no_aliases_dump = functools.partial(yaml.dump, Dumper=NoAliasDumper)


class BaseVisitor:
    format_code = "yaml"
    extension = ""
    transform = no_aliases_dump

    _join_with = {}
    _join_with_default = None

    # pylint: disable=unused-argument
    def __init__(self, environment, *args, **kwds):
        self.toc = None
        self.footnotes = None

        self.environment = environment

    def visit(self, node, *args, **kwargs):
        # The visitor has to define functions for each node type.
        # Those shall return a dictionary with the key "data" that
        # contains the result of the visit.
        # This is done to provide space for metadata or other values
        # like templates used to render the node.

        if node is None:
            return {}

        return node.accept(self, *args, **kwargs)

    def visitlist(self, node, nodes, *args, **kwargs):
        join_with = self._join_with.get(node.node_type, self._join_with_default)

        visited_nodes = [self.visit(i, *args, **kwargs) for i in nodes]

        if join_with is not None:
            return join_with.join(visited_nodes)

        return visited_nodes

    def visitdict(self, node, nodedict, *args, **kwargs):
        return {k: self.visit(v, *args, **kwargs) for k, v in nodedict.items()}

    def _error(self, message, node=None):
        error = MauVisitorError(
            message=message,
            details={
                "node": node,
            },
        )

        raise MauErrorException(error)

    def _visit_default(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "subtype": node.subtype,
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    # Inline nodes

    def _visit_raw(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_text(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_verbatim(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_sentence(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_style(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "value": node.value,
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_macro(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "name": node.name,
            }
        )

        return result

    def _visit_footnote(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content": self.visitlist(node, node.children, *args, **kwargs),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            }
        )

        return result

    def _visit_macro__class(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "classes": node.classes,
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_macro__link(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "target": node.target,
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_macro__header(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "header": {
                    "anchor": node.header.anchor,
                    "value": self.visit(node.header.value, *args, **kwargs),
                    "level": node.header.level,
                },
                "content": self.visitlist(node, node.children, *args, **kwargs)
                if node.children
                else self.visit(node.header.value, *args, **kwargs),
            }
        )

        return result

    def _visit_macro__image(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "uri": node.uri,
                "alt_text": node.alt_text,
                "width": node.width,
                "height": node.height,
            }
        )

        return result

    def _visit_list_item(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "level": int(node.level),
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_paragraph(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "title": self.visit(node.title, *args, **kwargs),
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_header(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)

        result["data"].update(
            {
                "value": self.visit(node.value, *args, **kwargs),
                "level": int(node.level),
                "anchor": node.anchor,
            }
        )

        return result

    def _visit_list(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "ordered": node.ordered,
                "items": self.visitlist(node, node.children, *args, **kwargs),
                "main_node": node.main_node,
                "start": node.start,
            }
        )

        return result

    def _visit_content(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content_type": node.content_type,
                "uris": node.uris,
                "title": self.visit(node.title, *args, **kwargs),
            }
        )

        return result

    def _visit_content_image(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "uri": node.uri,
                "alt_text": node.alt_text,
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
            }
        )

        return result

    def _visit_block(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content": self.visitlist(node, node.children, *args, **kwargs),
                "secondary_content": self.visitlist(
                    node, node.secondary_children, *args, **kwargs
                ),
                "subtype": node.subtype,
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
                "engine": node.engine,
                "preprocessor": node.preprocessor,
            }
        )

        return result

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
        code = self.visitlist(node, node.code, *args, **kwargs)

        # This is a list of callouts for each line
        # None if the callout is not present, otherwise
        # the rendered callout
        markers = [None] * len(code)

        for marker in node.markers:
            markers[marker.line] = self.visit(marker, *args, **kwargs)

        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "code": code,
                "subtype": node.subtype,
                "language": node.language,
                "callouts": self.visitlist(node, node.callouts, *args, **kwargs),
                "highlights": node.highlights,
                "markers": markers,
                "classes": node.classes,
                "title": self.visit(node.title, *args, **kwargs),
                "preprocessor": node.preprocessor,
                "lines": len(node.code),
            }
        )

        return result

    def _visit_callout(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "line": node.line,
                "marker": node.marker,
            }
        )

        return result

    def _visit_callouts_entry(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "marker": node.marker,
                "value": node.value,
            }
        )

        return result

    def _visit_toc_entry(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "value": self.visit(node.value, *args, **kwargs),
                "anchor": node.anchor,
                "children": self.visitlist(node, node.children, *args, **kwargs),
                "tags": node.tags,
            },
        }

    def _visit_toc(self, node, *args, **kwargs):
        return {
            "data": {
                "type": node.node_type,
                "entries": self.visitlist(node, node.children, *args, **kwargs),
                "args": node.args,
                "kwargs": node.kwargs,
                "tags": node.tags,
            },
        }

    def _visit_footnotes(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "entries": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_footnotes_entry(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content": self.visitlist(node, node.children, *args, **kwargs),
                "number": node.number,
                "reference_anchor": node.reference_anchor,
                "content_anchor": node.content_anchor,
            }
        )

        return result

    def _visit_container(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "content": self.visitlist(node, node.children, *args, **kwargs),
            }
        )

        return result

    def _visit_document(self, node, *args, **kwargs):
        return self._visit_container(node)

    def _visit_block_group(self, node, *args, **kwargs):
        result = self._visit_default(node, *args, **kwargs)
        result["data"].update(
            {
                "title": self.visit(node.title, *args, **kwargs),
                "group_name": node.group_name,
                "group": self.visitdict(node, node.group, *args, **kwargs),
            }
        )

        return result
