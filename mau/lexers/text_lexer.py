from mau.helpers import rematch
from mau.lexers.base_lexer import BaseLexer, TokenTypes


class TextLexer(BaseLexer):
    def _process_whitespace(self):
        match = rematch(r"\ +", self._tail)

        if not match:
            return None

        return [self._create_token_and_skip(TokenTypes.TEXT, " ")]

    def _process_literal(self):
        if self._current_char not in '~^_*`{}()[]\\"$%':
            return None

        return [self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)]

    def _process_text(self):
        match = rematch(r'[^~\^_*`{}()[\]"\\ \$%]+', self._tail)

        if not match:  # pragma: no cover
            return None

        return [self._create_token_and_skip(TokenTypes.TEXT, match.group())]

    def _process_functions(self):
        return [
            self._process_whitespace,
            self._process_literal,
            self._process_text,
        ]
