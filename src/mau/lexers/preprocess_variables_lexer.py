import re

from mau import text_buffer
from mau.lexers.base_lexer import BaseLexer, Token, TokenTypes


class PreprocessVariablesLexer(BaseLexer):
    def _process_eol(self):
        try:
            self._current_char
        except text_buffer.EOLError:
            self._nextline()
            return Token(TokenTypes.TEXT, "\n")

    def _process_literal(self):
        if self._current_char not in r"\`{}":
            return None

        return self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)

    def _process_text(self):
        return self._create_token_and_skip(TokenTypes.TEXT, self._current_char)

    def _process_functions(self):
        return [
            self._process_eof,
            self._process_eol,
            self._process_literal,
            self._process_text,
        ]

    def process(self, text):
        super().process(text)

        self.tokens = self.tokens[:-1]
