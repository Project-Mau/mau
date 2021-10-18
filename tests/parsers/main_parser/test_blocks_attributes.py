import pytest

from mau.parsers import nodes
from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser, EngineError

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_attributes_block():
    source = """
    [blocktype,myattr1=value1]
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"myattr1": "value1"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
                },
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


def test_attributes_can_contain_variables():
    source = """
    :value:42

    [blocktype,myattr1={value}]
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"myattr1": "42"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
                },
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


def test_parse_block_title_and_attributes():
    source = """
    .Just a title
    [blocktype, name1=value1, name2=value2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "blocktype",
            "content": [],
            "secondary_content": [],
            "title": {
                "content": [{"type": "text", "value": "Just a title"}],
                "type": "sentence",
            },
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {"name1": "value1", "name2": "value2"},
        },
    ]

    _test(source, expected)


def test_parse_block_title_and_attributes_are_reset():
    source = """
    .Just a title
    [blocktype1, name1=value1, name2=value2]
    ----
    ----

    [blocktype2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "blocktype1",
            "content": [],
            "secondary_content": [],
            "title": {
                "content": [{"type": "text", "value": "Just a title"}],
                "type": "sentence",
            },
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {"name1": "value1", "name2": "value2"},
        },
        {
            "type": "block",
            "blocktype": "blocktype2",
            "content": [],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_classes_single_class():
    source = """
    [blocktype,classes=cls1]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": ["cls1"],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_classes_multiple_classes():
    source = """
    [blocktype,classes="cls1,cls2"]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": ["cls1", "cls2"],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_engine():
    source = """
    [blocktype,engine=someengine]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "someengine",
            "title": None,
            "content": [],
        },
    ]

    with pytest.raises(EngineError):
        _test(source, expected)


def test_block_mau_has_no_external_variables():
    source = """
    :answer:42
    [block, engine=mau]
    ----
    The answer is {answer}.
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "block",
            "content": [{"type": "text", "value": "The answer is {answer}."}],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "mau",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_raw_engine():
    source = """
    [block, engine=raw]
    ----
    Raw content
    on multiple lines
    ----
    Secondary content
    on multiple lines too
    """

    expected = [
        {
            "type": "block",
            "blocktype": "block",
            "content": [
                {"type": "text", "value": "Raw content"},
                {"type": "text", "value": "on multiple lines"},
            ],
            "secondary_content": [
                {"type": "text", "value": "Secondary content"},
                {"type": "text", "value": "on multiple lines too"},
            ],
            "title": None,
            "classes": [],
            "engine": "raw",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_default_engine_adds_headers_to_global_toc():
    source = """
    = Global header

    [someblock]
    ----
    = Block header
    ----
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Global header",
            "level": 1,
            "anchor": "global-header",
        },
        {
            "args": [],
            "blocktype": "someblock",
            "content": [
                {
                    "anchor": "block-header",
                    "kwargs": {},
                    "level": 1,
                    "tags": [],
                    "type": "header",
                    "value": "Block header",
                },
            ],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "kwargs": {},
            "secondary_content": [],
            "title": None,
            "type": "block",
        },
    ]

    p = _test(source, expected)

    assert p.headers == [
        nodes.HeaderNode("Global header", 1, "global-header"),
        nodes.HeaderNode("Block header", 1, "block-header"),
    ]


def test_block_positive_condition_matches():
    source = """
    :render:yes

    [block, condition="if:render:yes"]
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "args": [],
            "blocktype": "block",
            "classes": [],
            "content": [
                {
                    "args": [],
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a paragraph.",
                            },
                        ],
                        "type": "sentence",
                    },
                    "kwargs": {},
                    "type": "paragraph",
                },
            ],
            "engine": "default",
            "preprocessor": "none",
            "kwargs": {},
            "secondary_content": [],
            "title": None,
            "type": "block",
        },
    ]

    _test(source, expected)


def test_block_positive_condition_doesnt_match():
    source = """
    :render:no

    [block, condition="if:render:yes"]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    _test(source, expected)


def test_block_negative_condition_matches():
    source = """
    :render:yes

    [block, condition="ifnot:render:no"]
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "args": [],
            "blocktype": "block",
            "classes": [],
            "content": [
                {
                    "args": [],
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a paragraph.",
                            },
                        ],
                        "type": "sentence",
                    },
                    "kwargs": {},
                    "type": "paragraph",
                },
            ],
            "engine": "default",
            "preprocessor": "none",
            "kwargs": {},
            "secondary_content": [],
            "title": None,
            "type": "block",
        },
    ]

    _test(source, expected)


def test_block_negative_condition_doesnt_match():
    source = """
    :render:no

    [block, condition="ifnot:render:no"]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    _test(source, expected)


def test_block_condition_accepts_booleans():
    source = """
    :render:

    [block, condition="ifnot:render:"]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    _test(source, expected)


def test_block_condition_raises_exception():
    source = """
    [block, condition="if:render"]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    with pytest.raises(ParserError):
        _test(source, expected)


def test_command_defblock():
    p = init_parser("::defblock:alias, myblock, language=python, engine=source")
    p.parse()

    assert p.block_aliases["alias"] == "myblock"
    assert p.block_defaults["myblock"] == {"language": "python", "engine": "source"}


def test_command_defblock_backward_compatible_source_can_be_overridden():
    p = init_parser("::defblock:source, source, language=python, engine=source")
    p.parse()

    assert p.block_aliases["source"] == "source"
    assert p.block_defaults["source"] == {"language": "python", "engine": "source"}


def test_command_defblock_no_args():
    p = init_parser("::defblock:")

    with pytest.raises(ParserError):
        p.parse()


def test_command_defblock_single_arg():
    p = init_parser("::defblock:source")

    with pytest.raises(ParserError):
        p.parse()


def test_block_definitions_are_used():
    source = """
    ::defblock:alias, blocktype, name1=value1, name2=value2

    [alias]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"name1": "value1", "name2": "value2"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_local_kwargs_overwrite_defined_ones():
    source = """
    ::defblock:alias, blocktype, name1=value1, name2=value2

    [alias, name1=value99]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"name1": "value99", "name2": "value2"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_local_args_are_used():
    source = """
    ::defblock:alias, blocktype, name1=value1, name2=value2

    [alias, attr1, name1=value99]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": ["attr1"],
            "blocktype": "blocktype",
            "kwargs": {"name1": "value99", "name2": "value2"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    with pytest.raises(ParserError):
        _test(source, expected)


def test_block_definitions_default_source_has_engine_source():
    source = """
    [source]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "source",
            "kwargs": {
                "callouts": {"contents": {}, "markers": {}},
                "highlights": [],
                "language": "text",
            },
            "secondary_content": [],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_default_source_language():
    source = """
    [source, python]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "source",
            "kwargs": {
                "callouts": {"contents": {}, "markers": {}},
                "highlights": [],
                "language": "python",
            },
            "secondary_content": [],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_unnamed_args_are_used_as_names():
    source = """
    ::defblock:alias, blocktype, attr1, attr2

    [alias, value1, value2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"attr1": "value1", "attr2": "value2"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_unnamed_and_named_args():
    source = """
    ::defblock:alias, blocktype, attr1, attr2, attr3=value3

    [alias, value1, value2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"attr1": "value1", "attr2": "value2", "attr3": "value3"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_definitions_no_values_for_unnamed_args():
    source = """
    ::defblock:alias, blocktype, attr1, attr2, attr3=value3

    [alias]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"attr3": "value3"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    with pytest.raises(ParserError):
        _test(source, expected)


def test_block_definitions_values_without_unnamed_args():
    source = """
    ::defblock:alias, blocktype, attr3=value3

    [alias, value1, value2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": ["value1", "value2"],
            "blocktype": "blocktype",
            "kwargs": {"attr3": "value3"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": None,
            "content": [],
        },
    ]

    with pytest.raises(ParserError):
        _test(source, expected)
