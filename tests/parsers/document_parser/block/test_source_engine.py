from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.source import (
    SourceLineNode,
    SourceMarkerNode,
    SourceNode,
)
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_source_engine_empty_block():
    source = """
    [engine=source]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                classes=[],
                info=NodeInfo(context=generate_context(2, 0, 3, 4)),
            ),
        ],
    )


def test_source_engine_empty_block_language():
    source = """
    [python, engine=source]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                classes=[],
                arguments=NodeArguments(
                    unnamed_args=["python"],
                ),
                info=NodeInfo(context=generate_context(2, 0, 3, 4)),
            ),
        ],
    )


def test_source_engine_contains_mau_code():
    source = """
    [engine=source]
    ----
    // A comment
    @@@@
    A block
    @@@@
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="// A comment",
                        info=NodeInfo(context=generate_context(3, 0, 3, 12)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="@@@@",
                        info=NodeInfo(context=generate_context(4, 0, 4, 4)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="A block",
                        info=NodeInfo(context=generate_context(5, 0, 5, 7)),
                    ),
                    SourceLineNode(
                        line_number="4",
                        line_content="@@@@",
                        info=NodeInfo(context=generate_context(6, 0, 6, 4)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 7, 4)),
            )
        ],
    )


def test_source_engine_with_code():
    source = """
    [python, engine=source]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "python",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import os",
                        info=NodeInfo(context=generate_context(3, 0, 3, 9)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="",
                        info=NodeInfo(context=generate_context(4, 0, 4, 0)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content='print(os.environ["HOME"])',
                        info=NodeInfo(context=generate_context(5, 0, 5, 25)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 6, 4)),
            ),
        ],
    )


def test_source_engine_ignores_mau_syntax():
    source = """
    [engine=source]
    ----
    :answer:42
    The answer is {answer}
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content=":answer:42",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="The answer is {answer}",
                        info=NodeInfo(context=generate_context(4, 0, 4, 22)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 5, 4)),
            ),
        ],
    )


def test_source_engine_respects_spaces_and_indentation():
    source = """
    [engine=source]
    ----
      //    This is a comment
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="  //    This is a comment",
                        info=NodeInfo(context=generate_context(3, 0, 3, 25)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 4, 4)),
            ),
        ],
    )


def test_source_engine_callouts_default_delimiter():
    source = """
    [engine=source]
    ----
    import sys
    import os:mark1:
    import enum:mark2:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import sys",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="import os",
                        marker=SourceMarkerNode(
                            "mark1",
                            info=NodeInfo(context=generate_context(4, 9, 4, 16)),
                        ),
                        info=NodeInfo(context=generate_context(4, 0, 4, 9)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="import enum",
                        marker=SourceMarkerNode(
                            "mark2",
                            info=NodeInfo(context=generate_context(5, 11, 5, 18)),
                        ),
                        info=NodeInfo(context=generate_context(5, 0, 5, 11)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 6, 4)),
            ),
        ],
    )


def test_source_engine_callouts_potential_clash():
    source = """
    [engine=source]
    ----
    import: os:mark1:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import: os",
                        marker=SourceMarkerNode(
                            "mark1",
                            info=NodeInfo(context=generate_context(3, 10, 3, 17)),
                        ),
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 4, 4)),
            ),
        ],
    )


def test_source_engine_callouts_one_single_marker_is_skipped():
    source = """
    [engine=source]
    ----
    import:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import:",
                        info=NodeInfo(context=generate_context(3, 0, 3, 7)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 4, 4)),
            ),
        ],
    )


def test_source_engine_marker_custom_delimiter():
    source = """
    [engine=source, marker_delimiter="|"]
    ----
    import sys
    import os:mark1:
    import enum|mark2|
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import sys",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="import os:mark1:",
                        info=NodeInfo(context=generate_context(4, 0, 4, 16)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="import enum",
                        marker=SourceMarkerNode(
                            "mark2",
                            info=NodeInfo(context=generate_context(5, 11, 5, 18)),
                        ),
                        info=NodeInfo(context=generate_context(5, 0, 5, 11)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 6, 4)),
            ),
        ],
    )


def test_source_engine_highlight_marker_with_default_style():
    source = """
    [engine=source]
    ----
    import sys
    import os:@:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import sys",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="import os",
                        highlight_style="default",
                        info=NodeInfo(context=generate_context(4, 0, 4, 12)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 5, 4)),
            ),
        ],
    )


def test_source_engine_highlight_custom_marker():
    source = """
    [engine=source, highlight_marker="#"]
    ----
    import sys
    import os:#:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import sys",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="import os",
                        highlight_style="default",
                        info=NodeInfo(context=generate_context(4, 0, 4, 12)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 5, 4)),
            ),
        ],
    )


def test_source_engine_highlight_marker_change_default_highlight_style():
    source = """
    [engine=source, highlight_default_style="another"]
    ----
    import sys
    import os:@:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="import sys",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="import os",
                        highlight_style="another",
                        info=NodeInfo(context=generate_context(4, 0, 4, 12)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 5, 4)),
            ),
        ],
    )


def test_source_engine_highlight_marker_use_default_aliases():
    source = """
    [engine=source]
    ----
    default:@:
    add:@+:
    remove:@-:
    important:@!:
    error:@x:
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="default",
                        highlight_style="default",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="add",
                        highlight_style="add",
                        info=NodeInfo(context=generate_context(4, 0, 4, 7)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="remove",
                        highlight_style="remove",
                        info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                    ),
                    SourceLineNode(
                        line_number="4",
                        line_content="important",
                        highlight_style="important",
                        info=NodeInfo(context=generate_context(6, 0, 6, 13)),
                    ),
                    SourceLineNode(
                        line_number="5",
                        line_content="error",
                        highlight_style="error",
                        info=NodeInfo(context=generate_context(7, 0, 7, 9)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 8, 4)),
            ),
        ],
    )


def test_source_engine_highlight_marker_can_define_new_aliases():
    environment = Environment.from_dict(
        {
            "mau.parser": {
                "source_highlight_style_aliases": {
                    "*": "special",
                },
            }
        }
    )

    source = """
    [engine=source]
    ----
    default:@:
    add:@+:
    remove:@-:
    important:@!:
    error:@x:
    special:@*:
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="default",
                        highlight_style="default",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="add",
                        highlight_style="add",
                        info=NodeInfo(context=generate_context(4, 0, 4, 7)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="remove",
                        highlight_style="remove",
                        info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                    ),
                    SourceLineNode(
                        line_number="4",
                        line_content="important",
                        highlight_style="important",
                        info=NodeInfo(context=generate_context(6, 0, 6, 13)),
                    ),
                    SourceLineNode(
                        line_number="5",
                        line_content="error",
                        highlight_style="error",
                        info=NodeInfo(context=generate_context(7, 0, 7, 9)),
                    ),
                    SourceLineNode(
                        line_number="6",
                        line_content="special",
                        highlight_style="special",
                        info=NodeInfo(context=generate_context(8, 0, 8, 11)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 9, 4)),
            ),
        ],
    )


def test_source_engine_highlight_marker_can_override_default_aliases():
    environment = Environment.from_dict(
        {
            "mau.parser": {
                "source_highlight_style_aliases": {
                    "+": "addition",
                },
            }
        }
    )

    source = """
    [engine=source]
    ----
    default:@:
    addition:@+:
    remove:@-:
    important:@!:
    error:@x:
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            SourceNode(
                "text",
                classes=[],
                content=[
                    SourceLineNode(
                        line_number="1",
                        line_content="default",
                        highlight_style="default",
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                    SourceLineNode(
                        line_number="2",
                        line_content="addition",
                        highlight_style="addition",
                        info=NodeInfo(context=generate_context(4, 0, 4, 12)),
                    ),
                    SourceLineNode(
                        line_number="3",
                        line_content="remove",
                        highlight_style="remove",
                        info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                    ),
                    SourceLineNode(
                        line_number="4",
                        line_content="important",
                        highlight_style="important",
                        info=NodeInfo(context=generate_context(6, 0, 6, 13)),
                    ),
                    SourceLineNode(
                        line_number="5",
                        line_content="error",
                        highlight_style="error",
                        info=NodeInfo(context=generate_context(7, 0, 7, 9)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 8, 4)),
            ),
        ],
    )


def test_source_parenthood():
    source = """
    [python, engine=source]
    ----
    import os
    ----
    """

    parser = runner(source)

    document_node = parser.output.document

    source_node = parser.nodes[0]

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # All nodes inside the block must be
    # children of the block.
    check_parent(source_node, source_node.content)


def test_source_parenthood_labels():
    source = """
    . A label
    .role Another label
    [engine=source]
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    source_node = parser.nodes[0]
    label_title = source_node.labels["title"]
    label_role = source_node.labels["role"]

    # Each label must be a child of the
    # source it has been assigned to.
    check_parent(source_node, [label_title])
    check_parent(label_title, label_title.content)
    check_parent(source_node, [label_role])
    check_parent(label_role, label_role.content)
