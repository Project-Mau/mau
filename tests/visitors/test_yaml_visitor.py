import yaml

from mau.environment.environment import Environment
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.test_helpers import ATestNode, NullMessageHandler, generate_context
from mau.visitors.yaml_visitor import YamlVisitor


def test_yaml_visitor_class_attributes():
    bv = YamlVisitor(NullMessageHandler(), Environment())

    assert bv.format_code == "yaml"
    assert bv.extension == "yaml"


def test_yaml_visitor_no_node():
    bv = YamlVisitor(NullMessageHandler(), Environment())
    result = bv.process(None)

    assert result == "{}\n"


def test_yaml_visitor_generic_node():
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

    bv = YamlVisitor(NullMessageHandler(), Environment())
    result = bv.process(node)

    assert yaml.load(result, Loader=yaml.SafeLoader) == {
        "_type": "test",
        "_context": generate_context(1, 2, 3, 4).asdict(),
        "args": ["arg1"],
        "kwargs": {"key1": "value1"},
        "subtype": "subtype1",
        "tags": ["tag1"],
        "internal_tags": ["tag2"],
        "parent": {},
    }
