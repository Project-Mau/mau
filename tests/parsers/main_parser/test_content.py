from mau.lexers.main_lexer import MainLexer
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_include_content():
    source = """
    ["text", #tag1, key1=value1, key2=value2]
    << ctype1:/path/to/it,/another/path
    """

    assert runner(source).nodes == [
        ContentNode(
            uris=["/path/to/it", "/another/path"],
            content_type="ctype1",
            args=["text"],
            tags=["tag1"],
            kwargs={"key1": "value1", "key2": "value2"},
        )
    ]


def test_include_content_with_subtype():
    source = """
    [*subtype1]
    << ctype1:/path/to/it
    """

    assert runner(source).nodes == [
        ContentNode(
            uris=["/path/to/it"],
            content_type="ctype1",
            subtype="subtype1",
            args=[],
            tags=[],
            kwargs={},
        )
    ]


def test_include_image_with_only_path():
    source = """
    << image:/path/to/it.jpg
    """

    assert runner(source).nodes == [ContentImageNode("/path/to/it.jpg")]


def test_include_image_with_http():
    source = """
    << image:https:///some.domain/path/to/it.jpg
    """

    assert runner(source).nodes == [
        ContentImageNode("https:///some.domain/path/to/it.jpg")
    ]


def test_include_image_with_arguments():
    source = """
    ["alt text", #tag1, key1=value1, key2=value2, classes="class1,class2"]
    << image:/path/to/it.jpg,
    """

    assert runner(source).nodes == [
        ContentImageNode(
            "/path/to/it.jpg",
            args=[],
            tags=["tag1"],
            kwargs={"key1": "value1", "key2": "value2"},
            alt_text="alt text",
            classes=["class1", "class2"],
        )
    ]


def test_include_image_with_title():
    source = """
    . A nice caption
    << image:/path/to/it.jpg
    """

    assert runner(source).nodes == [
        ContentImageNode(
            "/path/to/it.jpg",
            title=SentenceNode(
                children=[
                    TextNode("A nice caption"),
                ]
            ),
        )
    ]


def test_include_image_with_subtype():
    source = """
    [*subtype1]
    << image:/path/to/it.jpg
    """

    assert runner(source).nodes == [
        ContentImageNode(
            "/path/to/it.jpg",
            subtype="subtype1",
        ),
    ]
