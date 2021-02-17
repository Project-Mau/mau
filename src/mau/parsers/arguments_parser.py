from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.parsers.base_parser import BaseParser, ParseError


def merge_args(args, kwargs, names):
    named_args = {}

    for i, name in enumerate(names):
        try:
            named_args[name] = args[i]
        except IndexError:
            pass

    named_args.update(kwargs)

    return [], named_args


class ArgumentsParser(BaseParser):
    def __init__(self, raw=False):
        super().__init__()
        self.lexer = ArgumentsLexer()
        self.raw = raw
        self._named_arguments = False
        self.kwargs = {}
        self.args = []

    def _parse_named_argument(self):
        name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "=")

        if self.peek_token_is(TokenTypes.LITERAL, '"'):
            self.get_token(TokenTypes.LITERAL, '"')
            value = self.collect_join([Token(TokenTypes.LITERAL, '"')])
            self.get_token(TokenTypes.LITERAL, '"')
        else:
            value = self.get_token(TokenTypes.TEXT).value

        return name, value

    def _parse_unnamed_argument(self):
        if self.peek_token_is(TokenTypes.LITERAL, '"'):
            self.get_token(TokenTypes.LITERAL, '"')
            value = self.collect_join([Token(TokenTypes.LITERAL, '"')])
            self.get_token(TokenTypes.LITERAL, '"')
        else:
            value = self.get_token(TokenTypes.TEXT).value

        return value

    def _parse_single_argument(self):
        if self.raw:
            value = self.collect_join([Token(TokenTypes.EOL), Token(TokenTypes.EOF)])
            self.args.append(value)
            return

        with self:
            name, value = self._parse_named_argument()
            self.kwargs[name] = value
            self._named_arguments = True
            return

        if self._named_arguments:
            raise ParseError("Unnamed arguments after named arguments are forbidden")

        with self:
            value = self._parse_unnamed_argument()
            self.args.append(value)
            return

    def _parse_arguments(self):
        with self:
            while True:
                self._parse_single_argument()

                with self:
                    self.get_token(TokenTypes.LITERAL, ",")
                    with self:
                        self.get_token(TokenTypes.WHITESPACE)
                    continue

                break

    def _parse(self):
        self._parse_arguments()
