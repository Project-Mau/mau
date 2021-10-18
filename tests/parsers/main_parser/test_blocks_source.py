import pytest

from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_source():
    source = """
    [myblock, engine=source, language=somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_with_title():
    source = """
    . Title
    [myblock, engine=source, language=somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": {
                "content": [{"type": "text", "value": "Title"}],
                "type": "sentence",
            },
            "content": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_engine_source_without_language():
    source = """
    [myblock, engine=source]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "text",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_ignores_mau_syntax():
    source = """
    [myblock, engine=source]
    ----
    :answer:42
    The answer is {answer}
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "text",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": ":answer:42"},
                {"type": "text", "value": "The answer is {answer}"},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_respects_spaces_and_indentation():
    source = """
    [myblock, engine=source]
    ----
      //    This is a comment
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "text",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "  //    This is a comment"},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callouts():
    source = """
    [myblock, engine=source, language=somelang, callouts=":"]
    ----
    import sys
    import os:3:
    
    print(os.environ["HOME"]):6:
    ----
    3: This is an import
    6: Environment variables are paramount
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "3", 3: "6"},
                    "contents": {
                        "3": "This is an import",
                        "6": "Environment variables are paramount",
                    },
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callouts_possible_clash():
    source = """
    [myblock, engine=source, language=somelang, callouts=":"]
    ----
    import sys
    import: os:3:
    
    print(os.environ["HOME"]):6:
    ----
    3: This is an import
    6: Environment variables are paramount
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "3", 3: "6"},
                    "contents": {
                        "3": "This is an import",
                        "6": "Environment variables are paramount",
                    },
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import: os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callouts_default_delimiter():
    source = """
    [myblock, engine=source, language=somelang]
    ----
    import sys
    import os:3:
    
    print(os.environ["HOME"]):6:
    ----
    3: This is an import
    6: Environment variables are paramount
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "3", 3: "6"},
                    "contents": {
                        "3": "This is an import",
                        "6": "Environment variables are paramount",
                    },
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callouts_custom_delimiter():
    source = """
    [myblock, engine=source, language=somelang, callouts="|"]
    ----
    import sys
    import os|3|

    print(os.environ["HOME"])|6|
    ----
    3: This is an import
    6: Environment variables are paramount
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "3", 3: "6"},
                    "contents": {
                        "3": "This is an import",
                        "6": "Environment variables are paramount",
                    },
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callout_cannot_be_found():
    p = init_parser(
        dedent(
            """
            [myblock, engine=source, language=somelang, callouts="|"]
            ----
            import sys
            import os

            print(os.environ["HOME"])|6|
            ----
            3: This is an import
            6: Environment variables are paramount
            """
        )
    )

    with pytest.raises(ParserError):
        p.parse()


def test_source_callouts_non_numeric_labels():
    source = """
    [myblock, engine=source, language=somelang, callouts="|"]
    ----
    import sys
    import os|step1|
    
    print(os.environ["HOME"])|step2|
    ----
    step1: This is an import
    step2: Environment variables are paramount
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "step1", 3: "step2"},
                    "contents": {
                        "step1": "This is an import",
                        "step2": "Environment variables are paramount",
                    },
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_callout_wrong_format():
    p = init_parser(
        dedent(
            """
            [myblock, engine=source, language=somelang, callouts=":"]
            ----
            import sys
            import os:3:

            print(os.environ["HOME"]):6:
            ----
            3 This is an import
            6: Environment variables are paramount
            """
        )
    )

    with pytest.raises(ParserError):
        p.parse()


def test_source_callouts_without_definition():
    source = """
    [myblock, engine=source, language=somelang, callouts=":"]
    ----
    import sys
    import os:3:
    
    print(os.environ["HOME"]):6:
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "somelang",
                "callouts": {
                    "markers": {1: "3", 3: "6"},
                    "contents": {},
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_highlights():
    source = """
    [myblock, engine=source, language=somelang]
    ----
    import sys
    import os:@:
    
    print(os.environ["HOME"]):@:
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [1, 3],
                "language": "somelang",
                "callouts": {
                    "markers": {},
                    "contents": {},
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_source_highlights_custom_marker():
    source = """
    [myblock, engine=source, language=somelang, highlight="#"]
    ----
    import sys
    import os:#:
    
    print(os.environ["HOME"]):#:
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "myblock",
            "args": [],
            "kwargs": {
                "highlights": [1, 3],
                "language": "somelang",
                "callouts": {
                    "markers": {},
                    "contents": {},
                },
            },
            "secondary_content": [],
            "title": None,
            "content": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)


def test_engine_source_language_is_reset():
    source = """
    [source, python]
    ----
    ----

    [source]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "source",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "python",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
        {
            "type": "block",
            "blocktype": "source",
            "args": [],
            "kwargs": {
                "highlights": [],
                "language": "text",
                "callouts": {"markers": {}, "contents": {}},
            },
            "secondary_content": [],
            "title": None,
            "content": [],
            "classes": [],
            "engine": "source",
            "preprocessor": "none",
        },
    ]

    _test(source, expected)
