import logging
from collections.abc import Callable

from mau.text_buffer import Context
from mau.token import Token, TokenType

logger = logging.getLogger(__name__)


class TokenError(ValueError):
    """
    This is an exception that signals an error
    when processing tokens.

    This can be raised because the user is trying to
    get the current token while there are no tokens
    or if a token check fails.

    The exception is automatically ignored by the
    token manager when used as a context manager.
    """


class TokensManager:
    """This manager collects tokens and provides
    several methods to interact with them.
    """

    def __init__(
        self,
        tokens: list[Token],
    ):
        # This is the index of the current token.
        self.index: int = -1

        # These are the tokens parsed by the parser.
        self.tokens: list[Token] = tokens

        # A stack for the parser's state.
        # Currently the state is represented only
        # by the current index in the input tokens.
        self._stack: list[int] = []

    @property
    def current_token(self) -> Token:
        """
        Returns the token being parsed.
        We often need to know which token we are currently
        parsing, but we might already have parsed all
        of them, so this convenience method wraps the
        possible index error.
        """

        if not self.tokens:
            raise TokenError

        if self.index < 0:
            return self.tokens[-1]

        try:
            return self.tokens[self.index]
        except IndexError:
            return self.tokens[-1]

    def _advance(self):
        if self.index < len(self.tokens):
            self.index += 1

    def __enter__(self):
        # The parser can be used as a context manager.
        # When we enter a new context we just need to
        # push the current state.
        self._stack.append(self.index)

    def __exit__(self, etype, evalue, etrace) -> bool:
        # This is automatically run when we leave the context.
        # The execution of a parser function can either return
        # None or raise an exception.
        # In the first case everything went well, and we can exit
        # the context manager after we restored the stack.
        # In the second case we need to check if the exception
        # is an expected one or not. If the exception is
        # a signal that the function failed we can suppress it.

        # First make sure we leave the stack as it was before
        # we entered the context.
        stacked_index = self._stack.pop()

        # If there was no exception we can exit the
        # context manager and continue execution
        if etype is None:
            return True

        # If there was an exception we need to
        # actually backtrace and pretend we didn't
        # do anything. Be cautious and don't get caught.

        # Restore the original position
        self.index = stacked_index

        # If the exception is not among the managed
        # ones we need to signal that it has to
        # be propagated
        if etype not in [TokenError]:
            return False

        # At this point we know that there was
        # an exception but we can ignore it as
        # it is one of the expected ones
        return True

    def _check_token(
        self,
        token: Token,
        ttype: TokenType | None = None,
        tvalue: str | None = None,
        value_check_function: Callable[[str], bool] | None = None,
    ) -> Token:
        # This method performs a test on the current token,
        # figuring out if type and value correspond to those passed
        # as arguments. If type or value are not given they are not
        # tested.
        # If the test is successful the token is returned, otherwise
        # the TokenError exception is raised.
        # The argument value_check_function is a function that
        # can be passed to test the token value and shall return a boolean.

        check_type = ttype or token.type
        if token.type != check_type:
            raise TokenError

        if tvalue is not None and token.value != tvalue:
            raise TokenError

        if (
            value_check_function is not None
            and value_check_function(token.value) is False
        ):
            raise TokenError

        return token

    def peek_token(
        self,
        ttype: TokenType | None = None,
        tvalue: str | None = None,
        value_check_function: Callable[[str], bool] | None = None,
    ) -> Token:
        """
        Return the next token without advancing the index.

        If the next token doesn't match the given type or value
        the function raises TokenError, that can be intercepted
        by the method parse. This means that the current processing
        function failed, and that the parser should try to
        use the next one.
        """

        try:
            token = self.tokens[self.index + 1]
        except IndexError:
            token = self.tokens[-1]

        return self._check_token(token, ttype, tvalue, value_check_function)

    def get_token(
        self,
        ttype: TokenType | None = None,
        tvalue: str | None = None,
        value_check_function: Callable[[str], bool] | None = None,
    ) -> Token:
        """
        Return the next token and advances the index.
        This function returns the next token and then advances the index,
        and can optionally check its type or value.
        If the check fails the index is not advanced.
        """

        self.peek_token(ttype, tvalue, value_check_function)

        self._advance()

        return self.current_token

    def peek_token_is(
        self,
        ttype: TokenType,
        tvalue: str | None = None,
        value_check_function: Callable[[str], bool] | None = None,
    ) -> bool:
        """
        Peek a token and check it.
        This works like peek_token, but returns a boolean
        instead of raising an exception.
        """

        try:
            self.peek_token(ttype, tvalue, value_check_function)
            return True
        except TokenError:
            return False

    def collect(
        self, stop_tokens: list[Token], preserve_escaped_stop_tokens: bool = False
    ):
        """
        Collect all tokens until one of the stop_tokens pops up.

        The stop token that terminates the collection is added to
        the joined list.

        An escape token (a literal "\\") is processed according
        to the following rules:

        * In front of a normal token it is kept.
        * In front of an escape token it is removed.
        * In front of an escape token with preserve_escaped_stop_tokens on it is kept.
        """
        tokens = []

        # After all, at EOF the world ends.
        stop_tokens.append(Token(TokenType.EOF, "", Context.empty()))

        # This keeps looking at the next token and
        # stops when it is one of the stop ones.
        while self.peek_token() not in stop_tokens:
            # Stop tokens might be escaped, but we
            # consider the escape only if
            # preserve_escaped_stop_tokens is True.
            if self.peek_token() == Token(TokenType.LITERAL, "\\", Context.empty()):
                # Store the literal escape.
                escape = self.get_token()

                # We keep the escaped token if it is not
                # a stop one, or if the preserve flag is on.
                if self.peek_token() not in stop_tokens or preserve_escaped_stop_tokens:
                    tokens.append(escape)

            # Append the next token.
            # This might be a normal token or the escaped
            # one if the logic above added the escape.
            tokens.append(self.get_token())

        return tokens

    def collect_join(
        self,
        stop_tokens: list[Token],
        join_with: str = "",
        preserve_escaped_stop_tokens: bool = False,
    ) -> Token:
        """
        Collect tokens and join them.

        Collect all tokens until one of the stop_tokens
        pops up and join them in a single string.
        This works exactly like collect but returns
        a string of tokens joined with the given characters.
        """

        tokens = self.collect(stop_tokens, preserve_escaped_stop_tokens)

        if not tokens:
            return Token(TokenType.TEXT, "", Context.empty())

        # Some tokens have value None, so this removes them
        token_values = [t.value for t in tokens if t.value != ""]
        value = join_with.join(token_values)

        start_context = tokens[0].context
        end_context = tokens[-1].context
        context = Context.merge_contexts(start_context, end_context)

        return Token(TokenType.TEXT, value, context)
