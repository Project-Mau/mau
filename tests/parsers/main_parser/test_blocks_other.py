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
            "type": "block",
            "blocktype": "admonition",
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
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {"class": "someclass", "icon": "someicon", "label": "somelabel"},
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
            "type": "block",
            "args": [],
            "blocktype": "quote",
            "classes": [],
            "engine": "default",
            "kwargs": {"attribution": "Star Wars, 1977"},
            "preprocessor": "none",
            "title": None,
            "secondary_content": [],
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


def test_parse_block_quote_attribution_in_secondary_content():
    source = """
    [quote]
    ----
    Learn about the Force, Luke.
    ----
    _Star Wars_, 1977
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "quote",
            "classes": [],
            "engine": "default",
            "kwargs": {"attribution": None},
            "preprocessor": "none",
            "title": None,
            "secondary_content": [
                {
                    "args": [],
                    "content": {
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
                    "type": "paragraph",
                },
            ],
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


# def test_parse_block_quote_attribution_in_secondary_content_supports_styles():
#     source = """
#     [quote,"_Star Wars_, 1977"]
#     ----
#     Learn about the Force, Luke.
#     ----
#     """

#     expected = [
#         {
#             "type": "quote",
#             "attribution": {
#                 "content": [
#                     {
#                         "content": {
#                             "content": [{"type": "text", "value": "Star Wars"}],
#                             "type": "sentence",
#                         },
#                         "type": "style",
#                         "value": "underscore",
#                     },
#                     {"type": "text", "value": ", 1977"},
#                 ],
#                 "type": "sentence",
#             },
#             "kwargs": {},
#             "content": [
#                 {
#                     "type": "paragraph",
#                     "args": [],
#                     "kwargs": {},
#                     "content": {
#                         "type": "sentence",
#                         "content": [
#                             {"type": "text", "value": "Learn about the Force, Luke."}
#                         ],
#                     },
#                 }
#             ],
#         }
#     ]

#     _test(source, expected)
