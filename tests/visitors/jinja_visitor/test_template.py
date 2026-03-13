import pytest

from mau.nodes.node import Node, NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.visitors.jinja_visitor import Template


def test_specificity():
    template_a = Template(type="atype", content="content_a", name="name_a")

    template_b = Template(
        type="atype",
        content="content_b",
        name="name_b",
        subtype="asubtype",
        custom={
            "custom1": "value1",
            "custom2": "value2",
        },
        prefix="aprefix",
        parent_type="aptype",
        parent_custom={
            "pcustom1": "pvalue1",
            "pcustom2": "pvalue2",
        },
        parent_subtype="apstype",
        tags=["tag1", "tag2"],
    )

    assert template_a.specificity == (0, 0, 0, 0, 0, 0, 0)
    assert template_b.specificity == (2, 1, 1, 1, 2, 1, 2)


def test_from_name_type_only():
    template = Template.from_name("atype", content="somecontent")

    assert template.specificity == (0, 0, 0, 0, 0, 0, 0)


def test_from_name_empty_string():
    with pytest.raises(ValueError):
        Template.from_name("", content="somecontent")


def test_from_name_type_and_custom_fields():
    template = Template.from_name(
        "atype.somefield1__somevalue1.somefield2__somevalue2",
        content="somecontent",
    )

    assert template.specificity == (2, 0, 0, 0, 0, 0, 0)


def test_from_name_type_and_subtype():
    template = Template.from_name("atype.asubtype", content="somecontent")

    assert template.specificity == (0, 1, 0, 0, 0, 0, 0)


def test_from_name_type_and_prefix():
    template = Template.from_name("atype.pf_aprefix", content="somecontent")

    assert template.specificity == (0, 0, 1, 0, 0, 0, 0)


def test_from_name_type_and_parent_type():
    template = Template.from_name("atype.pt_aptype", content="somecontent")

    assert template.specificity == (0, 0, 0, 1, 0, 0, 0)


def test_from_name_type_and_parent_custom():
    template = Template.from_name(
        "atype.pts_custom1__value1.pts_custom2__value2", content="somecontent"
    )

    assert template.specificity == (0, 0, 0, 0, 2, 0, 0)


def test_from_name_type_and_parent_subtype():
    template = Template.from_name("atype.pts_apstype", content="somecontent")

    assert template.specificity == (0, 0, 0, 0, 0, 1, 0)


def test_from_name_type_and_tags():
    template = Template.from_name("atype.tg_atag1.tg_atag2", content="somecontent")

    assert template.specificity == (0, 0, 0, 0, 0, 0, 2)


def test_from_name_type_and_multiple_out_of_order():
    template = Template.from_name(
        "atype.tg_atag1.pt_aptype.field__value.asubtype.pts_custom1__value1.pf_aprefix.tg_atag2.pts_apstype",
        content="somecontent",
    )

    assert template.specificity == (1, 1, 1, 1, 1, 1, 2)


def test_match_type():
    template = Template(type="type_a", name="name_a", content="content_a")

    node_a = Node()
    node_a.type = "type_a"

    node_b = Node()
    node_b.type = "type_b"

    assert template.match(node_a)
    assert not template.match(node_b)


def test_match_prefix():
    template = Template(
        type="type_a", name="name_a", content="content_a", prefix="prefix_a"
    )

    node_a = Node()
    node_a.type = "type_a"

    assert template.match(node_a, prefix="prefix_a")

    assert not template.match(node_a, prefix="prefix_b")


def test_match_prefix_when_none():
    template = Template(
        type="type_a", name="name_a", content="content_a", prefix="prefix_a"
    )

    node_a = Node()
    node_a.type = "type_a"

    assert template.match(node_a, prefix="prefix_a")

    assert not template.match(node_a)


def test_match_custom():
    class NodeWithCustom(Node):
        # A node with custom fields.
        type = "sometype"

        def __init__(
            self,
            somefield: str,
            parent: Node | None = None,
            arguments: NodeArguments | None = None,
            info: NodeInfo | None = None,
        ):
            super().__init__(parent=parent, arguments=arguments, info=info)
            self.somefield = somefield

        @property
        def custom_template_fields(self):
            return {"somefield": self.somefield}

    template = Template(
        type="type_a",
        name="name_a",
        content="content_a",
        custom={"somefield": "somevalueA"},
    )

    node_a = NodeWithCustom(somefield="somevalueA")
    node_a.type = "type_a"

    node_b = NodeWithCustom(somefield="somevalueB")
    node_b.type = "type_a"

    node_c = Node()
    node_c.type = "type_a"

    assert template.match(node_a)
    assert not template.match(node_b)
    assert not template.match(node_c)


def test_match_subtype():
    template = Template(
        type="type_a", name="name_a", content="content_a", subtype="subtype_a"
    )

    node_a = Node()
    node_a.type = "type_a"
    node_a.arguments.subtype = "subtype_a"

    node_b = Node()
    node_b.type = "type_a"
    node_b.arguments.subtype = "subtype_b"

    assert template.match(node_a)
    assert not template.match(node_b)


def test_match_parent_type():
    template = Template(
        type="type_a", name="name_a", content="content_a", parent_type="ptype_a"
    )

    parent_a = Node()
    parent_a.type = "ptype_a"

    parent_b = Node()
    parent_b.type = "ptype_b"

    node_a = Node()
    node_a.type = "type_a"
    node_a.parent = parent_a

    node_b = Node()
    node_b.type = "type_a"
    node_b.parent = parent_b

    assert template.match(node_a)
    assert not template.match(node_b)


def test_match_parent_type_no_parent():
    template = Template(
        type="type_a", name="name_a", content="content_a", parent_type="ptype_a"
    )

    node_a = Node()
    node_a.type = "type_a"

    assert not template.match(node_a)


def test_match_parent_subtype():
    template = Template(
        type="type_a", name="name_a", content="content_a", parent_subtype="pstype_a"
    )

    parent_a = Node()
    parent_a.type = "ptype_a"
    parent_a.arguments.subtype = "pstype_a"

    parent_b = Node()
    parent_b.type = "ptype_b"

    node_a = Node()
    node_a.type = "type_a"
    node_a.parent = parent_a

    node_b = Node()
    node_b.type = "type_a"
    node_b.parent = parent_b

    assert template.match(node_a)
    assert not template.match(node_b)


def test_match_parent_subtype_no_parent():
    template = Template(
        type="type_a", name="name_a", content="content_a", parent_subtype="pstype_a"
    )

    node_a = Node()
    node_a.type = "type_a"

    assert not template.match(node_a)


def test_match_parent_custom():
    class ParentWithCustom(Node):
        type = "ptype"

        def __init__(self, somefield, **kwargs):
            super().__init__(**kwargs)
            self.somefield = somefield

        @property
        def custom_template_fields(self):
            return {"somefield": self.somefield}

    template = Template(
        type="type_a",
        name="name_a",
        content="content_a",
        parent_custom={"somefield": "somevalueA"},
    )

    parent_a = ParentWithCustom(somefield="somevalueA")
    parent_b = ParentWithCustom(somefield="somevalueB")
    parent_c = Node()
    parent_c.type = "ptype"

    node_a = Node()
    node_a.type = "type_a"
    node_a.parent = parent_a

    node_b = Node()
    node_b.type = "type_a"
    node_b.parent = parent_b

    node_c = Node()
    node_c.type = "type_a"
    node_c.parent = parent_c

    assert template.match(node_a)
    assert not template.match(node_b)
    assert not template.match(node_c)


def test_match_parent_custom_no_parent():
    template = Template(
        type="type_a",
        name="name_a",
        content="content_a",
        parent_custom={"somefield": "somevalue"},
    )

    node_a = Node()
    node_a.type = "type_a"

    assert not template.match(node_a)


def test_match_tags():
    template = Template(
        type="type_a", name="name_a", content="content_a", tags=["tag_a1", "tag_a2"]
    )

    node_a = Node()
    node_a.type = "type_a"
    node_a.arguments.tags = ["tag_a1"]

    node_b = Node()
    node_b.type = "type_a"
    node_b.arguments.tags = ["tag_a1", "tag_a2", "tag_a3"]

    node_c = Node()
    node_c.type = "type_a"
    node_c.arguments.tags = ["tag_c1"]

    assert template.match(node_b)
    assert not template.match(node_a)
    assert not template.match(node_c)
