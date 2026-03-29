from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.document import DocumentNode
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.parsers.document_parser import DocumentParser, DocumentParserOutput
from mau.test_helpers import (
    compare_nodes,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_parse_discards_empty_lines():
    source = "\n\n\n\n"

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, [])


def test_parse_output():
    source = ""

    assert runner(source).output == DocumentParserOutput()


def test_parse_output_custom_content_container():
    source = "text"

    class CustomDocumentNode(DocumentNode):
        type = "custom-document"

    environment = Environment()
    environment["mau.parser.document_wrapper"] = CustomDocumentNode

    compare_nodes(
        runner(source, environment).output.document,
        CustomDocumentNode(
            content=[
                ParagraphNode(
                    content=[
                        ParagraphLineNode(
                            content=[
                                TextNode(
                                    "text",
                                    info=NodeInfo(context=generate_context(0, 0, 0, 4)),
                                )
                            ],
                            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(0, 0, 0, 4)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    )


def test_parenthood_document():
    source = """
    This is a paragraph.

    This is another paragraph.
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph.",
                                info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                    ),
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 20)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(3, 0, 3, 26)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(3, 0, 3, 26)),
                    ),
                ],
                info=NodeInfo(context=generate_context(3, 0, 3, 26)),
            ),
        ],
    )
