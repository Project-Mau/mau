import pytest

from mau.parsers.main_parser import MainParser, ParseError

from tests.helpers import init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_source():
    source = """
    [source,somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_with_title():
    source = """
    . Title
    [source,somelang]
    ----
    import os

    print(os.environ["HOME"])
    ----
    """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": {
                "content": [{"type": "text", "value": "Title"}],
                "type": "sentence",
            },
            "code": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_without_language():
    source = """
            [source]
            ----
            import os

            print(os.environ["HOME"])
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "text",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_ignores_mau_syntax():
    source = """
            [source]
            ----
            :answer:42
            The answer is {answer}
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "text",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": ":answer:42"},
                {"type": "text", "value": "The answer is {answer}"},
            ],
        },
    ]

    _test(source, expected)


def test_source_respects_spaces():
    source = """
            [source]
            ----
            // This is a comment
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "text",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "// This is a comment"},
            ],
        },
    ]

    _test(source, expected)


def test_source_respects_indentation():
    source = """
            [source]
            ----
            * This is not indented
               ** This is indented
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "text",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "* This is not indented"},
                {"type": "text", "value": "   ** This is indented"},
            ],
        },
    ]

    _test(source, expected)


def test_source_named_language():
    source = """
            [source,language=somelang]
            ----
            import os

            print(os.environ["HOME"])
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_named_language_wins():
    source = """
            [source,text,language=somelang]
            ----
            import os

            print(os.environ["HOME"])
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {"markers": {}, "contents": {}},
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_callouts():
    source = """
            [source,somelang,callouts=":"]
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
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "3", 3: "6"},
                "contents": {
                    "3": "This is an import",
                    "6": "Environment variables are paramount",
                },
            },
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_callouts_possible_clash():
    source = """
            [source,somelang,callouts=":"]
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
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "3", 3: "6"},
                "contents": {
                    "3": "This is an import",
                    "6": "Environment variables are paramount",
                },
            },
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import: os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)
    _test(source, expected)


def test_source_callouts_default_delimiter():
    source = """
            [source,somelang]
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
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "3", 3: "6"},
                "contents": {
                    "3": "This is an import",
                    "6": "Environment variables are paramount",
                },
            },
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_callouts_custom_delimiter():
    source = """
            [source,somelang,callouts="|"]
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
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "3", 3: "6"},
                "contents": {
                    "3": "This is an import",
                    "6": "Environment variables are paramount",
                },
            },
            "highlights": [],
            "delimiter": "|",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_callout_cannot_be_found():
    p = init_parser(
        dedent(
            """
            [source,somelang,callouts="|"]
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

    with pytest.raises(ParseError):
        p.parse()


def test_source_callouts_non_numeric_labels():
    source = """
            [source,somelang,callouts="|"]
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
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "step1", 3: "step2"},
                "contents": {
                    "step1": "This is an import",
                    "step2": "Environment variables are paramount",
                },
            },
            "highlights": [],
            "delimiter": "|",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_callout_wrong_format():
    p = init_parser(
        dedent(
            """
            [source,somelang,callouts=":"]
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

    with pytest.raises(ParseError):
        p.parse()


def test_source_callouts_without_definition():
    source = """
            [source,somelang]
            ----
            import sys
            import os:3:

            print(os.environ["HOME"]):6:
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {1: "3", 3: "6"},
                "contents": {},
            },
            "highlights": [],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_highlights():
    source = """
            [source,somelang]
            ----
            import sys
            import os:@:

            print(os.environ["HOME"]):@:
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {},
                "contents": {},
            },
            "highlights": [1, 3],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)


def test_source_highlights_custom_marker():
    source = """
            [source,somelang,highlight=#]
            ----
            import sys:#:
            import os

            print(os.environ["HOME"]):#:
            ----
            """

    expected = [
        {
            "type": "source",
            "language": "somelang",
            "callouts": {
                "markers": {},
                "contents": {},
            },
            "highlights": [0, 3],
            "delimiter": ":",
            "kwargs": {},
            "title": None,
            "code": [
                {"type": "text", "value": "import sys"},
                {"type": "text", "value": "import os"},
                {"type": "text", "value": ""},
                {"type": "text", "value": 'print(os.environ["HOME"])'},
            ],
        },
    ]

    _test(source, expected)
