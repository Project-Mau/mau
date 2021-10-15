# This is a base class for parsers that collects common methods

import functools

from mau.lexers.base_lexer import BaseLexer, Token, TokenTypes, Literal


class TokenError(ValueError):
    """This is used by the parser to exit the context."""


class ConfigurationError(ValueError):
    """This is a configuration error."""


class ParserError(ValueError):
    """This is a detailed parser error"""

    def __init__(self, message=None, context=None):
        super().__init__(message)

        self.context = context


class ExpectedError(ParserError):
    """This exception signals that we were expecting a different token."""


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


class BaseParser:
    def __init__(self):
        self.lexer = BaseLexer()

        # This is the position of the current token.
        self.index = -1

        # These are the tokens parsed by the parser.
        self.tokens = []

        # A stack for the parser's state.
        # Currently the state is represented only
        # by the current index in the input tokens.
        self._stack = []

        # These are the nodes created by the parsing.
        self.nodes = []

    @property
    def current_token(self):
        """
        Returns the token being parsed.
        We often need to know which token we are currently
        parsing, but we might already have parsed all
        of them, so this convenience method wraps the
        possible index error.
        """
        if self.index < 0:
            raise ValueError("The parser has no current token")

        try:
            return self.tokens[self.index]
        except IndexError:
            return Token(TokenTypes.EOF)

    def _push(self):
        # Push the current state on the stack.
        self._stack.append(self.index)

    def _pop(self):
        # Get the state from the stack.
        return self._stack.pop()

    def __enter__(self):
        # The parser can be used as a context manager.
        # When we enter a new context we just need to
        # push the current state.
        self._push()

    def __exit__(self, etype, evalue, etrace):
        # This is automatically run when we leave the context.

        # First make sure we leave the stack as it was before
        # we entered the context.
        stacked_index = self._pop()

        # If there was an exception we need to
        # actually backtrace and pretend we didn't
        # do anything. Be cautious and don't get caught.
        if etype:
            # Restore the original position
            self.index = stacked_index

        # If the exception was one of the ones
        # we manage, let's return True so that
        # the exception is not propagated and
        # Python won't be bothered.
        if etype in [TokenError]:
            return True

    def _save(self, node):
        # Store the node.
        self.nodes.append(node)

    def _check_token(self, token, ttype=None, tvalue=None, value_check_function=None):
        # This method performs a test on the current token,
        # figuring out if type and value correspond to those passed
        # as arguments. If type or value are not given they are not
        # tested.
        # If the test is successful the token is returned, otherwise
        # the TokenError exception is raised.
        # The argument value_check_function is a function that
        # can be passed to test the token value and shall return a boolean.

        check_type = ttype if ttype is not None else token.type
        if token.type != check_type:
            raise TokenError(f"Type of token {token} is not {check_type}")

        if tvalue is not None and token.value != tvalue:
            raise TokenError(f"Value of token {token} is not {tvalue}")
        elif (
            value_check_function is not None
            and value_check_function(token.value) is False
        ):
            raise TokenError(f"Value of token {token} didn't pass check")

        return token

    def _parse_functions(self):
        # The parse functions available in this parser
        return []

    def error(self, message=None):
        raise ParserError(message, context=self.lexer.context(self.current_token))

    def put_token(self, token):
        self.tokens.insert(self.index + 1, token)

    def get_token(self, ttype=None, tvalue=None, check=None):
        """
        Return the next token and advances the index.
        This function returns the next token and then advances the index,
        and can optionally check its type or value (see _check_token).
        The token is stored it in self._current_token.
        """

        if self.index == len(self.tokens):
            return Token(TokenTypes.EOF)

        self.index += 1
        return self._check_token(self.current_token, ttype, tvalue, check)

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

    def peek_token_is(self, ttype=None, tvalue=None, check=None):
        """
        Peek a token and check it.
        This works like peek_token, but returns a boolean
        instead of raising an exception.
        """
        try:
            self.peek_token(ttype, tvalue, check)
            return True
        except TokenError:
            return False

    def force_token(self, ttype, tvalue=None):
        """
        Return the next token and advances the index,
        but forces the token to have a specific type
        and optionally a value.
        If the token doesn't match the provided values
        the function raises an ExpectedError
        """
        try:
            return self.get_token(ttype, tvalue)
        except TokenError:
            raise ExpectedError(
                {"expected": Token(ttype, tvalue), "found": self.current_token}
            )

    def collect(self, stop_tokens, preserve_escaped_stop_tokens=False):
        """
        Collect all tokens until one of the stop_tokens pops up.
        Escape tokens "\\" are removed unless
        preserve_escaped_stop_tokens is set to True.
        """
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
        """
        Collect all tokens until one of the stop_tokens
        pops up and join them in a single string.
        This works exactly like collect but returns
        a string of tokens joined with the given characters.
        """
        token_values = [
            t.value for t in self.collect(stop_tokens, preserve_escaped_stop_tokens)
        ]

        # EOL tokens have value None, so this removes them
        token_values = [t for t in token_values if t is not None]

        return join_with.join(token_values)

    def load(self, text):
        """
        Load the given text and run the lexer on it.
        """

        # Run the lexer
        self.lexer.process(text)

        # Store the resulting tokens
        self.tokens = self.lexer.tokens

        # Reset the index
        self.index = -1

    def parse(self):
        """
        Run the parser on the lexed tokens.
        """

        # A loop on all lexed tokens until we reach EOF
        while not self.peek_token_is(TokenTypes.EOF):
            result = False

            # Run all parsing functions provided
            # by the parser until one returns
            # a sensible result
            for parse_function in self._parse_functions():
                # The context manager wraps the parse
                # function so that failing functions
                # leave the parsed tokens as they were
                # at the beginning of their execution.
                # The result of a parse function is True
                # only if the function finished properly.
                # If the parse function raised an exception
                # the result is False.
                with self:
                    result = parse_function()

                if result is True:
                    break

            # If we get here and result is still False
            # we didn't find any function to parse the
            # current token.
            if result is False:
                self.error("Cannot parse token")

    def analyse(self, text):
        self.load(text)
        self.parse()

        return self
