from typing import Callable

from mau.lexers.base_lexer import BaseLexer, rematch
from mau.token import Token, TokenType


class TextLexer(BaseLexer):
    r"""This lexer operates on text blocks
    split into paragraphs.

    Inside Mau paragraphs, the special characters
    are the styles (~^_*`), the escape characters
    ($%\), and the macro characters (()[]").

    The double quotes can be used to include
    parentheses inside macro arguments, so they
    need to be isolated.
    """

    def _process_whitespace(self) -> list[Token] | None:
        # Find any amount of whitespace.
        match = rematch(r" +", self._tail)

        if not match:
            return None

        return [self._create_token_and_skip(TokenType.TEXT, " ")]

    def _process_literal(self) -> list[Token] | None:
        # Find special characters.
        # Please note that the backslash
        # must be escaped, so it's
        # represented as \\.
        #
        # The characters without escapes are
        # ~ ^ _ * ` ( ) [ ] \ " $ %
        if self._current_char not in '~^_*`()[]\\"$%':
            return None

        return [self._create_token_and_skip(TokenType.LITERAL, self._current_char)]

    def _process_text(self) -> list[Token] | None:
        # Find text characters, excluding
        # special characters.
        # Please note that since this is a
        # regular expression, the characters
        # ^ $ \ ] have to be escaped.
        #
        # So, the regexp below is
        # [^CHARACTERS]+
        # where CHARACTERS is
        # ~ ^ _ * ` ( ) [ ] " \ $ % SPACE
        match = rematch(r'[^~\^_*`()[\]"\\\$% ]+', self._tail)

        if not match:  # pragma: no cover
            return None

        return [self._create_token_and_skip(TokenType.TEXT, match.group())]

    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_whitespace,
            self._process_literal,
            self._process_text,
        ]
