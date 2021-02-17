from mau.visitors.html_visitor import HTMLVisitor

from mau.parsers.main_parser import MainParser
from tests.helpers import remove_indentation, init_parser_factory, visitlist_factory

init_parser = init_parser_factory(MainParser)
visitlist = visitlist_factory(HTMLVisitor)


def test_toc_entry():
    v = HTMLVisitor()

    result = v._visit_toc_entry(
        {
            "anchor": "Header 1-XXXXXX",
            "children": [],
            "value": "Header 1",
        }
    )

    assert result == '<li><a href="#Header 1-XXXXXX">Header 1</a></li>'


def test_toc_entry_with_children():
    v = HTMLVisitor()

    result = v._visit_toc_entry(
        {
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                    "value": "Header 1.1",
                }
            ],
            "value": "Header 1",
        }
    )

    assert result == remove_indentation(
        """
        <li>
          <a href="#Header 1-XXXXXX">Header 1</a>
          <ul>
            <li><a href="#Header 1.1-XXXXXX">Header 1.1</a></li>
          </ul>
        </li>
        """
    )


def test_toc():
    v = HTMLVisitor()

    result = v.visit_toc(
        [
            {
                "anchor": "Header 1-XXXXXX",
                "children": [
                    {
                        "anchor": "Header 1.1-XXXXXX",
                        "children": [],
                        "value": "Header 1.1",
                    },
                    {
                        "anchor": "Header 1.2-XXXXXX",
                        "children": [],
                        "value": "Header 1.2",
                    },
                ],
                "value": "Header 1",
            },
            {
                "anchor": "Header 2-XXXXXX",
                "children": [
                    {
                        "anchor": "Header 2.1-XXXXXX",
                        "children": [
                            {
                                "anchor": "Header 2.1.1-XXXXXX",
                                "children": [],
                                "value": "Header 2.1.1",
                            },
                        ],
                        "value": "Header 2.1",
                    },
                ],
                "value": "Header 2",
            },
        ]
    )

    assert result == remove_indentation(
        """
        <ul>
          <li>
            <a href="#Header 1-XXXXXX">Header 1</a>
            <ul>
             <li><a href="#Header 1.1-XXXXXX">Header 1.1</a></li>
             <li><a href="#Header 1.2-XXXXXX">Header 1.2</a></li>
            </ul>
          </li>
          <li>
            <a href="#Header 2-XXXXXX">Header 2</a>
            <ul>
              <li>
                <a href="#Header 2.1-XXXXXX">Header 2.1</a>
                <ul>
                  <li><a href="#Header 2.1.1-XXXXXX">Header 2.1.1</a></li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
        """
    )


def test_command_toc():
    toc = [
        {
            "anchor": "Header 1-XXXXXX",
            "value": "Header 1",
            "children": [
                {
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                    "value": "Header 1.1",
                },
            ],
        },
        {
            "anchor": "Header 2-XXXXXX",
            "value": "Header 2",
            "children": [],
        },
    ]

    parser = init_parser("::toc:")
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=toc)

    assert result == [
        remove_indentation(
            """
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
            """
        )
    ]
