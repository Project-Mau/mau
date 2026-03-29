from collections.abc import Mapping, Sequence
from typing import Type

from mau.environment.environment import Environment
from mau.message import (
    BaseMessageHandler,
    MauException,
    MauMessage,
    MauVisitorDebugMessage,
    MauVisitorErrorMessage,
)
from mau.nodes.node import Node
from mau.text_buffer import adjust_context, adjust_context_dict


def create_visitor_message(
    message_class: Type[MauMessage],
    text: str,
    node: Node | None = None,
    data: dict | None = None,
    environment: Environment | None = None,
    additional_info: dict[str, str] | None = None,
):
    context = None
    if data:
        context = adjust_context_dict(data["_context"])
    elif node:
        context = adjust_context(node.info.context)

    return message_class(
        text=text,
        context=context,
        node_type=node.type if node else None,
        data=data,
        environment=environment,
        additional_info=additional_info,
    )


def create_visitor_debug_message(
    text: str,
    node: Node | None = None,
    data: dict | None = None,
    environment: Environment | None = None,
    additional_info: dict[str, str] | None = None,
):
    return create_visitor_message(
        MauVisitorDebugMessage,
        text,
        node,
        data,
        environment,
        additional_info,
    )


def create_visitor_exception(
    text: str,
    node: Node | None = None,
    data: dict | None = None,
    environment: Environment | None = None,
    additional_info: dict[str, str] | None = None,
):
    message = create_visitor_message(
        MauVisitorErrorMessage,
        text,
        node,
        data,
        environment,
        additional_info,
    )

    return MauException(message)


class BaseVisitor:
    # The output format that identifies this visitor.
    format_code = "python"
    extension = ""

    def __init__(
        self,
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
    ):
        self.toc = None
        self.footnotes = None

        # The message handler instance.
        self.message_handler = message_handler

        # The configuration environment
        self.environment: Environment = environment or Environment()

    def process(self, node: Node | None, **kwargs):
        # This function is the entry point of the visitor.
        # It visits a node, and the subnodes
        # recursively, but allows the visitor to
        # preprocess the input and postprocess
        # the output.

        # Preprocess the input node.
        node = self._preprocess(node, **kwargs)

        # Visit the node.
        result = self.visit(node, **kwargs)

        # Postprocess the result.
        result = self._postprocess(result, **kwargs)

        return result

    def _preprocess(self, node: Node | None, **kwargs):
        # The base visitor has no
        # preprocess code.
        return node

    def _postprocess(self, result, **kwargs):
        # The base visitor has no
        # postprocess code.
        return result

    def _debug_additional_info(self, node: Node, result: dict):  # pragma: no cover
        # This function provides additional
        # debug information for a node and
        # its visited output.
        return {}

    def _debug_result(self, node: Node, result: dict):  # pragma: no cover
        # This function creates a debug
        # message from the visitor.

        # Create the message.
        message = create_visitor_debug_message(
            text="This is a debug message activated by a Mau internal tag.",
            node=node,
            data=result,
            environment=self.environment,
            additional_info=self._debug_additional_info(node, result),
        )

        # Send the message through the handler.
        self.message_handler.process(message)

    def visit(self, node: Node | None, **kwargs):
        # Simple implementation of the visitor pattern.
        # Here, the visitor passes itself to the node
        # through the method `accept`
        # The node calls a suitable method of the
        # visitor, and the result is returned here.
        #
        # All visitor functions return a dictionary with
        # the key "data" that contains the result of the visit.
        # This is done to provide space for metadata or other values
        # like templates used to render the node.

        if node is None:
            return {}

        result = node.accept(self, **kwargs)

        # Get the internal tags from
        # the output. Check if they activate
        # debugging for the present node.
        if "debug" in result.get("internal_tags", []):  # pragma: no cover
            self._debug_result(node, result)

        if transformer := kwargs.get("transformer"):
            result = transformer(result)

        return result

    def visit_data(self, node: Node | None, **kwargs):
        # Visit a node and return its data dict,
        # skipping template rendering in subclass visitors.
        # Children are still visited normally.

        if node is None:
            return {}

        return node.accept(self, **kwargs)

    def visitlist(self, current_node: Node, nodes_list: Sequence[Node], **kwargs):
        # Visit all the nodes in the given sequence.
        return [self.visit(node, **kwargs) for node in nodes_list]

    def visitdict(self, current_node: Node, nodes_dict: Mapping[str, Node], **kwargs):
        # Visit all the nodes in the given dictionary.
        return {k: self.visit(node, **kwargs) for k, node in nodes_dict.items()}

    def visitdictlist(
        self,
        current_node: Node,
        nodes_dict: Mapping[str, Sequence[Node]],
        **kwargs,
    ):
        # Visit all the nodes in the given dictionary.
        return {
            k: self.visitlist(current_node, nodes, **kwargs)
            for k, nodes in nodes_dict.items()
        }

    def _add_visit_content(self, result: dict, node: Node, **kwargs):
        result.update(
            {
                "content": self.visitlist(node, node.content, **kwargs),
            }
        )

    def _add_visit_labels(self, result: dict, node: Node, **kwargs):
        result.update(
            {
                "labels": self.visitdict(node, node.labels, **kwargs),
            }
        )

    def _get_node_data(self, node: Node, **kwargs) -> dict:
        if not node:
            return {}

        result = {
            "_type": node.type,
            "args": node.arguments.unnamed_args,
            "kwargs": node.arguments.named_args,
            "tags": node.arguments.tags,
            "internal_tags": node.arguments.internal_tags,
            "subtype": node.arguments.subtype,
        }

        if kwargs.get("add_context", True):
            result["_context"] = node.info.context.asdict()

        return result

    def _visit_default(self, node: Node, **kwargs) -> dict:
        # This is the default code to visit a node.

        data = self._get_node_data(node, **kwargs)

        if kwargs.get("add_parent", True):
            data["parent"] = self._get_node_data(node.parent, **kwargs)

        return data

    def _visit_value(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_wrapper(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_label(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "role": node.role,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_text(self, node: Node, **kwargs) -> dict:
        return self._visit_value(node, **kwargs)

    def _visit_verbatim(self, node: Node, **kwargs) -> dict:
        return self._visit_value(node, **kwargs)

    def _visit_word(self, node: Node, **kwargs) -> dict:
        return self._visit_value(node, **kwargs)

    def _visit_style(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "style": node.style,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_header(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "level": node.level,
                "internal_id": node.internal_id,
                "name": node.name,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_macro(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "name": node.name,
            }
        )

        return result

    def _visit_macro_class(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "classes": node.classes,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_macro_link(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "target": node.target,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_macro_unicode(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_macro_raw(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_macro_image(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "uri": node.uri,
                "alt_text": node.alt_text,
                "width": node.width,
                "height": node.height,
            }
        )

        return result

    def _visit_macro_header(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "target_name": node.target_name,
                "header": self.visit_data(node.header, **kwargs),
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_footnote(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "name": node.name,
                "public_id": node.public_id,
                "internal_id": node.internal_id,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_macro_footnote(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "footnote": self.visit_data(node.footnote, **kwargs),
            }
        )

        return result

    def _visit_footnotes_item(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "footnote": self.visit_data(node.footnote, **kwargs),
            }
        )

        return result

    def _visit_footnotes(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "footnotes": self.visitlist(node, node.footnotes, **kwargs),
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_toc_item(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "header": self.visit_data(node.header, **kwargs),
                "entries": self.visitlist(node, node.entries, **kwargs),
            }
        )

        return result

    def _visit_toc(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "plain_entries": self.visitlist(node, node.plain_entries, **kwargs),
                "nested_entries": self.visitlist(node, node.nested_entries, **kwargs),
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_blockgroup_item(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "position": node.position,
                "block_data": self.visit_data(node.block, **kwargs),
                "block": self.visit(node.block, **kwargs),
            }
        )

        return result

    def _visit_blockgroup(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "name": node.name,
                "items": self.visitdict(node, node.items, **kwargs),
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_block(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "classes": node.classes,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_horizontal_rule(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_document(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_include(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "ctype": node.ctype,
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_include_image(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "uri": node.uri,
                "alt_text": node.alt_text,
                "classes": node.classes,
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_include_mau(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "uri": node.uri,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_include_raw(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "uri": node.uri,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_list_item(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "level": node.level,
            }
        )

        self._add_visit_content(result, node, **kwargs)

        return result

    def _visit_list(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "ordered": node.ordered,
                "main_node": node.main_node,
                "start": node.start,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_paragraph(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "content": self.visitlist(node, node.content, **kwargs),
            }
        )

        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_paragraph_line(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_source_marker(self, node: Node, **kwargs) -> dict:
        return self._visit_value(node, **kwargs)

    def _visit_source_line(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "line_number": node.line_number,
                "line_content": node.line_content,
                "highlight_style": node.highlight_style,
                "marker": self.visit(node.marker, **kwargs),
            }
        )

        return result

    def _visit_source(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)
        result.update(
            {
                "language": node.language,
                "classes": node.classes,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_raw_line(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "value": node.value,
            }
        )

        return result

    def _visit_raw(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        result.update(
            {
                "classes": node.classes,
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result
