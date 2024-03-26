from mau.lexers.main_lexer import MainLexer
from mau.nodes.page import HorizontalRuleNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_horizontal_rule():
    source = "---"

    expected = [HorizontalRuleNode()]

    assert runner(source).nodes == expected


def test_horizontal_rule_with_arguments():
    source = """
    [*break,arg1,key1=value1]
    ---
    """

    expected = [
        HorizontalRuleNode(
            subtype="break",
            args=["arg1"],
            kwargs={
                "key1": "value1",
            },
        ),
    ]

    assert runner(source).nodes == expected
