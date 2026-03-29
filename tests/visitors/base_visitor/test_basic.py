from unittest.mock import Mock, patch

from mau.environment.environment import Environment
from mau.nodes.node import Node, NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.test_helpers import ATestNode, NullMessageHandler, generate_context
from mau.visitors.base_visitor import (
    BaseVisitor,
    MauException,
    MauVisitorDebugMessage,
    MauVisitorErrorMessage,
    create_visitor_debug_message,
    create_visitor_exception,
    create_visitor_message,
)


def test_visitor_node_accept():
    node = Mock()
    node.accept.return_value = {
        "_type": "test",
        "_context": generate_context(1, 2, 3, 4).asdict(),
        "args": ["arg1"],
        "kwargs": {"key1": "value1"},
        "subtype": "subtype1",
        "tags": ["tag1"],
        "internal_tags": ["tag2"],
        "parent": {},
    }

    bv = BaseVisitor(NullMessageHandler(), Environment())
    result = bv.visit(node, key1="value1")

    node.accept.assert_called_with(bv, key1="value1")
    assert result == node.accept.return_value


def test_visitor_no_node():
    bv = BaseVisitor(NullMessageHandler(), Environment())
    result = bv.visit(None, key1="value1")

    assert result == {}


def test_generic_node():
    node = ATestNode(
        "Some test content",
        arguments=NodeArguments(
            unnamed_args=["arg1"],
            named_args={"key1": "value1"},
            tags=["tag1"],
            internal_tags=["tag2"],
            subtype="subtype1",
        ),
        info=NodeInfo(
            context=generate_context(1, 2, 3, 4),
        ),
    )

    bv = BaseVisitor(NullMessageHandler(), Environment())
    result = bv.visit(node)

    assert result == {
        "_type": "test",
        "_context": generate_context(1, 2, 3, 4).asdict(),
        "args": ["arg1"],
        "kwargs": {"key1": "value1"},
        "subtype": "subtype1",
        "tags": ["tag1"],
        "internal_tags": ["tag2"],
        "parent": {},
    }


def test_create_visitor_message_context_from_data():
    message_class = Mock()

    node = Node()
    node.type = "sometype"

    text = "text"
    data = {
        "some": "data",
        "_context": generate_context(0, 0, 0, 0).asdict(),
    }
    environment = Environment()
    additional_info = {"additional": "info"}

    actual_context = generate_context(1, 0, 1, 0)

    create_visitor_message(
        message_class, text, node, data, environment, additional_info
    )

    message_class.assert_called_with(
        text=text,
        context=actual_context,
        node_type="sometype",
        data=data,
        environment=environment,
        additional_info=additional_info,
    )


def test_create_visitor_message_context_from_node():
    message_class = Mock()

    node = Node()
    node.type = "sometype"
    node.info.context = generate_context(0, 0, 0, 0)

    text = "text"
    data = None
    environment = Environment()
    additional_info = {"additional": "info"}

    actual_context = generate_context(1, 0, 1, 0)

    create_visitor_message(
        message_class, text, node, data, environment, additional_info
    )

    message_class.assert_called_with(
        text=text,
        context=actual_context,
        node_type="sometype",
        data=data,
        environment=environment,
        additional_info=additional_info,
    )


@patch("mau.visitors.base_visitor.create_visitor_message")
def test_create_visitor_debug_message(mock_create_visitor_message):
    node = Node()
    node.type = "sometype"
    node.info.context = generate_context(0, 0, 0, 0)

    text = "text"
    data = None
    environment = Environment()
    additional_info = {"additional": "info"}

    create_visitor_debug_message(text, node, data, environment, additional_info)

    mock_create_visitor_message.assert_called_with(
        MauVisitorDebugMessage, text, node, data, environment, additional_info
    )


@patch("mau.visitors.base_visitor.create_visitor_message")
def test_create_visitor_exception(mock_create_visitor_message):
    node = Node()
    node.type = "sometype"
    node.info.context = generate_context(0, 0, 0, 0)

    text = "text"
    data = None
    environment = Environment()
    additional_info = {"additional": "info"}

    result = create_visitor_exception(text, node, data, environment, additional_info)

    mock_create_visitor_message.assert_called_with(
        MauVisitorErrorMessage, text, node, data, environment, additional_info
    )
    assert type(result) is MauException
    assert result.message == mock_create_visitor_message.return_value
