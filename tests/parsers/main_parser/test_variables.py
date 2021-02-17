from mau.parsers.main_parser import MainParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_parse_variable_definition_without_value_is_loaded_as_boolean():
    p = init_parser(":attr:")
    p.parse()

    assert listasdict(p.nodes) == []
    assert p.variables == {"attr": True}


def test_parse_variable_definition_without_value_can_be_negated():
    p = init_parser(":!attr:")
    p.parse()

    assert listasdict(p.nodes) == []
    assert p.variables == {"attr": False}


def test_parse_variable_definition_with_value_is_loaded():
    p = init_parser(":attr:42")
    p.parse()

    assert listasdict(p.nodes) == []
    assert p.variables == {"attr": "42"}


def test_parse_variable_definition_value_can_be_any_text():
    p = init_parser(":attr:[footnote](http://some.domain/path)")
    p.parse()

    assert listasdict(p.nodes) == []
    assert p.variables == {"attr": "[footnote](http://some.domain/path)"}


def test_parse_variable_definition_with_namespace():
    p = init_parser(":meta.attr:42")
    p.parse()

    assert listasdict(p.nodes) == []
    assert p.variables == {"meta": {"attr": "42"}}


def test_variable_replacement():
    source = """
    :answer:42
    
    The answer is {answer}
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "The answer is 42",
                    }
                ],
            },
        },
    ]

    _test(source, expected)


def test_variable_definition_escape():
    source = r"""
    \:answer:42
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": ":answer:42",
                    }
                ],
            },
        },
    ]

    _test(source, expected)


def test_skip_variable_replacement():
    source = r"""
    :answer:42
    
    The answer is \{answer\}
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "The answer is {answer}",
                    }
                ],
            },
        },
    ]

    _test(source, expected)


def test_variables_are_preprocessed():
    source = """
    :important:*IMPORTANT*
    
    This is {important}
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is ",
                    },
                    {
                        "type": "style",
                        "value": "star",
                        "content": {
                            "type": "sentence",
                            "content": [{"type": "text", "value": "IMPORTANT"}],
                        },
                    },
                ],
            },
        }
    ]

    _test(source, expected)
