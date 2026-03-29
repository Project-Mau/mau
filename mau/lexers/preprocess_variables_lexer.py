from typing import Callable

from mau.lexers.base_lexer import BaseLexer, rematch
from mau.token import Token, TokenType


class PreprocessVariablesLexer(BaseLexer):
    r"""This lexer has been designed to work on
    strings of text (single lines). It detects
    the characters {} that might surround a
    variable, the escape \, or the backtick `.
    """

    def _process_literal(self) -> list[Token] | None:
        # Spot if the current character is one
        # among \`{}. These will be useful to the
        # parser as they might contain
        # variables or escaped variables.

        # If the current char is not special
        # just return.
        if self._current_char not in r"\`{}":
            return None

        return [self._create_token_and_skip(TokenType.LITERAL, self._current_char)]

    def _process_text(self) -> list[Token] | None:
        # Anything that is not a special character
        # can be collected under the generic name
        # of "text".
        match = rematch(r"[^\\`{}]+", self._tail)

        if not match:  # pragma: no cover
            return None

        return [self._create_token_and_skip(TokenType.TEXT, match.group())]

    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_literal,
            self._process_text,
        ]
