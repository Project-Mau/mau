import pytest

from mau.environment.environment import Environment
from mau.message import MauException, MauMessageType
from mau.parsers.buffers.control_buffer import Control, ControlBuffer
from mau.test_helpers import (
    generate_context,
)


def test_control_buffer():
    cb = ControlBuffer()

    assert cb.pop() is None


def test_control_buffer_push_and_pop():
    cb = ControlBuffer()
    test_control = Control(
        "if",
        "answer",
        "==",
        "42",
        generate_context(0, 1, 0, 10),
    )

    cb.push(test_control)

    assert cb.pop() == test_control
    assert cb.pop() is None


def test_control_buffer_push_twice():
    cb = ControlBuffer()
    test_control1 = Control(
        "if",
        "answer",
        "==",
        "42",
        generate_context(0, 1, 0, 10),
    )
    test_control2 = Control(
        "if",
        "answer",
        "!=",
        "43",
        generate_context(0, 1, 0, 10),
    )

    cb.push(test_control1)
    cb.push(test_control2)

    assert cb.pop() == test_control2
    assert cb.pop() is None


def test_control_process_wrong_operator():
    with pytest.raises(MauException) as exc:
        Control(
            "notanoperator", "answer", "==", "42", context=generate_context(1, 2, 1, 20)
        )

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text == "Control operator 'notanoperator' is not supported."
    )
    assert exc.value.message.context == generate_context(1, 2, 1, 20)


def test_control_process_if_operator_variable_not_defined_equality():
    environment = Environment()

    c = Control("if", "answer", "==", "42", generate_context(0, 0, 0, 10))

    with pytest.raises(MauException) as exc:
        c.process(environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'answer' has not been defined."


def test_control_process_if_operator_variable_defined_equality():
    environment = Environment.from_dict({"answer": "42"})

    c = Control("if", "answer", "==", "42", generate_context(0, 0, 0, 10))

    assert c.process(environment) is True


def test_control_process_if_operator_variable_not_defined_inequality():
    environment = Environment()

    c = Control("if", "answer", "!=", "42", generate_context(0, 0, 0, 10))

    with pytest.raises(MauException) as exc:
        c.process(environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'answer' has not been defined."


def test_control_process_if_operator_variable_defined_inequality():
    environment = Environment.from_dict({"answer": "42"})

    c = Control("if", "answer", "!=", "42", generate_context(0, 0, 0, 10))

    assert c.process(environment) is False
