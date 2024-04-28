import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_block_attributes_args_and_kwargs():
    source = """
    [*subtype,arg1,key1=value1]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=["arg1"],
            kwargs={"key1": "value1"},
        )
    ]


def test_block_attributes_can_contain_variables():
    source = """
    :value1:42

    [*subtype,key1={value1}]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"key1": "42"},
        )
    ]


def test_parse_block_title_and_attributes():
    source = """
    .Just a title
    [*subtype, name1=value1, name2=value2]
    ----
    ----
    """

    parser = runner(source)

    assert parser.nodes == [
        BlockNode(
            subtype="subtype",
            classes=[],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"name1": "value1", "name2": "value2"},
        )
    ]

    block_node = parser.nodes[0]
    text_node = block_node.title.children[0]

    assert text_node.parent == block_node
    assert text_node.parent_position == "title"


def test_parse_block_title_and_attributes_are_reset():
    source = """
    .Just a title
    [*subtype1, name1=value1, name2=value2]
    ----
    ----

    [*subtype2]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype1",
            classes=[],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"name1": "value1", "name2": "value2"},
        ),
        BlockNode(
            subtype="subtype2",
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]


def test_block_classes_single_class():
    source = """
    [*subtype,classes=cls1]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            classes=["cls1"],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]


def test_block_classes_multiple_classes():
    source = """
    [*subtype,classes="cls1,cls2"]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            classes=["cls1", "cls2"],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]


def test_block_engine():
    source = """
    [*subtype,engine=someengine]
    ----
    ----
    """

    with pytest.raises(MauErrorException):
        runner(source)


@patch("mau.parsers.main_parser.header_anchor")
def test_block_default_engine_adds_headers_to_global_toc(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Global header

    [*someblock]
    ----
    = Block header
    ----
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Global header")]),
            level="1",
            anchor="XXYY",
        ),
        BlockNode(
            subtype="someblock",
            children=[
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Block header")]),
                    level="1",
                    anchor="XXYY",
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]

    assert par.toc_manager.headers == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Global header")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Block header")]),
            level="1",
            anchor="XXYY",
        ),
    ]


def test_command_defblock():
    source = """
    ::defblock:alias, *myblock, language=python, engine=source
    """

    par = runner(source)

    assert par.block_aliases["alias"] == {
        "subtype": "myblock",
        "mandatory_args": [],
        "defaults": {"language": "python", "engine": "source"},
    }


def test_define_block_in_environment():
    source = """
    """

    environment = Environment()
    environment.setvar(
        "mau.parser.block_definitions",
        {
            "alias": {
                "subtype": "type",
                "mandatory_args": ["arg1", "arg2"],
                "defaults": {"key1": "value1"},
            },
        },
    )

    par = runner(source, environment=environment)

    assert par.block_aliases["alias"] == {
        "subtype": "type",
        "mandatory_args": ["arg1", "arg2"],
        "defaults": {"key1": "value1"},
    }


def test_command_defblock_no_subtype():
    source = """
    ::defblock:alias, language=python, engine=source
    """

    par = runner(source)

    assert par.block_aliases["alias"] == {
        "subtype": None,
        "mandatory_args": [],
        "defaults": {"language": "python", "engine": "source"},
    }


def test_command_defblock_source():
    source = """
    """

    par = runner(source)

    assert par.block_aliases["source"] == {
        "subtype": None,
        "mandatory_args": ["language"],
        "defaults": {"language": "text", "engine": "source"},
    }


def test_command_defblock_source_can_be_overridden():
    source = """
    ::defblock:source, *source, language=python, engine=source
    """

    par = runner(source)

    assert par.block_aliases["source"] == {
        "subtype": "source",
        "mandatory_args": [],
        "defaults": {"language": "python", "engine": "source"},
    }


def test_command_defblock_no_args():
    source = """
    ::defblock:
    """

    with pytest.raises(MauErrorException):
        runner(source)


def test_block_definitions_are_used():
    source = """
    ::defblock:alias, *subtype, name1=value1, name2=value2

    [*alias]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"name1": "value1", "name2": "value2"},
        ),
    ]


def test_block_definitions_local_kwargs_overwrite_defined_ones():
    source = """
    ::defblock:alias, *subtype, name1=value1, name2=value2

    [*alias, name1=value99]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"name1": "value99", "name2": "value2"},
        ),
    ]


def test_block_definitions_local_args_are_used():
    # This is testing that local args are used even when
    # an alias is used. However, the test should fail as
    # blocks cannot have unnamed arguments.

    source = """
    ::defblock:alias, *subtype, name1=value1, name2=value2

    [*alias, attr1, name1=value99]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=["attr1"],
            kwargs={"name1": "value99", "name2": "value2"},
        ),
    ]


def test_block_definitions_unnamed_args_are_used_as_names():
    # This is testing that the unnamed args specified
    # in the block definition are used as names for the
    # unnamed arguments passed to the block.

    source = """
    ::defblock:alias, *subtype, attr1, attr2

    [*alias, value1, value2]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"attr1": "value1", "attr2": "value2"},
        ),
    ]


def test_block_definitions_unnamed_and_named_args():
    # This is testing that any named are specifid in
    # the block definition is included in the block
    # kwargs if not redefined.

    source = """
    ::defblock:alias, *subtype, attr1, attr2, attr3=value3

    [*alias, value1, value2]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"attr1": "value1", "attr2": "value2", "attr3": "value3"},
        ),
    ]


def test_block_definitions_no_values_for_unnamed_args():
    # This is testing that is there are unnamed args in
    # the block definiton they should be given values
    # when the block is created.

    source = """
    ::defblock:alias, *subtype, attr1, attr2, attr3=value3

    [*alias]
    ----
    ----
    """

    with pytest.raises(ValueError):
        runner(source)


def test_block_definitions_values_without_unnamed_args():
    # This is testing that values passed to the
    # block at creation time should match the parameters
    # specified in the block definition.

    source = """
    ::defblock:alias, *subtype, attr3=value3

    [*alias, value1, value2]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=["value1", "value2"],
            kwargs={"attr3": "value3"},
        ),
    ]


def test_block_definitions_named_override_unnamed():
    # This is testing that values passed to the
    # block at creation time should match the parameters
    # specified in the block definition.

    source = """
    ::defblock:alias, *subtype, arg1, key1=value1

    [*alias, value2, arg1=value1]
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="subtype",
            children=[],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=["value2"],
            kwargs={"arg1": "value1", "key1": "value1"},
        ),
    ]
