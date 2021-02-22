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
            "attribution": "Star Wars, 1977",
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
            "attribution": "Star Wars, 1977",
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


def test_conditional_block():
    source = """
    :render:yes
    [if,render,yes]
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "content": [
                    {
                        "type": "text",
                        "value": "This is a paragraph.",
                    },
                ],
                "type": "sentence",
            },
        },
    ]

    _test(source, expected)


def test_conditional_block_negative():
    source = """
    :render:no
    [if,render,yes]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    _test(source, expected)


def test_conditional_block_boolean():
    source = """
    :render:
    [if,render]
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "content": [
                    {
                        "type": "text",
                        "value": "This is a paragraph.",
                    },
                ],
                "type": "sentence",
            },
        },
    ]

    _test(source, expected)


def test_conditional_block_boolean_negative():
    source = """
    :!render:
    [if,render]
    ----
    This is a paragraph.
    ----
    """

    expected = []

    _test(source, expected)


def test_negative_conditional_block():
    source = """
    :!render:
    [ifnot,render]
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "content": [
                    {
                        "type": "text",
                        "value": "This is a paragraph.",
                    },
                ],
                "type": "sentence",
            },
        },
    ]

    _test(source, expected)


def test_raw_block():
    source = """
    [raw]
    ----
    <div class="someclass">
      <p>This is HTML</>
    </div>
    ----
    """

    expected = [
        {
            "type": "raw",
            "args": [],
            "kwargs": {},
            "content": [
                {"type": "text", "value": '<div class="someclass">'},
                {"type": "text", "value": "  <p>This is HTML</>"},
                {"type": "text", "value": "</div>"},
            ],
        },
    ]

    _test(source, expected)
