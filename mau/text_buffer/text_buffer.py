from typing import Optional, Tuple

from mau.text_buffer.context import Context

Position = Tuple[int, int]

# The TextBuffer is an object used to interact with a text file.
#
# The object contains by default an empty piece of text and no
# initial context, but it can accept both at initialisation time.
#
# The object itself doesnt interact with files, the text content
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
    def __init__(self, text: str = "", context: Optional[Context] = None):
        self.lines: list[str] = []
        self.load(text, context)

    def load(self, text: str, context: Optional[Context] = None) -> None:
        self.lines = text.split("\n") if text != "" else []

        self.initial_context = context or Context()
        self.line = 0
        self.column = 0

    @property
    def context(self) -> Context:
        return Context(
            line=self.line + self.initial_context.line,
            column=self.column + self.initial_context.column,
            source=self.initial_context.source,
            text=self.current_line,
        )

    @property
    def eof(self) -> bool:
        """
        True if the position is beyond EOF.
        """
        return self.line >= len(self.lines)

    @property
    def eol(self):
        """
        True if the position is beyond EOL.
        """
        return self.column >= len(self.current_line)

    @property
    def current_line(self):
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
    def current_char(self):
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
    def peek_char(self):
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
    def tail(self):
        """
        Returns the remaining part of the line.

        This property returns a string with the last part of the current
        line from the current character to the end.
        """
        return self.current_line[self.column :]

    @property
    def position(self):
        """
        Returns a tuple with the current position.
        """
        return (self.line, self.column)

    @position.setter
    def position(self, position: Position):
        """
        Sets the current position.
        """
        self.line, self.column = position

    def nextline(self):
        """
        Moves the index to the beginning of the next line
        """
        if self.line <= len(self.lines):
            self.line += 1

        self.column = 0

    def skip(self, chars=1):
        """
        Skips the given number of characters (default 1). Can silently
        go over the end of the line.
        """
        new_column = self.column + chars

        if new_column > len(self.current_line):
            new_column = len(self.current_line)

        self.column = new_column
