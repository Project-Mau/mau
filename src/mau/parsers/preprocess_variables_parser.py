from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.parsers.base_parser import BaseParser, parser
from mau.parsers.nodes import TextNode


class PreprocessError(ValueError):
    pass


class PreprocessVariablesParser(BaseParser):
    def __init__(self, variables=None):
        super().__init__()

        self.lexer = PreprocessVariablesLexer()

        self._text = []
        self.variables = variables or {}

    @parser
    def _parse_verbatim(self):
        self.get_token(TokenTypes.LITERAL, "`")
        text = self.collect_join(
            [Token(TokenTypes.LITERAL, "`"), Token(TokenTypes.EOF)],
            preserve_escaped_stop_tokens=True,
        )
        self.get_token(TokenTypes.LITERAL, "`")

        text = f"`{text}`"

        self._save(TextNode(text))

    @parser
    def _parse_escaped_char(self):
        self.get_token(TokenTypes.LITERAL, "\\")

        char = self.get_token().value

        if char not in "{}":
            char = f"\\{char}"

        self._save(TextNode(char))

    @parser
    def _parse_curly(self):
        variable_name = []
        self.get_token(TokenTypes.LITERAL, "{")
        variable_name = self.collect_join(
            [Token(TokenTypes.LITERAL, "}"), Token(TokenTypes.EOF)]
        )
        self.get_token(TokenTypes.LITERAL, "}")

        try:
            if "." not in variable_name:
                variable_value = self.variables[variable_name]
            else:
                namespace, variable_name = variable_name.split(".")

                variable_value = self.variables[namespace][variable_name]

            self._save(TextNode(variable_value))
        except KeyError:
            raise PreprocessError(f'Attribute "{variable_name}" has not been defined')

    @parser
    def _parse_pass(self):
        self._save(TextNode(self.get_token().value))

    def _parse_functions(self):
        return [
            self._parse_escaped_char,
            self._parse_verbatim,
            self._parse_curly,
            self._parse_pass,
        ]

    def parse(self):
        self._parse()
        text = "".join([str(i.value) for i in self.nodes])
        self.nodes = [TextNode(text)]
