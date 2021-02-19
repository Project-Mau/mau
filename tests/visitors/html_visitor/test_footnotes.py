from mau.visitors.html_visitor import HTMLVisitor

from mau.parsers.main_parser import MainParser
from tests.helpers import remove_indentation, init_parser_factory, visitlist_factory

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

    result = v._visit_footnote_def(
        {
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
    )

    assert result == {
        "defanchor": "defXYZ",
        "number": 1,
        "refanchor": "refXYZ",
        "text": "Some text 1",
    }


def test_footnotes():
    v = HTMLVisitor()

    result = v.visit_footnotes(
        [
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
    footnotes = [
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
