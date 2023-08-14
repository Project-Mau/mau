from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.page import HeaderNode
from mau.parsers.environment import Environment
from mau.parsers.main_parser import MainParser, header_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.main_parser.hashlib.md5")
def test_default_header_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert header_anchor("Some Words 1234 56", "1") == "some-words-1234-56-XXYY"


@patch("mau.parsers.main_parser.hashlib.md5")
def test_default_header_anchor_function_multiple_spaces(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert (
        header_anchor("Some    Words     1234    56", "1") == "some-words-1234-56-XXYY"
    )


@patch("mau.parsers.main_parser.hashlib.md5")
def test_default_header_anchor_function_filter_characters(mock_md5):
    mock_md5().hexdigest.return_value = "XXYY"

    assert header_anchor("Some #Words @ 12!34 56", "1") == "some-words-1234-56-XXYY"


def test_custom_header_anchor_function():
    source = """
    = Title of the section
    """

    config = {"header_anchor_function": lambda text, level: "XXXXXY"}
    env_runner = parser_runner_factory(
        MainLexer, MainParser, environment=Environment(config, "mau")
    )

    assert env_runner(source).nodes == [
        HeaderNode("Title of the section", "1", "XXXXXY")
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_level_1(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    = Title of the section
    """

    assert runner(source).nodes == [HeaderNode("Title of the section", "1", "XXXXXX")]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_level_3(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    === Title of a subsection
    """

    assert runner(source).nodes == [HeaderNode("Title of a subsection", "3", "XXXXXX")]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_collect_headers(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    = Header 1
    == Header 1.1
    == Header 1.2
    = Header 2
    == Header 2.1
    === Header 2.1.1
    """

    parser = runner(source)

    assert parser.nodes == [
        HeaderNode("Header 1", "1", "Header 1-XXXXXX"),
        HeaderNode("Header 1.1", "2", "Header 1.1-XXXXXX"),
        HeaderNode("Header 1.2", "2", "Header 1.2-XXXXXX"),
        HeaderNode("Header 2", "1", "Header 2-XXXXXX"),
        HeaderNode("Header 2.1", "2", "Header 2.1-XXXXXX"),
        HeaderNode("Header 2.1.1", "3", "Header 2.1.1-XXXXXX"),
    ]

    assert parser.headers == [
        HeaderNode("Header 1", "1", "Header 1-XXXXXX"),
        HeaderNode("Header 1.1", "2", "Header 1.1-XXXXXX"),
        HeaderNode("Header 1.2", "2", "Header 1.2-XXXXXX"),
        HeaderNode("Header 2", "1", "Header 2-XXXXXX"),
        HeaderNode("Header 2.1", "2", "Header 2.1-XXXXXX"),
        HeaderNode("Header 2.1.1", "3", "Header 2.1.1-XXXXXX"),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_attributes_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [value1,someattr1=somevalue1,someattr2=somevalue2]
    = Header
    """

    assert runner(source).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=["value1"],
            kwargs={"someattr1": "somevalue1", "someattr2": "somevalue2"},
        ),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_single_tag_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [value1, #tag1, value2,someattr1=somevalue1,someattr2=somevalue2]
    = Header
    """

    assert runner(source).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=["value1", "value2"],
            kwargs={"someattr1": "somevalue1", "someattr2": "somevalue2"},
            tags=["tag1"],
        ),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_multiple_tags_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [value1, #tag1, value2,#tag2,someattr1=somevalue1,someattr2=somevalue2]
    = Header
    """

    assert runner(source).nodes == [
        HeaderNode(
            "Header",
            "1",
            "Header-XXXXXX",
            args=["value1", "value2"],
            kwargs={"someattr1": "somevalue1", "someattr2": "somevalue2"},
            tags=["tag1", "tag2"],
        ),
    ]
