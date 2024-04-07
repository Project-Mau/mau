# This is a base class for parsers that collects common methods

from mau.errors import MauError, MauErrorException
from mau.lexers.base_lexer import BaseLexer, TokenTypes
from mau.parsers.arguments import set_names_and_defaults
from mau.text_buffer.context import print_context
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token


class TokenError(ValueError):
    """
    This is an exception that parsers ca use to signal
    that the current function cannot process the upcoming
    tokens.
    This means that the parser as a context manager
    must reset the index, but also that the exception
    must not be propagated.
    """


class MauParserError(MauError):
    source = "parser"

    def print_details(self):  # pragma: no cover
        super().print_details()

        context = self.details["context"]
        print_context(context)


class BaseParser:
    text_buffer_class = TextBuffer
    lexer_class = BaseLexer

    def __init__(self, environment, parent_node=None, parent_position=None):
        # This is the position of the current token.
        self.index = -1

        # These are the tokens parsed by the parser.
        self.tokens = None

        # A stack for the parser's state.
        # Currently the state is represented only
        # by the current index in the input tokens.
        self._stack = []

        # These are the nodes created by the parsing.
        self.nodes = []

        # The last processed token. Used to detect loops.
        self.last_processed_token = Token(TokenTypes.EOF)

        # The configuration environment
        self.environment = environment

        # This is the parent node of all the nodes
        # created by this parser
        self.parent_node = parent_node

        # This is the position of all the nodes
        # in the parent
        self.parent_position = parent_position

    @property
    def _current_token(self):
        """
        Returns the token being parsed.
        We often need to know which token we are currently
        parsing, but we might already have parsed all
        of them, so this convenience method wraps the
        possible index error.
        """
        if not self.tokens:
            return None

        if self.index < 0:
            return self.tokens[-1]

        try:
            return self.tokens[self.index]
        except IndexError:
            return self.tokens[-1]

    def _advance(self):
        if self.index != len(self.tokens):
            self.index += 1

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
        # The execution of a parser function can either return
        # None or raise an exception.
        # In the first case everything went well, and we can exit
        # the context manager after we restored the stack.
        # In the second case we need to check if the exception
        # is an expected one or not. If the exception is
        # a signal that the function failed we can suppress it.

        # First make sure we leave the stack as it was before
        # we entered the context.
        stacked_index = self._pop()

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

    def _save(self, node):
        # Store the node.
        node.parent = self.parent_node

        self.nodes.append(node)

    def save(self, node):
        # Store the node.
        self.nodes.append(node)

    def _check_token(
        self,
        token,
        ttype=None,
        tvalue=None,
        value_check_function=None,
    ):
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

        if (
            value_check_function is not None
            and value_check_function(token.value) is False
        ):
            raise TokenError(f"Value of token {token} didn't pass check")

        return token

    def _process_functions(self):
        # The parse functions available in this parser
        return []

    def _error(self, message=None):
        context = None
        if self._current_token:
            context = self._current_token.context

        error = MauParserError(
            message=message,
            details={
                "context": context,
            },
        )

        raise MauErrorException(error)

    def _put_token(self, token):
        self.tokens.insert(self.index + 1, token)

    def _get_token(self, ttype=None, tvalue=None, check=None):
        """
        Return the next token and advances the index.
        This function returns the next token and then advances the index,
        and can optionally check its type or value (see _check_token).
        """

        self._advance()

        return self._check_token(self._current_token, ttype, tvalue, check)

    def _check_current_token(self, ttype, tvalue=None, check=None):
        """
        Just check the type and value of the current token without
        advancing the index.
        """

        return self._check_token(self._current_token, ttype, tvalue, check)

    def _peek_token(self, ttype=None, tvalue=None, check=None):
        """
        Return the next token without advancing the index.
        """

        try:
            token = self.tokens[self.index + 1]
        except IndexError:
            token = self.tokens[-1]

        return self._check_token(token, ttype, tvalue, check)

    def _peek_token_is(self, ttype=None, tvalue=None, check=None):
        """
        Peek a token and check it.
        This works like peek_token, but returns a boolean
        instead of raising an exception.
        """
        try:
            self._peek_token(ttype, tvalue, check)
            return True
        except TokenError:
            return False

    def _force_token(self, ttype, tvalue=None):
        """
        Return the next token and advances the index,
        but forces the token to have a specific type
        and optionally a value.
        If the token doesn't match the provided values
        the function raises and error
        """
        try:
            token = self._get_token(ttype, tvalue)
        except TokenError:
            if tvalue is not None:
                self._error(f"Expected token of type {ttype} with value '{tvalue}'")
            else:
                self._error(f"Expected token of type {ttype}")

        return token

    def _collect(self, stop_tokens, preserve_escaped_stop_tokens=False):
        """
        Collect all tokens until one of the stop_tokens pops up.

        Escaped tokens (preceded by a literal "\\") are kept as they are.
        If a stop token is escaped it is included only if
        preserve_escaped_stop_tokens is set to True.
        """
        tokens = []

        # After all, at EOF the world ends.
        stop_tokens.append(Token(TokenTypes.EOF))

        while self._peek_token() not in stop_tokens:
            if self._peek_token() == Token(TokenTypes.LITERAL, "\\"):
                escape = self._get_token()

                if (
                    self._peek_token() not in stop_tokens
                    or preserve_escaped_stop_tokens
                ):
                    tokens.append(escape)

            tokens.append(self._get_token())

        return tokens

    def _collect_join(
        self,
        stop_tokens,
        join_with="",
        preserve_escaped_stop_tokens=False,
    ):
        """
        Collect all tokens until one of the stop_tokens
        pops up and join them in a single string.
        This works exactly like collect but returns
        a string of tokens joined with the given characters.
        """

        # Some tokens have value None, so this removes them
        token_values = [
            t.value
            for t in self._collect(stop_tokens, preserve_escaped_stop_tokens)
            if t.value != ""
        ]

        return join_with.join(token_values)

    # pylint: disable=inconsistent-return-statements
    def _set_names_and_defaults(
        self,
        args,
        kwargs,
        positional_names,
        default_values=None,
    ):  # pragma: no cover
        try:
            return set_names_and_defaults(
                args, kwargs, positional_names, default_values
            )
        except ValueError as exception:
            self._error(str(exception))

    def parse(self, tokens):
        """
        Run the parser on the lexed tokens.
        """

        self.tokens = tokens

        # A loop on all lexed tokens until we reach EOF
        while not self._peek_token_is(TokenTypes.EOF):
            # This detects infinite loops created by incomplete
            # parsing functions. Those functions keep trying
            # to parse the same token, so if we spot that
            # we are doing it we should raise an error.
            next_token = self._peek_token()
            if next_token.match(self.last_processed_token):
                self._error("Loop detected, cannot parse token")  # pragma: no cover
            else:
                self.last_processed_token = next_token

            # Here we run all parsing functions provided by
            # the parser until one returns a sensible result
            result = False
            for process_function in self._process_functions():
                # The context manager wraps the function so that
                # any exception leaves the parsed tokens as they
                # were at the beginning of the function execution.
                #
                # If the parse function is successful it returns
                # True. If the function raises an exception the
                # variable result is not set and the value is False.
                # Any other result returned by the function
                # is ignored.
                with self:
                    result = process_function()

                if result is True:
                    # True means the function was successful
                    # and we can stop the loop.
                    break

            # If we get here and result is still False
            # we didn't find any function to parse the
            # current token.
            if result is False:
                self._error("Cannot parse token")

    @classmethod
    def analyse(cls, text, context, environment, *args, **kwargs):
        text_buffer = cls.text_buffer_class(text, context)

        lex = cls.lexer_class(environment)
        lex.process(text_buffer)

        par = cls(environment, *args, **kwargs)
        par.parse(lex.tokens)

        return par

    def finalise(self):
        pass
