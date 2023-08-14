from dataclasses import dataclass
from typing import Optional


@dataclass
class Context:
    # Context objects represent the place where a token was found
    # in the source code. They contain line and column where they
    # begin, the name of the source file (if provided), and the
    # text of the full line.

    line: int = 0
    column: int = 0
    source: Optional[str] = None
    text: str = ""

    def asdict(self):
        return {
            "line": self.line,
            "column": self.column,
            "source": self.source,
            "text": self.text,
        }

    def __repr__(self):
        return f"Context({self.line},{self.column},{self.source})"


def print_context(context, error_message=None):  # pragma: no cover
    # This is a function used to print out the context of a token
    # when an error occurs in Mau. It's a typical graphical
    # error-reporting function: a mess.

    len_bar = len(error_message) if error_message is not None else 0
    title = " Mau Error "

    # This takes into account the title and the spaces
    half_bar = "=" * ((len_bar - len(title)) // 2 + 1)
    full_bar = half_bar + "=" * len(title) + half_bar

    print(f"{half_bar}{title}{half_bar}")

    if error_message is not None:
        print(error_message)
        print()

    if context.source is not None:
        print(f"Source: {context.source}")
    print(f"Line: {context.line} - Column: {context.column}")
    print()

    print(f"{context.line}: {context.text}")
    print(" " * (len(str(context.line)) + 2) + "^")
    print(f"{full_bar}")
