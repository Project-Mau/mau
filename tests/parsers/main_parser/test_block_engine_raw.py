from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.inline import RawNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_block_raw_engine():
    source = """
    [*block, engine=raw]
    ----
    Raw content
    on multiple lines
    ----
    Secondary content
    on multiple lines as well
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="block",
            children=[
                RawNode("Raw content"),
                RawNode("on multiple lines"),
            ],
            secondary_children=[
                RawNode("Secondary content"),
                RawNode("on multiple lines as well"),
            ],
            classes=[],
            title=None,
            engine="raw",
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]
