from typing import Optional

from mau.text_buffer.context import Context


class Token:
    """
    This represents a token.
    Tokens have a type, a value (the actual characters), and a context
    """

    def __init__(
        self, _type: str, value: Optional[str] = None, context: Optional[Context] = None
    ):
        self.type = _type
        self.context = context or Context()
        self.value = value or ""

    def __repr__(self):
        return f'Token({self.type}, "{self.value}", {self.context})'

    def __eq__(self, other):
        try:
            if self.value == "" or other.value == "":
                return self.type == other.type

            return (self.type, self.value) == (
                other.type,
                other.value,
            )
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.type, self.value))

    def __len__(self):
        if self.value:
            return len(self.value)

        return 0

    def __bool__(self):
        return True

    def match(self, other):
        # Match is different from __eq__ because it also
        # checks the context.
        return self == other and self.context == other.context
