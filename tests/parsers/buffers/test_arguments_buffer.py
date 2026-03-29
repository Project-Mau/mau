from mau.nodes.node_arguments import NodeArguments
from mau.parsers.buffers.arguments_buffer import ArgumentsBuffer


def test_arguments_buffer():
    ab = ArgumentsBuffer()

    assert ab.pop() is None
    assert ab.pop_or_default() == NodeArguments()


def test_arguments_buffer_push_and_pop():
    ab = ArgumentsBuffer()
    test_arguments = NodeArguments(unnamed_args=["42"])

    ab.push(test_arguments)

    assert ab.pop() is test_arguments
    assert ab.pop() is None


def test_arguments_buffer_pop_or_default():
    ab = ArgumentsBuffer()
    test_arguments = NodeArguments(unnamed_args=["42"])

    ab.push(test_arguments)

    assert ab.pop_or_default() is test_arguments
    assert ab.pop_or_default() == NodeArguments()
