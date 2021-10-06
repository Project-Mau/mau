from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_admonition():
    source = """
    [admonition,someclass,someicon,somelabel]
    ----
    Content
    ----
    """

    expected = [
        {
            "type": "admonition",
            "class": "someclass",
            "icon": "someicon",
            "label": "somelabel",
            "kwargs": {},
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [{"type": "text", "value": "Content"}],
                        "type": "sentence",
                    },
                }
            ],
        },
    ]

    _test(source, expected)


def test_admonition_ignores_title():
    source = """
            . Title
            [admonition,someclass,someicon,somelabel]
            ----
            Content
            ----
            """

    expected = [
        {
            "type": "admonition",
            "class": "someclass",
            "icon": "someicon",
            "label": "somelabel",
            "kwargs": {},
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [{"type": "text", "value": "Content"}],
                        "type": "sentence",
                    },
                }
            ],
        },
    ]

    _test(source, expected)


def test_parse_block_quote():
    source = """
    [quote,"Star Wars, 1977"]
    ----
    Learn about the Force, Luke.
    ----
    """

    expected = [
        {
            "type": "quote",
            "attribution": {
                "content": [{"type": "text", "value": "Star Wars, 1977"}],
                "type": "sentence",
            },
            "kwargs": {},
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "Learn about the Force, Luke."}
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_parse_block_quote_ignores_title():
    source = """
    . Title
    [quote,"Star Wars, 1977"]
    ----
    Learn about the Force, Luke.
    ----
    """

    expected = [
        {
            "type": "quote",
            "attribution": {
                "content": [{"type": "text", "value": "Star Wars, 1977"}],
                "type": "sentence",
            },
            "kwargs": {},
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "Learn about the Force, Luke."}
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_parse_block_quote_attribution_supports_styles():
    source = """
    [quote,"_Star Wars_, 1977"]
    ----
    Learn about the Force, Luke.
    ----
    """

    expected = [
        {
            "type": "quote",
            "attribution": {
                "content": [
                    {
                        "content": {
                            "content": [{"type": "text", "value": "Star Wars"}],
                            "type": "sentence",
                        },
                        "type": "style",
                        "value": "underscore",
                    },
                    {"type": "text", "value": ", 1977"},
                ],
                "type": "sentence",
            },
            "kwargs": {},
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "Learn about the Force, Luke."}
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)
