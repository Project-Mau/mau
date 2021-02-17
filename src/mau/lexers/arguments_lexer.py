import re

from mau.lexers.base_lexer import BaseLexer, TokenTypes


class ArgumentsLexer(BaseLexer):
    def _process_functions(self):
        return [
            self._process_eof,
            self._process_eol,
            self._process_whitespace,
            self._process_literal,
            self._process_text,
        ]

    def _process_whitespace(self):
        regexp = re.compile(r" +")

        match = regexp.match(self._tail)

        if not match:  # pragma: no cover
            return None

        return self._create_token_and_skip(TokenTypes.WHITESPACE, match.group())

    def _process_literal(self):
        if self._current_char not in r'\=,"':
            return None

        return self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)

    def _process_text(self):
        regexp = re.compile(r'[^\\=," ]+')

        match = regexp.match(self._tail)

        if not match:  # pragma: no cover
            return None

        return self._create_token_and_skip(TokenTypes.TEXT, match.group())

    def process(self, text):
        super().process(text)

        # Remove EOL and EOF
        self.tokens = self.tokens[:-2]
