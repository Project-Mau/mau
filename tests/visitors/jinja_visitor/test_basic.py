import pytest

from mau.environment.environment import Environment
from mau.message import MauException, MauMessageType
from mau.test_helpers import ATestNode, NullMessageHandler
from mau.visitors.jinja_visitor import JinjaVisitor


def test_no_templates():
    visitor = JinjaVisitor(NullMessageHandler(), Environment())

    node = ATestNode("Just some text.")

    with pytest.raises(MauException) as exc:
        visitor.visit(node)

    assert exc.value.message.type == MauMessageType.ERROR_VISITOR
    assert exc.value.message.text == "Cannot find a suitable template."


def test_no_node():
    visitor = JinjaVisitor(NullMessageHandler(), Environment())

    result = visitor.visit(None)

    assert result == ""
