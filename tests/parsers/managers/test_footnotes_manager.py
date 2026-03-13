from unittest.mock import patch

import pytest

from mau.message import MauException, MauMessageType
from mau.nodes.block import BlockNode
from mau.nodes.include import FootnotesNode
from mau.nodes.macro import (
    MacroFootnoteNode,
)
from mau.parsers.managers.footnotes_manager import FootnotesManager


def test_footnotes_manager_init():
    fnm = FootnotesManager()

    assert fnm.footnote_macros == []
    assert fnm.bodies == {}
    assert fnm.footnotes_list_nodes == []


def test_footnotes_manager_add_footnote_macros():
    fnm = FootnotesManager()

    macro_footnote_node = MacroFootnoteNode("name")

    fnm.add_footnote_macros([macro_footnote_node])

    assert fnm.footnote_macros == [macro_footnote_node]
    assert fnm.bodies == {}
    assert fnm.footnotes_list_nodes == []


def test_footnotes_manager_add_body():
    fnm = FootnotesManager()

    footnote_name = "name"
    footnote_block_node = BlockNode()

    fnm.add_body(footnote_name, footnote_block_node)

    assert fnm.footnote_macros == []
    assert fnm.bodies == {footnote_name: footnote_block_node}
    assert fnm.footnotes_list_nodes == []


def test_footnotes_manager_add_footnotes_list():
    fnm = FootnotesManager()

    footnotes_list = FootnotesNode()

    fnm.add_footnotes_list(footnotes_list)

    assert fnm.footnote_macros == []
    assert fnm.bodies == {}
    assert fnm.footnotes_list_nodes == [footnotes_list]


def test_footnotes_manager_update():
    fnm = FootnotesManager()

    footnote_name = "nope"

    macro_footnote_node = MacroFootnoteNode(footnote_name)
    fnm.add_footnote_macros([macro_footnote_node])

    footnote_block_node = BlockNode()
    footnote_body = footnote_block_node
    fnm.add_body(footnote_name, footnote_body)

    footnote_list = FootnotesNode()
    fnm.add_footnotes_list(footnote_list)

    other_fnm = FootnotesManager()
    other_fnm.update(fnm)

    assert other_fnm.footnote_macros == [macro_footnote_node]
    assert other_fnm.bodies == {footnote_name: footnote_block_node}
    assert other_fnm.footnotes_list_nodes == [footnote_list]


def test_footnotes_manager_add_node_duplicate_name():
    fnm = FootnotesManager()

    footnote_name = "nope"

    footnote_block_node1 = BlockNode()
    footnote_body1 = footnote_block_node1

    footnote_block_node2 = BlockNode()
    footnote_body2 = footnote_block_node2

    fnm.add_body(footnote_name, footnote_body1)

    with pytest.raises(MauException) as exc:
        fnm.add_body(footnote_name, footnote_body2)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Footnote 'nope' has been already defined."
    assert exc.value.message.context == footnote_body2.info.context


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_footnotes_manager_process(mock_footnote_unique_id):
    mock_footnote_unique_id.return_value = "XXYY"

    fnm = FootnotesManager()

    footnote_name1 = "footnote_name1"
    footnote_name2 = "footnote_name2"

    # Create and add footnote macro nodes.
    macro_footnote_node1 = MacroFootnoteNode(footnote_name1)
    macro_footnote_node2 = MacroFootnoteNode(footnote_name2)

    fnm.add_footnote_macros([macro_footnote_node1, macro_footnote_node2])

    # Create and add bodies.
    footnote_block_node1 = BlockNode()
    footnote_body1 = footnote_block_node1
    fnm.add_body(footnote_name1, footnote_body1)

    footnote_block_node2 = BlockNode()
    footnote_body2 = footnote_block_node2
    fnm.add_body(footnote_name2, footnote_body2)

    # Create and add footnote lists.
    footnotes_list1 = FootnotesNode()
    fnm.add_footnotes_list(footnotes_list1)

    footnotes_list2 = FootnotesNode()
    fnm.add_footnotes_list(footnotes_list2)

    fnm.process()

    # Get the list of footnotes for each
    # footnotes list.
    footnotes1 = [item.footnote for item in footnotes_list1.footnotes]
    footnotes2 = [item.footnote for item in footnotes_list2.footnotes]

    # Check that all footnote lists have
    # the same list of footnotes.
    assert footnotes1 == footnotes2

    # Check that the footnotes have been
    # created with the proper ids.
    assert footnotes1[0].public_id == "1"
    assert footnotes1[0].internal_id == "XXYY"
    assert footnotes1[1].public_id == "2"
    assert footnotes1[1].internal_id == "XXYY"

    # Check that footnote macros have
    # been properly connected with
    # the footnote they reference.
    assert macro_footnote_node1.footnote == footnotes1[0]
    assert macro_footnote_node2.footnote == footnotes1[1]


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_footnotes_manager_process_undefined_footnote(mock_footnote_unique_id):
    # This test checks that the process stops if
    # it finds a footnote macro that mentions a
    # footnote that has not been defined with a body.

    mock_footnote_unique_id.return_value = "XXYY"

    fnm = FootnotesManager()

    footnote_name1 = "footnote_name1"
    footnote_name2 = "footnote_name2"

    # Create and add footnote macro nodes.
    macro_footnote_node1 = MacroFootnoteNode(footnote_name1)
    macro_footnote_node2 = MacroFootnoteNode(footnote_name2)

    fnm.add_footnote_macros([macro_footnote_node1, macro_footnote_node2])

    # Create and add bodies.
    footnote_block_node1 = BlockNode()
    footnote_body1 = footnote_block_node1
    fnm.add_body(footnote_name1, footnote_body1)

    with pytest.raises(MauException) as exc:
        fnm.process()

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Footnote 'footnote_name2' has not been defined."
    assert exc.value.message.context == macro_footnote_node2.info.context
