import textwrap
from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ParagraphNode
from mau.parsers.main_parser import MainParser, footnote_anchor, reference_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.main_parser.hashlib.md5")
def test_default_footnote_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYYXXYYZZZ"

    assert footnote_anchor("Some Words 1234 56") == "XXYYXXYY"


@patch("mau.parsers.main_parser.hashlib.md5")
def test_default_reference_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYYXXYYZZZ"

    assert reference_anchor("Some Words 1234 56") == "XXYYXXYY"


def test_footnote_empty_block():
    source = """
    [footnote, note1]
    ----
    ----
    """

    parser = init_parser(textwrap.dedent(source))
    parser.footnotes = {
        "note1": FootnoteNode(number=1),
        "note2": FootnoteNode(number=2),
    }
    parser.parse()

    assert parser.nodes == []


@patch("mau.parsers.main_parser.footnote_anchor")
def test_footnote_content(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    [footnote, note2]
    ----
    This is another paragraph.
    ----

    [footnote, note1]
    ----
    This is a paragraph.
    ----
    """

    parser = init_parser(textwrap.dedent(source))
    parser.footnotes = {
        "note1": FootnoteNode(number=1),
        "note2": FootnoteNode(number=2),
    }
    parser.parse()
    parser.create_footnotes()

    assert parser.nodes == []
    assert parser.footnotes == {
        "note1": FootnoteNode(
            number=1,
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is a paragraph."),
                        ]
                    )
                ),
            ],
            reference_anchor="fr-XXYY-1",
            content_anchor="fd-XXYY-1",
        ),
        "note2": FootnoteNode(
            number=2,
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is another paragraph."),
                        ]
                    )
                ),
            ],
            reference_anchor="fr-XXYY-2",
            content_anchor="fd-XXYY-2",
        ),
    }
