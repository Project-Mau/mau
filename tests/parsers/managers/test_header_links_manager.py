import pytest

from mau.nodes.header import HeaderNode
from mau.nodes.inline import TextNode
from mau.nodes.macro import MacroHeaderNode
from mau.parsers.managers.header_links_manager import HeaderLinksManager


def test_header_links_manager():
    ilm = HeaderLinksManager()

    header_node = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
        content=[
            TextNode(
                "Header",
            )
        ],
    )

    macro_node = MacroHeaderNode("someheader")

    ilm.add_header(header_node)
    ilm.add_macros([macro_node])

    assert macro_node.header is None

    ilm.process()

    assert macro_node.header == header_node

    text_node: TextNode = macro_node.content[0]
    assert text_node.value == "Header"


def test_header_links_manager_macro_with_content():
    ilm = HeaderLinksManager()

    header_node = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
        content=[
            TextNode(
                "Header",
            )
        ],
    )

    macro_node = MacroHeaderNode(
        "someheader",
        content=[
            TextNode(
                "Another string",
            )
        ],
    )

    ilm.add_header(header_node)
    ilm.add_macros([macro_node])

    assert macro_node.header is None

    ilm.process()

    assert macro_node.header == header_node
    text_node: TextNode = macro_node.content[0]
    assert text_node.value == "Another string"


def test_header_macros_manager_no_macro():
    ilm = HeaderLinksManager()

    header_node = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
        content=[
            TextNode(
                "Header",
            )
        ],
    )

    ilm.add_header(header_node)

    ilm.process()


def test_header_macros_manager_no_header():
    ilm = HeaderLinksManager()

    macro_node = MacroHeaderNode("someheader")

    ilm.add_macros([macro_node])

    with pytest.raises(ValueError):
        ilm.process()


def test_header_links_manager_duplicate_header_name():
    ilm = HeaderLinksManager()

    header_node1 = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
    )

    header_node2 = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
    )

    ilm.add_header(header_node1)

    with pytest.raises(ValueError):
        ilm.add_header(header_node2)


def test_header_links_manager_update():
    ilm_src = HeaderLinksManager()
    ilm_dst = HeaderLinksManager()

    header_node = HeaderNode(
        level=2,
        internal_id="XXXXXX",
        name="someheader",
        content=[
            TextNode(
                "Header",
            )
        ],
    )

    macro_node = MacroHeaderNode("someheader")

    ilm_src.add_header(header_node)
    ilm_src.add_macros([macro_node])

    ilm_dst.update(ilm_src)
    ilm_dst.process()

    assert macro_node.header == header_node
