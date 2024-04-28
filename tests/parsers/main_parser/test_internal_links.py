import textwrap

import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.macros import MacroHeaderNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_internal_link():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    This is a paragraph with an internal link [header](someid, text).

    [id=someid]
    == Header
    """

    parser = runner(textwrap.dedent(source), environment)
    parser.finalise()

    header_node = HeaderNode(
        value=SentenceNode(children=[TextNode("Header")]),
        level="2",
        anchor="XXXXXX",
        kwargs={"id": "someid"},
    )

    assert parser.internal_links_manager.links == [
        MacroHeaderNode(
            header_id="someid", header=header_node, children=[TextNode("text")]
        )
    ]
    assert parser.internal_links_manager.headers == {"someid": header_node}


def test_internal_link_no_header():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    This is a paragraph with an internal link [header](someotherid, text).

    [id=someid]
    == Header
    """

    with pytest.raises(MauErrorException):
        runner(textwrap.dedent(source))


def test_internal_link_header_in_block():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    This is a paragraph with an internal link [header](someid, text).

    ====
    [id=someid]
    == Header
    ====
    """

    parser = runner(textwrap.dedent(source), environment)
    parser.finalise()

    header_node = HeaderNode(
        value=SentenceNode(children=[TextNode("Header")]),
        level="2",
        anchor="XXXXXX",
        kwargs={"id": "someid"},
    )

    assert parser.internal_links_manager.links == [
        MacroHeaderNode(
            header_id="someid", header=header_node, children=[TextNode("text")]
        )
    ]
    assert parser.internal_links_manager.headers == {"someid": header_node}


def test_internal_link_link_in_block():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    ====
    This is a paragraph with an internal link [header](someid, text).
    ====

    [id=someid]
    == Header
    """

    parser = runner(textwrap.dedent(source), environment)
    parser.finalise()

    header_node = HeaderNode(
        value=SentenceNode(children=[TextNode("Header")]),
        level="2",
        anchor="XXXXXX",
        kwargs={"id": "someid"},
    )

    assert parser.internal_links_manager.links == [
        MacroHeaderNode(
            header_id="someid", header=header_node, children=[TextNode("text")]
        )
    ]
    assert parser.internal_links_manager.headers == {"someid": header_node}


def test_internal_link_link_and_header_in_block():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    ====
    This is a paragraph with an internal link [header](someid, text).

    [id=someid]
    == Header
    ====
    """

    parser = runner(textwrap.dedent(source), environment)
    parser.finalise()

    header_node = HeaderNode(
        value=SentenceNode(children=[TextNode("Header")]),
        level="2",
        anchor="XXXXXX",
        kwargs={"id": "someid"},
    )

    assert parser.internal_links_manager.links == [
        MacroHeaderNode(
            header_id="someid", header=header_node, children=[TextNode("text")]
        )
    ]
    assert parser.internal_links_manager.headers == {"someid": header_node}
