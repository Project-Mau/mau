import hashlib


class Node:
    node_type = "node"

    @property
    def _content(self):
        return {"type": self.node_type}

    def accept(self, visitor, *args, **kwargs):
        method_name = f"_visit_{self.node_type}"

        try:
            method = getattr(visitor, method_name)
        except AttributeError:
            method = getattr(visitor, "_visit_default")

        return method(self, *args, **kwargs)

    def __eq__(self, other):
        try:
            return self._content == other._content
        except AttributeError:  # pragma: no cover
            return False

    def __repr__(self):  # pragma: no cover
        return f"{self._content}"

    def hash(self):  # pragma: no cover
        return hashlib.md5(str(self).encode("utf-8")).hexdigest()[:8]


class ValueNode(Node):
    node_type = "value_node"

    def __init__(self, value=None):
        self.value = value

    @property
    def _content(self):
        return {"type": self.node_type, "value": self.value}


class SupaNode:
    node_type = "node"

    def __init__(
        self,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        self.parent = parent
        self.subtype = subtype
        self.children = children or []
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tags = tags or []

    @property
    def _content(self):
        return self.asdict()

    def _custom_dict(self):
        return {}

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
        method_name = f"_visit_{self.node_type}"

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


class SupaValueNode(SupaNode):
    node_type = "value_node"

    def __init__(
        self,
        value,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
        parent=None,
    ):
        super().__init__(parent, subtype, args, kwargs, tags)
        self.value = value

    def _custom_dict(self):
        return {
            "value": self.value,
        }
