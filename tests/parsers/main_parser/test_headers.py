from unittest.mock import patch

from mau.environment.environment import Environment
from mau.lexers.main_lexer import MainLexer
from mau.nodes.header import HeaderNode
from mau.parsers.main_parser import MainParser, header_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.toc.hashlib.md5")
def test_default_header_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert header_anchor("Some Words 1234 56", "1") == "some-words-1234-56-XXYY"


@patch("mau.parsers.toc.hashlib.md5")
def test_default_header_anchor_function_multiple_spaces(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert (
        header_anchor("Some    Words     1234    56", "1") == "some-words-1234-56-XXYY"
    )


@patch("mau.parsers.toc.hashlib.md5")
def test_default_header_anchor_function_filter_characters(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert header_anchor("Some #Words @ 12!34 56", "1") == "some-words-1234-56-XXYY"


def test_custom_header_anchor_function():
    source = """
    = Title of the section
    """

    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXY"
    )

    assert runner(source, environment).nodes == [
        HeaderNode("Title of the section", "1", "XXXXXY")
    ]


def test_parse_header_level_1():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXY"
    )

    source = """
    = Title of the section
    """

    assert runner(source, environment).nodes == [
        HeaderNode("Title of the section", "1", "XXXXXY")
    ]


def test_parse_header_level_3():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    === Title of a subsection
    """

    assert runner(source, environment).nodes == [
        HeaderNode("Title of a subsection", "3", "XXXXXX")
    ]


def test_parse_collect_headers():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: f"{text}-XXXXXX"
    )

    source = """
    = Header 1
    == Header 1.1
    == Header 1.2
    = Header 2
    == Header 2.1
    === Header 2.1.1
    """

    parser = runner(source, environment)

    assert parser.nodes == [
        HeaderNode("Header 1", "1", "Header 1-XXXXXX"),
        HeaderNode("Header 1.1", "2", "Header 1.1-XXXXXX"),
        HeaderNode("Header 1.2", "2", "Header 1.2-XXXXXX"),
        HeaderNode("Header 2", "1", "Header 2-XXXXXX"),
        HeaderNode("Header 2.1", "2", "Header 2.1-XXXXXX"),
        HeaderNode("Header 2.1.1", "3", "Header 2.1.1-XXXXXX"),
    ]

    assert parser.toc_manager.headers == [
        HeaderNode("Header 1", "1", "Header 1-XXXXXX"),
        HeaderNode("Header 1.1", "2", "Header 1.1-XXXXXX"),
        HeaderNode("Header 1.2", "2", "Header 1.2-XXXXXX"),
        HeaderNode("Header 2", "1", "Header 2-XXXXXX"),
        HeaderNode("Header 2.1", "2", "Header 2.1-XXXXXX"),
        HeaderNode("Header 2.1.1", "3", "Header 2.1.1-XXXXXX"),
    ]


def test_attributes_header():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: f"{text}-XXXXXX"
    )

    source = """
    [arg1,key1=value1]
    = Header
    """

    assert runner(source, environment).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=["arg1"],
            kwargs={"key1": "value1"},
        ),
    ]


def test_header_attributes_can_overwrite_anchor():
    source = """
    [arg1, anchor=someheader, key1=value1]
    = Header
    """

    assert runner(source).nodes == [
        HeaderNode(
            value="Header",
            level="1",
            anchor="someheader",
            args=["arg1"],
            kwargs={"key1": "value1"},
        ),
    ]


def test_single_tag_header():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: f"{text}-XXXXXX"
    )

    source = """
    [arg1, #tag1, key1=value1]
    = Header
    """

    assert runner(source, environment).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=["arg1"],
            kwargs={"key1": "value1"},
            tags=["tag1"],
        ),
    ]


def test_():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: f"{text}-XXXXXX"
    )

    source = """
    [*type1]
    = Header
    """

    assert runner(source, environment).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=[],
            kwargs={},
            tags=[],
            subtype="type1",
        ),
    ]
