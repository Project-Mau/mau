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
