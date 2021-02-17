class EOLError(ValueError):

    """ Signals that the buffer is reading after the end of a line."""


class EOFError(ValueError):

    """ Signals that the buffer is reading after the end of the text."""


class TextBuffer:
    def __init__(self, text=None):
        self.lines = []
        self.reset()

        if text is not None:
            self.load(text)

    def reset(self):
        self.line = 0
        self.column = 0

    def load(self, text):
        self.lines = text.split("\n") if text is not None else []
        self.reset()

    @property
    def current_line(self):
        """
        Returns the current line.

        This property returns the current line without advancing the index.
        If the buffer is reading after the last line it raises EOFError.
        """
        try:
            return self.lines[self.line]
        except IndexError:
            raise EOFError("EOF reading line {}".format(self.line))

    @property
    def current_char(self):
        """
        Returns the current character.

        This property returns the current character without advancing the index.
        If the buffer is reading after the last character of the line it raises EOLError.
        """
        try:
            return self.current_line[self.column]
        except IndexError:
            raise EOLError(
                "EOL reading column {} at line {}".format(self.column, self.line)
            )

    @property
    def peek_char(self):
        """
        Returns the next character.

        This property returns the next character without advancing the index.
        If the buffer is reading after the last character of the line it raises EOLError.
        """

        try:
            return self.current_line[self.column + 1]
        except IndexError:
            raise EOLError(
                "EOL reading column {} at line {}".format(self.column, self.line)
            )

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
    def position(self, position):
        """
        Sets the current position.
        """
        self.line, self.column = position

    def nextline(self):
        """
        Moves the index to the beginning of the next line
        """
        self.line += 1
        self.column = 0

    def skip(self, chars=1):
        """
        Skips the given number of characters (default 1). Can silently
        go over the end of the line.
        """
        self.column += chars

    def goto(self, line, column=0):
        self.line, self.column = line, column

    def context(self, ctxline, ctxcolumn):
        CONTEXT_CHARACTERS = 20
        ctx = []

        last_line_len = len(f"{ctxline}")
        additional = last_line_len
        marker_position = ctxcolumn

        lines = [ctxline - 1, ctxline]

        lower_flag = False
        lower = max(ctxcolumn - CONTEXT_CHARACTERS, 0)
        if lower > 0:
            lower_flag = True
            additional += 6

        for i in lines:
            line_num = str(i).rjust(last_line_len, "0")
            line = self.lines[i]

            higher_flag = False
            higher = min(ctxcolumn + CONTEXT_CHARACTERS + 1, len(line))
            if higher < len(line):
                higher_flag = True

            line = line[lower:higher]

            if lower_flag:
                line = "[...] " + line

            if higher_flag:
                line = line + " [...]"

            ctx.append(f"{line_num}: {line}")

        additional += 2  # because of ": "
        marker_line = " " * (marker_position - lower + additional) + "^"

        ctx.append(marker_line)
        return ctx
