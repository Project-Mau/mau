import functools

from mau.lexers.base_lexer import BaseLexer, Token, TokenTypes, TokenError, Literal


class ParseError(ValueError):
    pass


class ExpectedError(ParseError):
    pass


# This makes a function return True instead of
# None when successfully executed, which
# makes the parser loop much easier to
# understand
def parser(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        value = func(*args, **kwargs)
        if value is None:
            return True

    return wrapper_decorator


def analyse(parser, text):
    parser.load(text)
    parser.parse()

    return parser


class BaseParser:
    def __init__(self):
        self.lexer = BaseLexer()
        self.index = -1
        self.tokens = []
        self._stack = []
        self.nodes = []

    def _stash(self):
        self._stack.append(self.index)

    def __enter__(self):
        self._stash()

    def __exit__(self, etype, evalue, etrace):
        # Leave the stack as it was before
        # we entered the context
        stacked_index = self._pop()

        if etype:
            # Restore the original position
            self.index = stacked_index

        if etype in [TokenError]:
            return True

    def _pop(self):
        return self._stack.pop()

    def fail(self):
        raise TokenError

    def _save(self, node):
        self.nodes.append(node)

    @property
    def current_token(self):
        try:
            return self.tokens[self.index]
        except IndexError:
            return Token(TokenTypes.EOF)

    def load(self, text):
        self.lexer.process(text)
        self.tokens = self.lexer.tokens
        self.index = -1

    def _check_token(self, token, ttype=None, tvalue=None, check=None):
        check_type = ttype if ttype is not None else token.type

        if token.type != check_type:
            raise TokenError(f"Type of token {token} is not {check_type}")

        if tvalue is not None and token.value != tvalue:
            raise TokenError(f"Value of token {token} is not {tvalue}")
        elif check is not None and check(token.value) is False:
            raise TokenError(f"Value of token {token} didn't pass check")

        return token

    def get_token(self, ttype=None, tvalue=None, check=None):
        """
        Return the next token and advances the index.
        The token is stored it in current_token.
        """

        if self.index == len(self.tokens):
            return Token(TokenTypes.EOF)

        self.index += 1
        return self._check_token(self.current_token, ttype, tvalue, check)

    def get_token_value(self, ttype=None, tvalue=None, check=None):
        """
        A shortcut to get the next token and return the value
        """

        return self.get_token(ttype, tvalue, check).value

    def check_current_token(self, ttype, tvalue=None, check=None):
        """
        Just check the type and value of the current token without
        advancing the index.
        """

        return self._check_token(self.current_token, ttype, tvalue, check)

    def peek_token(self, ttype=None, tvalue=None, check=None):
        """
        Return the next token without advancing the index.
        """

        try:
            token = self.tokens[self.index + 1]
            return self._check_token(token, ttype, tvalue, check)
        except IndexError:
            return Token(TokenTypes.EOF)

    def peek_token_is(self, *args, **kwargs):
        try:
            self.peek_token(*args, **kwargs)
            return True
        except TokenError:
            return False

    def force_token(self, ttype, tvalue=None):
        try:
            return self.get_token(ttype, tvalue)
        except TokenError:
            raise ExpectedError(
                {"expected": Token(ttype, tvalue), "found": self.current_token}
            )

    def force_token_in(self, tokens):
        if self.peek_token() not in tokens:
            raise ExpectedError({"expected": tokens, "found": self.current_token})

    def collect(self, stop_tokens, preserve_escaped_stop_tokens=False):
        tokens = []

        while self.peek_token() not in stop_tokens:
            if self.peek_token() == Literal("\\"):
                escape = self.get_token()

                if self.peek_token() not in stop_tokens or preserve_escaped_stop_tokens:
                    tokens.append(escape)

            tokens.append(self.get_token())

        return tokens

    def collect_join(
        self, stop_tokens, join_with="", preserve_escaped_stop_tokens=False
    ):
        token_values = [
            t.value for t in self.collect(stop_tokens, preserve_escaped_stop_tokens)
        ]
        token_values = [t for t in token_values if t is not None]

        return join_with.join(token_values)

    def parse(self):
        self._parse()

    def _parse(self):
        while not self.peek_token_is(TokenTypes.EOF):
            result = False

            for parse_function in self._parse_functions():
                with self:
                    result = parse_function()

                # We get here both if the context manager
                # was interrupted by the exception or if
                # it finished properly. In this last case,
                # however, the function reached the end
                # and returned True
                if result is True:
                    break

            # If we get here and result is still false
            # we didn't find any function to parse the
            # current token.
            if result is False:
                raise ParseError(f"Cannot parse token {self.peek_token()}")
