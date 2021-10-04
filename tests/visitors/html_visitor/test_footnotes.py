from mau.visitors.html_visitor import HTMLVisitor

from mau.parsers import nodes
from mau.parsers.main_parser import MainParser
from tests.helpers import (
    dedent,
    remove_indentation,
    init_parser_factory,
    visitlist_factory,
)

init_parser = init_parser_factory(MainParser)
visitlist = visitlist_factory(HTMLVisitor)


def test_footnote():
    v = HTMLVisitor()

    result = v.visit(
        {
            "type": "footnote_ref",
            "number": 6,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
        }
    )

    assert result == '<sup>[<a id="refXYZ" href="#defXYZ">6</a>]</sup>'


def test_footnote_definition():
    v = HTMLVisitor()

    node = {
        "type": "footnote_def",
        "number": 1,
        "refanchor": "refXYZ",
        "defanchor": "defXYZ",
        "content": [
            {
                "type": "sentence",
                "content": [
                    {"type": "text", "value": "Some text 1"},
                ],
            }
        ],
    }

    v._visit_footnote_def(node)

    assert node == {
        "type": "footnote_def",
        "defanchor": "defXYZ",
        "number": 1,
        "refanchor": "refXYZ",
        "content": "Some text 1",
    }


def test_footnotes():
    v = HTMLVisitor()

    nodes = [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ1",
            "defanchor": "defXYZ1",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {"type": "text", "value": "Some text 1"},
                    ],
                }
            ],
        },
        {
            "type": "footnote_def",
            "number": 2,
            "refanchor": "refXYZ2",
            "defanchor": "defXYZ2",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {"type": "text", "value": "Some text 2"},
                    ],
                }
            ],
        },
    ]

    result = v._render(
        "footnotes",
        entries="".join([v.visit(i) for i in nodes]),
    )

    assert result == remove_indentation(
        """
        <div id="_footnotes">
          <div id="defXYZ1">
            <a href="#refXYZ1">1</a> Some text 1
          </div>
          <div id="defXYZ2">
            <a href="#refXYZ2">2</a> Some text 2
          </div>
        </div>
        """
    )


def test_command_footnotes():
    footnotes = nodes.FootnotesNode(
        entries=[
            nodes.FootnoteDefNode(
                1,
                "refXYZ1",
                "defXYZ1",
                [nodes.SentenceNode([nodes.TextNode("Some text 1")])],
            ),
            nodes.FootnoteDefNode(
                2,
                "refXYZ2",
                "defXYZ2",
                [nodes.SentenceNode([nodes.TextNode("Some text 2")])],
            ),
        ]
    )

    parser = init_parser("::footnotes:")
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], footnotes=footnotes)

    assert result == [
        remove_indentation(
            """
            <div id="_footnotes">
              <div id="defXYZ1">
                <a href="#refXYZ1">1</a> Some text 1
              </div>
              <div id="defXYZ2">
                <a href="#refXYZ2">2</a> Some text 2
              </div>
            </div>
            """
        )
    ]


def test_footnotes_generation_without_footnote_definitions():
    source = dedent(
        """
        ::footnotes:
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist(
        [node.asdict() for node in parser.nodes], footnotes=parser.footnotes
    )

    assert result == ["""<div id="_footnotes"></div>"""]
