from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ContentImageNode, ContentNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_include_standard_content():
    source = """
    << somecontent:attr1,attr2,#atag,attr3=value3
    """

    assert runner(source).nodes == [
        ContentNode(
            "somecontent",
            args=["attr1", "attr2"],
            tags=["atag"],
            kwargs={"attr3": "value3"},
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


def test_include_image_with_alt_text():
    source = """
    << image:/path/to/it.jpg,alt_text="This is a beautiful image"
    """

    assert runner(source).nodes == [
        ContentImageNode("/path/to/it.jpg", alt_text="This is a beautiful image")
    ]


def test_include_image_with_classes():
    source = """
    << image:/path/to/it.jpg,classes="class1,class2"
    """

    assert runner(source).nodes == [
        ContentImageNode("/path/to/it.jpg", classes=["class1", "class2"])
    ]


def test_include_image_with_arguments():
    source = """
   << image:/path/to/it.jpg,"alternate text", argument1=value1,argument2=value2
   """

    assert runner(source).nodes == [
        ContentImageNode(
            "/path/to/it.jpg",
            args=[],
            kwargs={"argument1": "value1", "argument2": "value2"},
            alt_text="alternate text",
        )
    ]


def test_include_image_with_tags():
    source = """
   << image:/path/to/it.jpg,"alternate text", #tag1, #tag2, argument1=value1,argument2=value2
   """

    assert runner(source).nodes == [
        ContentImageNode(
            "/path/to/it.jpg",
            args=[],
            tags=["tag1", "tag2"],
            kwargs={"argument1": "value1", "argument2": "value2"},
            alt_text="alternate text",
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
                [
                    TextNode("A nice caption"),
                ]
            ),
        )
    ]
