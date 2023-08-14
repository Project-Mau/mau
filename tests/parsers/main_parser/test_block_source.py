import pytest
from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

# from mau.parsers.base_parser import ParserError


init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_source_empty_block():
    source = """
    [source]
    ----
    ----
    """

    assert runner(source).nodes == [
        SourceNode(blocktype="default", code=[]),
    ]


def test_source_language():
    source = """
    [source, python]
    ----
    ----
    """

    assert runner(source).nodes == [
        SourceNode(code=[], language="python"),
    ]


def test_source_contains_mau():
    source = """
    [source, callouts="|"]
    ----
    // A comment
    ::toc:
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            code=[
                TextNode("// A comment"),
                TextNode("::toc:"),
            ],
        ),
    ]


def test_source_removes_escape_from_directive_like_text():
    source = r"""
    [source]
    ----
    \::#looks like a directive
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            code=[
                TextNode("::#looks like a directive"),
            ],
        ),
    ]


def test_source_with_code():
    source = """
    [source]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            code=[
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
        ),
    ]


def test_source_explicit_engine():
    source = """
    [myblock, engine=source, language=somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            blocktype="myblock",
            language="somelang",
            code=[
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
        ),
    ]


def test_source_with_title():
    source = """
    . Title
    [source, somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            title=SentenceNode([TextNode("Title")]),
        ),
    ]


def test_source_ignores_mau_syntax():
    source = """
    [source]
    ----
    :answer:42
    The answer is {answer}
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            code=[
                TextNode(":answer:42"),
                TextNode("The answer is {answer}"),
            ],
        ),
    ]


def test_source_respects_spaces_and_indentation():
    source = """
    [source]
    ----
      //    This is a comment
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            code=[
                TextNode("  //    This is a comment"),
            ],
        ),
    ]


def test_source_callouts():
    source = """
    [source, somelang, callouts=":"]
    ----
    import sys
    import os:imp:

    print(os.environ["HOME"]):env:
    ----
    imp: This is an import
    env: Environment variables are paramount
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import sys"),
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            markers=[CalloutNode(1, "imp"), CalloutNode(3, "env")],
            callouts=[
                CalloutsEntryNode("imp", "This is an import"),
                CalloutsEntryNode("env", "Environment variables are paramount"),
            ],
        ),
    ]


def test_source_callouts_possible_clash():
    source = """
    [source, somelang, callouts=":"]
    ----
    import sys
    import: os:imp:

    print(os.environ["HOME"]):env:
    ----
    imp: This is an import
    env: Environment variables are paramount
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import sys"),
                TextNode("import: os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            markers=[CalloutNode(1, "imp"), CalloutNode(3, "env")],
            callouts=[
                CalloutsEntryNode("imp", "This is an import"),
                CalloutsEntryNode("env", "Environment variables are paramount"),
            ],
        ),
    ]


def test_source_callouts_one_single_marker_is_skipped():
    source = """
    [source, somelang, callouts=":"]
    ----
    def something:
        print("AAA")
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("def something:"),
                TextNode('    print("AAA")'),
            ],
            markers=[],
            callouts=[],
        ),
    ]


def test_source_callouts_custom_delimiter():
    source = """
    [source, language=somelang, callouts="|"]
    ----
    import sys
    import os|imp|

    print(os.environ["HOME"])|env|
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import sys"),
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            markers=[CalloutNode(1, "imp"), CalloutNode(3, "env")],
        ),
    ]


def test_source_callout_wrong_format():
    # This is testing that all callouts in the secondary
    # content have the right format "label: content"

    source = """
    [myblock, engine=source, language=somelang, callouts=":"]
    ----
    import sys
    import os:3:

    print(os.environ["HOME"]):6:
    ----
    3 This is an import
    6: Environment variables are paramount
    """

    with pytest.raises(ParserError):
        runner(source)


def test_source_highlights():
    source = """
    [source, language=somelang]
    ----
    import sys
    import os:@:

    print(os.environ["HOME"]):@:
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import sys"),
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            highlights=[1, 3],
        ),
    ]


def test_source_highlights_custom_marker():
    source = """
    [source, language=somelang, highlight="#"]
    ----
    import sys
    import os:#:

    print(os.environ["HOME"]):#:
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="somelang",
            code=[
                TextNode("import sys"),
                TextNode("import os"),
                TextNode(""),
                TextNode('print(os.environ["HOME"])'),
            ],
            highlights=[1, 3],
        ),
    ]


def test_engine_source_language_is_reset():
    source = """
    [source, python]
    ----
    ----

    [source]
    ----
    ----
    """

    assert runner(source).nodes == [
        SourceNode(
            language="python",
            code=[],
        ),
        SourceNode(
            language="text",
            code=[],
        ),
    ]
