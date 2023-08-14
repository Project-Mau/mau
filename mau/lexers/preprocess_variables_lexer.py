from mau.lexers.base_lexer import BaseLexer, TokenTypes


class PreprocessVariablesLexer(BaseLexer):
    def _process_literal(self):
        if self._current_char not in r"\`{}":
            return None

        return [self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)]

    def _process_text(self):
        return [self._create_token_and_skip(TokenTypes.TEXT, self._current_char)]

    def _process_functions(self):
        return [
            self._process_literal,
            self._process_text,
        ]
