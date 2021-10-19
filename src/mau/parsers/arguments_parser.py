from copy import deepcopy

from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.parsers.base_parser import BaseParser, ParserError


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

    def set_names_and_defaults(self, positional_names, default_values=None):
        """
        Gives names to positional arguments and assigns
        default values to the ones that have not been
        initialised.
        """

        if default_values:
            _default_values = default_values.copy()
        else:
            _default_values = {}

        # This happens if we passed too many positional
        # values. The case where we pass less positional
        # values than required is checked later when named
        # arguments are merged.
        if len(self.args) > len(positional_names):
            self.error(
                f"Error while parsing arguments {self.args} through names {positional_names}"
            )

        positional_arguments = dict(zip(positional_names, self.args))

        # Named arguments win over the defaults
        _default_values.update(self.kwargs)

        # Positional arguments with win over all the rest
        _default_values.update(positional_arguments)

        # Positional arguments are mandatory and strict
        # so all the names have to be present in the
        # final dictionary.
        if not set(positional_names).issubset(set(_default_values.keys())):
            self.error(
                f"The following attributes need to be specified: {positional_names}"
            )

        self.kwargs = _default_values
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
                raise ParserError(
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
