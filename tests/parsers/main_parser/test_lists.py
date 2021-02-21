from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_parse_list_with_one_item():
    source = """
    * This is a list with one element
    """

    expected = [
        {
            "type": "list",
            "ordered": False,
            "main_node": True,
            "items": [
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a list with one element",
                            }
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_parse_list_with_multiple_items():
    source = """
    * Item 1
    * Item 2
    """

    expected = [
        {
            "type": "list",
            "ordered": False,
            "main_node": True,
            "items": [
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 1",
                            }
                        ],
                    },
                },
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 2",
                            }
                        ],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_parse_list_with_multiple_levels():
    source = """
    * Item 1
    ** Item 1.1
    * Item 2
    """

    expected = [
        {
            "type": "list",
            "ordered": False,
            "main_node": True,
            "items": [
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 1",
                            },
                            {
                                "type": "list",
                                "ordered": False,
                                "main_node": False,
                                "items": [
                                    {
                                        "type": "list_item",
                                        "level": 2,
                                        "content": {
                                            "type": "sentence",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "value": "Item 1.1",
                                                }
                                            ],
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                },
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 2",
                            }
                        ],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_parse_numbered_list():
    source = """
    # Item 1
    ## Item 1.1
    # Item 2
    """

    expected = [
        {
            "type": "list",
            "ordered": True,
            "main_node": True,
            "items": [
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 1",
                            },
                            {
                                "type": "list",
                                "ordered": True,
                                "main_node": False,
                                "items": [
                                    {
                                        "type": "list_item",
                                        "level": 2,
                                        "content": {
                                            "type": "sentence",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "value": "Item 1.1",
                                                }
                                            ],
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                },
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 2",
                            }
                        ],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_parse_mixed_list():
    source = """
    * Item 1
    ## Item 1.1
    * Item 2
    """

    expected = [
        {
            "type": "list",
            "ordered": False,
            "main_node": True,
            "items": [
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 1",
                            },
                            {
                                "type": "list",
                                "ordered": True,
                                "main_node": False,
                                "items": [
                                    {
                                        "type": "list_item",
                                        "level": 2,
                                        "content": {
                                            "type": "sentence",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "value": "Item 1.1",
                                                }
                                            ],
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                },
                {
                    "type": "list_item",
                    "level": 1,
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "Item 2",
                            }
                        ],
                    },
                },
            ],
        }
    ]

    _test(source, expected)
