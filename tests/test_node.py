from mau.nodes.inline import TextNode
from mau.nodes.node import Node, NodeInfo, ValueNode, WrapperNode
from mau.nodes.node_arguments import NodeArguments
from mau.test_helpers import generate_context


def test_info():
    info = NodeInfo(
        context=generate_context(0, 0, 0, 0),
    )

    assert info.asdict() == {
        "context": generate_context(0, 0, 0, 0).asdict(),
    }


def test_arguments():
    arguments = NodeArguments(
        unnamed_args=["arg1"],
        named_args={"key1": "value1"},
        tags=["tag1"],
        internal_tags=["tag2"],
        subtype="subtype1",
    )

    assert arguments.asdict() == {
        "unnamed_args": ["arg1"],
        "named_args": {"key1": "value1"},
        "tags": ["tag1"],
        "internal_tags": ["tag2"],
        "subtype": "subtype1",
    }


def test_node_parent():
    parent = Node()
    node = Node(parent=parent)

    assert node.parent is parent


def test_node_set_parent():
    parent = Node()
    node = Node()

    node.set_parent(parent)

    assert node.parent is parent


def test_node_deepcopy():
    parent = Node()
    args = NodeArguments(unnamed_args=["a"], named_args={"k": "v"})
    node = Node(parent=parent, arguments=args)

    new_parent = Node()
    copy = node.deepcopy(parent=new_parent)

    assert copy is not node
    assert type(copy) is Node
    assert copy.parent is new_parent
    assert copy.arguments is not node.arguments
    assert copy.arguments == node.arguments
    assert copy.info is not node.info


def test_node_deepcopy_default_parent():
    node = Node(parent=Node())
    copy = node.deepcopy()

    assert copy.parent is None


def test_value_node_deepcopy():
    parent = Node()
    node = ValueNode(value="hello", parent=parent)

    new_parent = Node()
    copy = node.deepcopy(parent=new_parent)

    assert copy is not node
    assert type(copy) is ValueNode
    assert copy.parent is new_parent
    assert copy.value == "hello"


def test_wrapper_node_deepcopy():
    parent = Node()
    child1 = TextNode(value="word1", parent=None)
    child2 = TextNode(value="word2", parent=None)
    node = WrapperNode(parent=parent, content=[child1, child2])

    new_parent = Node()
    copy = node.deepcopy(parent=new_parent)

    assert copy is not node
    assert type(copy) is WrapperNode
    assert copy.parent is new_parent
    assert len(copy.content) == 2
    assert copy.content[0] is not child1
    assert copy.content[1] is not child2
    assert copy.content[0].value == "word1"
    assert copy.content[1].value == "word2"
    assert copy.content[0].parent is copy
    assert copy.content[1].parent is copy


def test_wrapper_node_deepcopy_no_mutation():
    child = TextNode(value="original", parent=None)
    node = WrapperNode(content=[child])

    copy = node.deepcopy()

    copy.content[0].value = "modified"
    assert child.value == "original"
