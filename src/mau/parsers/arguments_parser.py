from copy import deepcopy

from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.parsers.base_parser import BaseParser, ParseError


# The ArgumentsParser is used to parse
# unnamed and named arguments passed to macros.
# It parses a string into a list of unnamed
# arguments and a dictionary of named ones.
class ArgumentsParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.lexer = ArgumentsLexer()

        # This flag is turned on as soon as
        # a named argument is parsed
        self._named_arguments = False

        self.kwargs = {}
        self.args = []

    def apply_prototype(self, positional_names, default_values):
        # This happens if we passed too many positional
        # values. The case where we pass less positional
        # values than required is checked later when named
        # arguments are merged.
        if len(self.args) > len(positional_names):
            raise ParseError

        positional_arguments = dict(zip(positional_names, self.args))
        default_values.update(self.kwargs)
        default_values.update(positional_arguments)

        # Positional arguments are mandatory and strict
        if not set(positional_names).issubset(set(default_values.keys())):
            raise ParseError

        self.kwargs = default_values
        self.args = []

    def merge_unnamed_args(self, names):
        """
        Give a name to unnamed args.
        This creates keys in the kwargs with
        the values of unnamed arguments.
        Already existing keys are not
        overwritten.
        """

        if len(self.args) > len(names):
            raise ParseError(
                f"Too many values. Required arguments: {names} - values: {self.args}"
            )

        _kwargs = dict(zip(names, self.args))

        self.kwargs.update(_kwargs)

        self.args = []

    def pop(self):
        """
        Return the first unnamed argument,
        removing it from the list.
        If no arguments are available it
        returns None.
        """
        try:
            return self.args.pop(0)
        except IndexError:
            return None

    def get_arguments_and_reset(self):
        args = deepcopy(self.args)
        kwargs = deepcopy(self.kwargs)

        self.args = []
        self.kwargs = {}
        self._named_arguments = False

        return args, kwargs

    def _parse_named_argument(self):
        # This parses a named argument
        # in the form name=value or name="value"

        name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "=")

        # Values can be surrounded by quotes
        if self.peek_token_is(TokenTypes.LITERAL, '"'):
            self.get_token(TokenTypes.LITERAL, '"')
            value = self.collect_join([Token(TokenTypes.LITERAL, '"')])
            self.get_token(TokenTypes.LITERAL, '"')
        else:
            value = self.collect_join(
                [Token(TokenTypes.LITERAL, ","), Token(TokenTypes.EOF)]
            )

        return name, value

    def _parse_unnamed_argument(self):
        # This parses a named argument
        # in the form value or "value"

        # Values can be surrounded by quotes
        if self.peek_token_is(TokenTypes.LITERAL, '"'):
            self.get_token(TokenTypes.LITERAL, '"')
            value = self.collect_join([Token(TokenTypes.LITERAL, '"')])
            self.get_token(TokenTypes.LITERAL, '"')
        else:
            value = self.collect_join(
                [Token(TokenTypes.LITERAL, ","), Token(TokenTypes.EOF)]
            )

        return value

    def _parse_single_argument(self):
        # This parses a single argument, named or unnamed

        with self:
            name, value = self._parse_named_argument()
            self.kwargs[name] = value
            self._named_arguments = True
            return

        with self:
            value = self._parse_unnamed_argument()

            if self._named_arguments:
                raise ParseError(
                    "Unnamed arguments after named arguments are forbidden"
                )

            self.args.append(value)
            return

    def _parse_arguments(self):
        # Just run until you can't find any more commas

        while True:
            self._parse_single_argument()

            with self:
                self.get_token(TokenTypes.LITERAL, ",")
                with self:
                    self.get_token(TokenTypes.WHITESPACE)
                continue

            break

    def parse(self):
        self._parse_arguments()
