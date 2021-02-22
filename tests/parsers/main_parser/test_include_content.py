from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_include_image_with_only_path():
    source = """
    << image:/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": None,
            "title": None,
            "classes": None,
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_include_image_with_full_uri():
    source = """
    << image:/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": None,
            "title": None,
            "classes": None,
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_include_image_with_http():
    source = """
    << image:https:///some.domain/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "https:///some.domain/path/to/it.jpg",
            "alt_text": None,
            "title": None,
            "classes": None,
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_include_image_with_alt_text():
    source = """
    [alt_text="This is a beautiful image"]
    << image:/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": "This is a beautiful image",
            "title": None,
            "classes": None,
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_include_image_with_classes():
    source = """
    [classes="class1,class2"]
    << image:/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": None,
            "title": None,
            "classes": ["class1", "class2"],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_include_image_with_arguments():
    source = """
   [argument1=value1,argument2=value2]
   << image:/path/to/it.jpg
   """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": None,
            "title": None,
            "classes": None,
            "kwargs": {"argument1": "value1", "argument2": "value2"},
        },
    ]

    _test(source, expected)


def test_include_image_with_title():
    source = """
    . A nice caption
    << image:/path/to/it.jpg
    """

    expected = [
        {
            "type": "content_image",
            "uri": "/path/to/it.jpg",
            "alt_text": None,
            "title": {
                "content": [{"type": "text", "value": "A nice caption"}],
                "type": "sentence",
            },
            "classes": None,
            "kwargs": {},
        },
    ]

    _test(source, expected)
