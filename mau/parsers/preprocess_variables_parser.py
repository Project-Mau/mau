from mau.lexers.base_lexer import TokenTypes
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.nodes.inline import TextNode
from mau.parsers.base_parser import BaseParser
from mau.tokens.tokens import Token


class PreprocessVariablesParser(BaseParser):
    lexer_class = PreprocessVariablesLexer

    def __init__(self, environment):
        super().__init__(environment)

    def _process_verbatim(self):
        self._get_token(TokenTypes.LITERAL, "`")
        text = self._collect_join(
            [Token(TokenTypes.LITERAL, "`")],
            preserve_escaped_stop_tokens=True,
        )
        self._get_token(TokenTypes.LITERAL, "`")

        text = f"`{text}`"

        self._save(TextNode(text))

        return True

    def _process_escaped_char(self):
        self._get_token(TokenTypes.LITERAL, "\\")

        char = self._get_token().value

        if char not in "{}":
            char = f"\\{char}"

        self._save(TextNode(char))

        return True

    def _process_curly(self):
        self._get_token(TokenTypes.LITERAL, "{")
        variable_name = self._collect_join(stop_tokens=[Token(TokenTypes.LITERAL, "}")])
        self._get_token(TokenTypes.LITERAL, "}")

        try:
            variable_value = self.environment.getvar_nodefault(variable_name)

            # Boolean variables are used in
            # conditions but shouldn't be printed
            if variable_value in [True, False]:
                variable_value = ""

            self._save(TextNode(variable_value))
        except KeyError:
            self._error(f'Attribute "{variable_name}" has not been defined')

        return True

    def _process_pass(self):
        self._save(TextNode(self._get_token().value))

        return True

    def _process_functions(self):
        return [
            self._process_escaped_char,
            self._process_verbatim,
            self._process_curly,
            self._process_pass,
        ]

    def parse(self, tokens):
        super().parse(tokens)

        # After having parsed the text and replaced the
        # variables, this should return a piece of text again
        text = "".join([str(i.value) for i in self.nodes])
        self.nodes = [TextNode(text)]
