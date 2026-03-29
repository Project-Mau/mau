from __future__ import annotations

from enum import Enum

from mau.text_buffer import Context


class TokenType(Enum):
    ARGUMENTS = "ARGUMENTS"
    BLOCK = "BLOCK"
    COMMENT = "COMMENT"
    CONTROL = "CONTROL"
    EMPTY = "EMPTY"
    EOF = "EOF"
    EOL = "EOL"
    HEADER = "HEADER"
    HORIZONTAL_RULE = "HORIZONTAL_RULE"
    INCLUDE = "INCLUDE"
    LIST = "LIST"
    # Characters with specific syntax value like
    # commas to separate between arguments, colons,
    # double quotes, etc.
    LITERAL = "LITERAL"
    MULTILINE_COMMENT = "MULTILINE_COMMENT"
    # Free text without a specific value in
    # the language
    TEXT = "TEXT"
    LABEL = "LABEL"
    VARIABLE = "VARIABLE"
    WHITESPACE = "WHITESPACE"


class Token:
    """This class represents a lexer token.

    Tokens have a type, a value (the actual characters), and a context.
    """

    def __init__(
        self,
        _type: TokenType,
        value: str,
        context: Context,
    ):
        self.type = _type
        self.value = value
        self.context = context

    @classmethod
    def generate(cls, ttype: TokenType, value: str = ""):
        """Generate a token without a context."""
        return Token(ttype, value, Context.empty())

    @classmethod
    def from_token_list(cls, tokens: list[Token], join_with: str = "") -> Token:
        """Convert a list of TEXT tokens into a single
        TEXT token joining the values of all tokens and
        merging their contexts."""

        # If there are no tokens in the list
        # we output an empty token
        if not tokens:
            return Token(TokenType.TEXT, "", Context.empty())

        # Get the context of the first token, this
        # will mark the starting position.
        start_context = tokens[0].context

        # Get the context of the last token, this
        # will mark the end position.
        end_context = tokens[-1].context

        # Build the final context merging the two.
        context = Context.merge_contexts(start_context, end_context)

        # Build the token value joining their
        # values of all the tokens in the list.
        value = join_with.join([t.value for t in tokens])

        return Token(TokenType.TEXT, value, context)

    def to_token_list(self) -> list[Token]:
        """Split a TEXT token into a list of TEXT tokens."""

        # Split the token value into lines.
        token_lines = self.value.split("\n")

        # Prepare an empty list to host the resulting tokens.
        result: list[Token] = []

        # Process each line. Keep track of the line
        # number to adjust the context.

        for line_number, line_content in enumerate(token_lines):
            # Clone the context of the source token and
            # move it to the beginning of the current line.
            context = self.context.clone().move_to(line_number, 0)

            # Make sure the size of the token is correct in the context.
            context.end_column = context.start_column + len(line_content)

            # Since we split the text line by line
            # the context spans a single line.
            context.end_line = context.start_line

            # Create the token for this line and
            # append it to the results list.
            result.append(Token(TokenType.TEXT, line_content, context))

        return result

    def asdict(self):
        return {
            "type": self.type,
            "value": self.value,
            "context": self.context.asdict(),
        }

    def __repr__(self):
        return f'Token({self.type}, "{self.value}", {self.context})'

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False

        return (self.type, self.value) == (
            other.type,
            other.value,
        )

    def __hash__(self):
        return hash((self.type, self.value))

    def __len__(self):
        if self.value:
            return len(self.value)

        return 0


EOF = Token.generate(TokenType.EOF)
EOL = Token.generate(TokenType.EOL)
