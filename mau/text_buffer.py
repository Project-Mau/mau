from __future__ import annotations

from dataclasses import dataclass

Position = tuple[int, int]


def adjust_context(context: Context):
    """Text files in editors are indexed from 1
    both vertically (lines) and horizontally
    (columns), while internally, we
    deal with lists which are indexed from 0.

    This function moves the given context
    to 1,1, making it readable by a human.
    """
    return context.clone().move_to(1, 0)


def adjust_context_dict(context_dict: dict):
    """Text files in editors are indexed from 1
    both vertically (lines) and horizontally
    (columns), while internally, we
    deal with lists which are indexed from 0.

    This function moves the given context
    to 1,1, making it readable by a human.
    """
    return Context(**context_dict).move_to(1, 0)


def adjust_position(position: Position):
    """Text files in editors are indexed from 1
    both vertically (lines) and horizontally
    (columns), while internally, we
    deal with lists which are indexed from 0.

    This function shifts the given position
    by 1 both vertically and horizontally,
    making it readable by a human.
    """
    return (position[0] + 1, position[1])


@dataclass
class Context:
    # Context objects represent the place where a token was found
    # in the source code. They contain start and end line and
    # column of the text block, and the name of the source file
    # (if provided).

    start_line: int
    start_column: int
    end_line: int
    end_column: int
    source: str | None = None

    @classmethod
    def empty(cls) -> Context:
        return Context(0, 0, 0, 0)

    @classmethod
    def merge_contexts(cls, ctx1: Context, ctx2: Context) -> Context:
        """Merge two contexts.
        This function merges two contexts, returning
        a context that contains both.
        """
        context = Context(
            start_line=min(ctx1.start_line, ctx2.start_line),
            start_column=min(ctx1.start_column, ctx2.start_column),
            end_line=max(ctx1.end_line, ctx2.end_line),
            end_column=max(ctx1.end_column, ctx2.end_column),
            source=ctx1.source,
        )

        return context

    @property
    def start_position(self) -> Position:
        return (self.start_line, self.start_column)

    @property
    def end_position(self) -> Position:
        return (self.end_line, self.end_column)

    def move_to(self, line: int, column: int) -> Context:
        """Move the context to a new start position."""
        self.start_line += line
        self.end_line += line
        self.start_column += column
        self.end_column += column

        return self

    def asdict(self):
        return {
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "source": self.source,
        }

    def clone(self):
        return self.__class__(**self.asdict())

    def __repr__(self):
        source_prefix = ""
        if self.source:
            source_prefix = f"{self.source}:"

        return f"{source_prefix}{self.start_line},{self.start_column}-{self.end_line},{self.end_column}"

    def __str__(self):
        return repr(self)


# The TextBuffer is an object used to interact with a text file.
#
# The object contains by default an empty piece of text and no
# initial context, but it can accept both at initialisation time.
#
# The object itself doesn't interact with files, the text content
# has to be loaded externally. The `text` parameter is a single
# string containing newlines, the object will split it internally.
# When a piece of text is loaded it is split into lines using `\n`.
#
# The attribute `initial_context` allows to nest pieces of text that
# come from different sources. The property `context` takes the
# initial context into account and adjusts the line and column.
#
# The object has several properties:
# * `eof` - True if the current line is beyond the last line.
# * `eol` - True if the current column is beyond the last column
#   of the current line.
# * `current_line` - The current line of the file or an empty string
#   in case of EOF.
# * `current_char` - The current character of the current line
#   or an empty string in case of EOL/EOF.
# * `peek_char` - The next character of the current line
#   or an empty string in case of EOL/EOF.
# * `tail` - The remaining part of the line starting with the next
#   character.
# * `position` - (getter/setter) A tuple (line, column) with the
#   current position.
# * `context` - A instance of Context relative to `initial_context`.
#
# The class also exposes three main methods:
# * `load` - Loads a string into the internal buffer. The string is
#   split using newlines `\n`.
# * `nextline` - Moves to the beginning of the next line.
# * `skip` - Skips the given number of characters.
#
# The class has been designed to minimise the number of exceptions it
# can raise, so it will quietly go beyond the end of the line of beyond
# the end of the file. It's the users task to check whether one of
# these conditions occured.


class TextBuffer:
    def __init__(
        self,
        text: str = "",
        start_line: int = 0,
        start_column: int = 0,
        source_filename: str | None = None,
    ):
        self.line = 0
        self.column = 0
        self.start_line = start_line
        self.start_column = start_column
        self.source_filename = source_filename

        # Split the input text into lines.
        self.lines = text.split("\n") if text != "" else []

    @property
    def eof(self) -> bool:
        """
        True if the position is beyond EOF.
        """

        # If there are no lines in the buffer
        # we are at the end of file for sure.
        if not self.lines:
            return True

        # There might be empty lines, and those
        # should never be mistaken for the EOF.
        # If we are at the last line, and beyond
        # its length we are at the EOF.
        if self.line == len(self.lines) - 1 and self.column >= len(self.current_line):
            return True

        # If we are past the last line
        # we are at the EOF.
        return self.line >= len(self.lines)

    @property
    def eol(self) -> bool:
        """
        True if the position is beyond EOL.
        """
        return self.column >= len(self.current_line)

    @property
    def current_line(self) -> str:
        """
        Returns the current line.

        This property returns the current line without advancing the index.
        If the buffer is reading after the last line it returns an empty string.
        """
        try:
            return self.lines[self.line]
        except IndexError:
            return ""

    @property
    def current_char(self) -> str:
        """
        Returns the current character.

        This property returns the current character without advancing the index.
        If the buffer is reading after the last character of the line
        or after the last line it returns an empty string.
        """
        try:
            return self.current_line[self.column]
        except IndexError:
            return ""

    @property
    def peek_char(self) -> str:
        """
        Returns the next character.

        This property returns the next character without advancing the index.
        If the buffer is reading after the last character of the line
        or after the last line it returns an empty string.
        """

        try:
            return self.current_line[self.column + 1]
        except IndexError:
            return ""

    @property
    def tail(self) -> str:
        """
        Returns the remaining part of the line.

        This property returns a string with the last part of the current
        line from the current character to the end.
        """
        return self.current_line[self.column :]

    @property
    def position(self) -> tuple[int, int]:
        """
        Returns a tuple with the current position.
        """
        return (self.line + self.start_line, self.column + self.start_column)

    def nextline(self):
        """
        Moves the index to the beginning of the next line
        """
        if self.line <= len(self.lines):
            self.line += 1

        # If we go to a new line, the
        # start column should be reset
        # as well. The buffer is not a
        # text box floating in the page.
        self.start_column = 0
        self.column = 0

    def skip(self, chars=1):
        """
        Skips the given number of characters (default 1). Can silently
        go over the end of the line.
        """
        self.column = self.column + chars
