from mau.visitors.html_visitor import HTMLVisitor

from mau.parsers import nodes
from mau.parsers.main_parser import MainParser
from tests.helpers import (
    dedent,
    remove_indentation,
    init_parser_factory,
    visitlist_factory,
    ast_test_factory,
)

init_parser = init_parser_factory(MainParser)
visitlist = visitlist_factory(HTMLVisitor)

_test = ast_test_factory(MainParser, HTMLVisitor)


def test_toc_entry():
    v = HTMLVisitor()

    node = nodes.TocEntryNode(
        nodes.HeaderNode("Header 1", 1, "Header 1-XXXXXX"), children=[]
    )

    v._visit_toc_entry(node.asdict())

    assert node.asdict() == {
        "type": "toc_entry",
        "header": {
            "type": "header",
            "value": "Header 1",
            "level": 1,
            "anchor": "Header 1-XXXXXX",
            "kwargs": {},
            "tags": [],
        },
        "children": [],
    }


def test_command_toc():

    toc = nodes.TocNode(
        entries=[
            nodes.TocEntryNode(
                nodes.HeaderNode("Header 1", 1, "Header 1-XXXXXX"),
                children=[
                    nodes.TocEntryNode(
                        nodes.HeaderNode("Header 1.1", 2, "Header 1.1-XXXXXX")
                    )
                ],
            ),
            nodes.TocEntryNode(
                nodes.HeaderNode("Header 2", 1, "Header 2-XXXXXX"),
            ),
        ]
    )

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


def test_command_toc_exclude_tags():
    source = dedent(
        """
        [tags=notoc]
        = Header 1

        == Header 1.1

        = Header 2

        ::toc:exclude_tags=notoc
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == [
        '<h1 id="header-1">Header 1</h1>',
        '<h2 id="header-1.1">Header 1.1</h2>',
        '<h1 id="header-2">Header 2</h1>',
        remove_indentation(
            """
            <div>
              <ul>
                <li>
                  <a href="#header-2">Header 2</a>
                </li>
              </ul>
            </div>
            """
        ),
    ]


def test_command_toc_exclude_tags_multiple_tags():
    toc = nodes.TocNode(
        entries=[
            nodes.TocEntryNode(
                nodes.HeaderNode(
                    "Header 1", 1, "Header 1-XXXXXX", kwargs={"tags": "notoc,section"}
                ),
                children=[
                    nodes.TocEntryNode(
                        nodes.HeaderNode("Header 1.1", 2, "Header 1.1-XXXXXX")
                    )
                ],
            ),
            nodes.TocEntryNode(
                nodes.HeaderNode(
                    "Header 2", 1, "Header 2-XXXXXX", kwargs={"tags": "section"}
                ),
            ),
        ]
    )

    parser = init_parser('::toc:exclude_tags="notoc"')
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=toc)

    assert result == [
        remove_indentation(
            """
            <div>
              <ul>
                <li>
                  <a href="#Header 2-XXXXXX">Header 2</a>
                </li>
              </ul>
            </div>
            """
        )
    ]


def test_toc_generation_without_headers():
    source = dedent(
        """
        ::toc:
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == ["<div></div>"]


def test_toc_generation_from_headers():
    source = dedent(
        """
        = Header 1

        == Header 1.1

        ::toc:
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == [
        '<h1 id="header-1">Header 1</h1>',
        '<h2 id="header-1.1">Header 1.1</h2>',
        remove_indentation(
            """
            <div>
              <ul>
                <li>
                  <a href="#header-1">Header 1</a>
                  <ul>
                    <li>
                      <a href="#header-1.1">Header 1.1</a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
            """
        ),
    ]


def test_toc_generation_in_standard_blocks():
    source = dedent(
        """
        = Header 1

        == Header 1.1

        [someblock]
        ----
        == Header 1.2

        ::toc:
        ----
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == [
        '<h1 id="header-1">Header 1</h1>',
        '<h2 id="header-1.1">Header 1.1</h2>',
        '<div class="someblock"><div class="content"><h2 id="header-1.2">Header 1.2</h2>\n<div><ul><li><a href="#header-1">Header 1</a><ul><li><a href="#header-1.1">Header 1.1</a></li><li><a href="#header-1.2">Header 1.2</a></li></ul></li></ul></div></div></div>',
    ]
