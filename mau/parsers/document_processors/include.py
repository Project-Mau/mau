from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from dataclasses import dataclass, field

from mau.environment.environment import Environment
from mau.nodes.include import (
    INCLUDE_HELP,
    INCLUDE_IMAGE_HELP,
    INCLUDE_MAU_HELP,
    INCLUDE_RAW_HELP,
    BlockGroupNode,
    FootnotesNode,
    IncludeImageNode,
    IncludeMauNode,
    IncludeNode,
    IncludeRawNode,
    TocNode,
)
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.raw import RawLineNode
from mau.parsers.arguments_parser import (
    process_arguments_with_variables,
)
from mau.parsers.base_parser import create_parser_exception
from mau.text_buffer import Context
from mau.token import TokenType


@dataclass
class IncludeCall:
    # The URI of the includer file.
    caller_uri: str

    # The URI of the included file.
    callee_uri: str

    # The arguments passed to the call.
    # These are used to populate the
    # environment before the included file
    # is parsed.
    call_arguments: dict[str, str] = field(default_factory=dict)

    # This is the include node info,
    # that keeps trace of where this
    # inclusion happened.
    info: NodeInfo | None = None


def include_processor(parser: DocumentParser):
    # Parse content in the form
    #
    # << content_type:URI

    # Get the mandatory prefix.
    prefix = parser.tm.get_token(TokenType.INCLUDE)

    # Get the content type.
    content_type = parser.tm.get_token(TokenType.TEXT)

    # Find the final context.
    context = Context.merge_contexts(prefix.context, content_type.context)

    arguments: NodeArguments | None = parser.arguments_buffer.pop()

    if parser.tm.peek_token_is(TokenType.LITERAL, ":"):
        # In this case arguments are inline

        # Check if boxed arguments have been defined.
        # In that case we need to stop with an error.
        if arguments:
            raise create_parser_exception(
                "Syntax error. You cannot specify both boxed and inline arguments.",
                context,
                help_text=INCLUDE_HELP,
            )

        # Get the colon.
        parser.tm.get_token(TokenType.LITERAL, ":")

        # Get the inline arguments.
        arguments_token = parser.tm.get_token(TokenType.TEXT)

        arguments = process_arguments_with_variables(
            arguments_token, parser.message_handler, parser.environment
        ).arguments

    arguments = arguments or NodeArguments()

    node: IncludeImageNode | IncludeNode

    match content_type.value:
        case "image":
            node = _parse_image(parser, arguments, context)
        case "mau":
            node = _parse_mau(parser, arguments, context)
        case "raw":
            node = _parse_raw(parser, arguments, context)
        case "toc":
            node = _parse_toc(parser, arguments, context)
        case "footnotes":
            node = _parse_footnotes(parser, arguments, context)
        case "blockgroup":
            node = _parse_blockgroup(parser, arguments, context)
        case _:
            node = IncludeNode(content_type.value)

    # Build the node info.
    node.info = NodeInfo(context=context)
    node.arguments = NodeArguments(**arguments.asdict())

    # Extract labels from the buffer and
    # store them in the node data.
    parser.pop_labels(node)

    # Check the stored control
    if control := parser.control_buffer.pop():
        # If control is False, we need to stop
        # processing here and return without
        # saving any node.
        if not control.process(parser.environment):
            return True

    parser._save(node)

    return True


def _parse_image(
    parser: DocumentParser, arguments: NodeArguments, context: Context
) -> IncludeImageNode:
    arguments.set_names(["uri", "alt_text", "classes"])

    uri = arguments.named_args.pop("uri", None)

    if not uri:
        raise create_parser_exception(
            "Syntax error. You need to specify a URI.",
            context,
            help_text=INCLUDE_IMAGE_HELP,
        )

    alt_text = arguments.named_args.pop("alt_text", None)
    classes_arg = arguments.named_args.pop("classes", None)

    classes = []
    if classes_arg:
        classes.extend(classes_arg.split(","))

    content = IncludeImageNode(
        uri,
        alt_text,
        classes,
    )

    return content


def _parse_mau(
    parser: DocumentParser, arguments: NodeArguments, context: Context
) -> IncludeMauNode:
    arguments.set_names(["uri"])

    uri = arguments.named_args.pop("uri", None)
    pass_environment = arguments.named_args.pop("pass_environment", "true")

    if not uri:
        raise create_parser_exception(
            "Syntax error. You need to specify a URI.",
            context,
            help_text=INCLUDE_MAU_HELP,
        )

    # Add this very file to the list of forbidden
    # inclusions. It's 1984 and Farenheit 451
    # all together!
    # We check if the element is already there to
    # prevent double inclusion but still preserve
    # the order.
    if context.source not in parser.forbidden_includes:
        parser.forbidden_includes.append(context.source)

    # Make sure we are not trying to include a file that
    # included this file. It's called infinite recursion,
    # sweetheart.
    if uri in parser.forbidden_includes:
        raise create_parser_exception(
            f"To avoid recursion, you cannot include the following files: {parser.forbidden_includes}.",
            context,
        )

    # This is the dictionary of call arguments.
    call_arguments = {}

    # Get all keys that have to be passed to
    # the included file as environment variables.
    keys = [k for k in arguments.named_args if k.startswith("call:")]

    # Remove the prefix from all the call variables
    # and remove the original item from the include node.
    for key in keys:
        new_key = key.removeprefix("call:")
        call_arguments[new_key] = arguments.named_args.pop(key)

    # Add the included URI to the list of forbidden
    # inclusions. More censorship!
    # We check if the element is already there to
    # prevent double inclusion but still preserve
    # the order.
    if uri not in parser.forbidden_includes:
        parser.forbidden_includes.append(uri)

    # Open the given URI and read the text.
    try:
        with open(uri, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError as exc:
        raise create_parser_exception(
            f"File '{uri}' cannot be read.",
            context,
        ) from exc

    if pass_environment == "true":
        # The parsing environment is
        # that of the external parser.
        # We clone it because we need
        # to add the call variables.
        environment = Environment.from_environment(parser.environment)
    else:
        environment = Environment()

    # Update the environment with call variables.
    environment.dupdate(call_arguments)

    # Unpack the token initial position.
    start_line, start_column = context.start_position

    # Get the token source.
    source_filename = uri

    content_parser = parser.lex_and_parse(
        text=text,
        message_handler=parser.message_handler,
        environment=environment,
        start_line=0,
        start_column=0,
        source_filename=source_filename,
        forbidden_includes=parser.forbidden_includes,
    )

    # Add the include call to the parser output.
    # The key is (includer file, included file)
    parser.output.include_calls.append(
        IncludeCall(
            caller_uri=context.source,
            callee_uri=uri,
            call_arguments=call_arguments,
            info=NodeInfo(context=context),
        )
    )

    # Inherit all the calls made by the recursive
    # parser that processed the content to the
    # included file.
    parser.output.include_calls.extend(content_parser.output.include_calls)

    return IncludeMauNode(
        uri,
        content=content_parser.nodes,
    )


def _parse_raw(
    parser: DocumentParser, arguments: NodeArguments, context: Context
) -> IncludeRawNode:
    arguments.set_names(["uri"])

    uri = arguments.named_args.pop("uri", None)

    if not uri:
        raise create_parser_exception(
            "Syntax error. You need to specify a URI.",
            context,
        )

    # Open the given URI and read the text.
    try:
        with open(uri, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as exc:
        raise create_parser_exception(
            f"File '{uri}' cannot be read.",
            context,
            help_text=INCLUDE_RAW_HELP,
        ) from exc

    # A list of content lines (raw).
    content_lines = content.split("\n")

    # A list of raw content lines.
    raw_lines: list[RawLineNode] = []

    # Create the include node.
    node = IncludeRawNode(uri, info=NodeInfo(context=context))

    # Create a raw line for each line
    # in the included file.
    for content_line in content_lines:
        raw_lines.append(
            RawLineNode(
                content_line,
                info=NodeInfo(context=context),
                parent=node,
            )
        )

    # Assign the raw lines to the include node.
    node.content = raw_lines

    return node


def _parse_toc(
    parser: DocumentParser, arguments: NodeArguments, context: Context
) -> TocNode:
    toc_node = TocNode()

    parser.toc_manager.add_toc_node(toc_node)

    return toc_node


def _parse_footnotes(
    parser: DocumentParser, arguments: NodeArguments, context: Context
):
    footnotes_node = FootnotesNode()

    parser.footnotes_manager.add_footnotes_list(footnotes_node)

    return footnotes_node


def _parse_blockgroup(
    parser: DocumentParser, arguments: NodeArguments, context: Context
):
    arguments.set_names(["group"])

    group_name = arguments.named_args.pop("group")

    blockgroup_node = BlockGroupNode(group_name)

    parser.blockgroup_manager.add_group(blockgroup_node)

    return blockgroup_node
