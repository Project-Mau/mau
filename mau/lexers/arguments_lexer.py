from mau.helpers import rematch
from mau.lexers.base_lexer import BaseLexer, TokenTypes


class ArgumentsLexer(BaseLexer):
    def _process_functions(self):
        return [
            self._process_whitespace,
            self._process_literal,
            self._process_text,
        ]

    def _process_whitespace(self):
        match = rematch(r" +", self._tail)

        if not match:
            return None

        return [self._create_token_and_skip(TokenTypes.WHITESPACE, match.group())]

    def _process_literal(self):
        if self._current_char not in r'\=,"':
            return None

        return [self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)]

    def _process_text(self):
        match = rematch(r'[^\\=," ]+', self._tail)

        if not match:  # pragma: no cover
            return None

        return [self._create_token_and_skip(TokenTypes.TEXT, match.group())]
