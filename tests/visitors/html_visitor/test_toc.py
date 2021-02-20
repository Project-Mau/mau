from mau.visitors.html_visitor import HTMLVisitor

from mau.parsers.main_parser import MainParser
from tests.helpers import remove_indentation, init_parser_factory, visitlist_factory

init_parser = init_parser_factory(MainParser)
visitlist = visitlist_factory(HTMLVisitor)


def test_toc_entry():
    v = HTMLVisitor()

    result = v._visit_toc_entry(
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 1",
            "anchor": "Header 1-XXXXXX",
            "children": [],
        }
    )

    assert result == {
        "text": "Header 1",
        "anchor": "Header 1-XXXXXX",
        "children": "",
    }


def test_command_toc():

    toc = [
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 1",
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "type": "toc_entry",
                    "level": 2,
                    "text": "Header 1.1",
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                },
            ],
        },
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 2",
            "anchor": "Header 2-XXXXXX",
            "children": [],
        },
    ]

    parser = init_parser("::toc:")
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=toc)

    assert result == [
        remove_indentation(
            """
            <div>
              <ul>
                <li>
                  <a href="#Header 1-XXXXXX">Header 1</a>
                  <ul>
                    <li>
                      <a href="#Header 1.1-XXXXXX">Header 1.1</a>
                    </li>
                  </ul>
                </li>
                <li>
                  <a href="#Header 2-XXXXXX">Header 2</a>
                </li>
              </ul>
            </div>
            """
        )
    ]
