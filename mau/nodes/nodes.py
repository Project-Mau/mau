import hashlib


class Node:
    node_type = "node"

    def __init__(
        self,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        self.parent = parent
        self.parent_position = parent_position
        self.subtype = subtype
        self.children = children or []
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tags = tags or []

    def _custom_dict(self):
        return {}

    def add_children(self, children):
        self.children.extend(children)
        for child in children:
            child.parent = self

    def asdict(self):
        base = {
            # Parent is excluded to avoid
            # having to deal with recursion
            "type": self.node_type,
            "subtype": self.subtype,
            "children": [i.asdict() for i in self.children],
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
        base.update(self._custom_dict())

        return base

    def accept(self, visitor, *args, **kwargs):
        # Some node types contain a dot to allow templates
        # to be created in a hierarchy of directories
        # but dots are not allowed in function names
        method_name = f"_visit_{self.node_type.replace('.', '__')}"

        try:
            method = getattr(visitor, method_name)
        except AttributeError:
            method = getattr(visitor, "_visit_default")

        return method(self, *args, **kwargs)

    def __eq__(self, other):
        try:
            return self.asdict() == other.asdict()
        except AttributeError:  # pragma: no cover
            return False

    def __repr__(self):  # pragma: no cover
        return str(self.asdict())

    def hash(self):  # pragma: no cover
        return hashlib.md5(str(self).encode("utf-8")).hexdigest()[:8]


class ValueNode(Node):
    node_type = "value_node"

    def __init__(
        self,
        value,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.value = value

    def _custom_dict(self):
        return {
            "value": self.value,
        }
