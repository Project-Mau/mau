import logging
from typing import Callable

from mau.lexers.base_lexer import BaseLexer, rematch
from mau.token import Token, TokenType

logger = logging.getLogger(__name__)


class ConditionLexer(BaseLexer):
    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_condition,
        ]

    def _process_condition(self) -> list[Token] | None:
        # Detect control conditions in the form
        #
        # VAR (==|!=) VALUE
        #
        # This is done to isolate the logic as it is
        # shared between the control operator in the
        # document parser and the macro control in the
        # text parser.

        # Try to match the syntax shown above.
        match = rematch(
            (
                r"(?P<variable>[a-zA-Z0-9_\.\+\-]+)(?P<whitespace1> *)"
                r"(?P<comparison>(==|!=))(?P<whitespace2> *)(?P<value>.*)$"
            ),
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        variable = match.groupdict().get("variable")
        whitespace1 = match.groupdict().get("whitespace1")
        comparison = match.groupdict().get("comparison")
        whitespace2 = match.groupdict().get("whitespace2")
        value = match.groupdict().get("value")

        # Create the tokens we want to keep.
        variable_token = self._create_token_and_skip(TokenType.TEXT, variable)
        self._skip(whitespace1)
        comparison_token = self._create_token_and_skip(TokenType.TEXT, comparison)
        self._skip(whitespace2)
        value_token = self._create_token_and_skip(TokenType.TEXT, value)

        tokens = [
            variable_token,
            comparison_token,
            value_token,
        ]

        return tokens
