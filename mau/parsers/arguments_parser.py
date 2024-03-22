from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.lexers.base_lexer import TokenTypes
from mau.nodes.arguments import NamedArgumentNode, UnnamedArgumentNode
from mau.parsers.base_parser import BaseParser
from mau.tokens.tokens import Token


class ArgumentsParser(BaseParser):
    lexer_class = ArgumentsLexer

    def __init__(self, environment):
        super().__init__(environment)

        # This flag is turned on as soon as
        # a named argument is parsed
        self._named_arguments = False

    def _process_functions(self):
        return [
            self._process_eol,
            self._process_named_argument,
            self._process_unnamed_argument,
        ]

    def _process_eol(self):
        # This simply parses the end of line, ignoring it

        self._get_token(TokenTypes.EOL)

        return True

    def _process_named_argument(self):
        # This parses a named argument

        key = self._get_token(TokenTypes.TEXT).value
        self._get_token(TokenTypes.LITERAL, "=")

        # Values can be surrounded by quotes
        if self._peek_token_is(TokenTypes.LITERAL, '"'):
            self._get_token(TokenTypes.LITERAL, '"')
            value = self._collect_join([Token(TokenTypes.LITERAL, '"')])
            self._get_token(TokenTypes.LITERAL, '"')
        else:
            value = self._collect_join([Token(TokenTypes.LITERAL, ",")])

        # The comma is not there after the last argument
        with self:
            self._get_token(TokenTypes.LITERAL, ",")

        # Leading spaces are removed
        with self:
            self._get_token(TokenTypes.WHITESPACE)

        # Leading and trailing spaces are removed
        self._save(NamedArgumentNode(key, value.strip()))

        # Mark the beginning of named arguments
        self._named_arguments = True

        return True

    def _process_unnamed_argument(self):
        # This parses an unnamed argument

        if self._named_arguments:
            self._error("Unnamed arguments after named arguments are forbidden")

        # Values can be surrounded by quotes
        if self._peek_token_is(TokenTypes.LITERAL, '"'):
            self._get_token(TokenTypes.LITERAL, '"')
            value = self._collect_join([Token(TokenTypes.LITERAL, '"')])
            self._get_token(TokenTypes.LITERAL, '"')
        else:
            value = self._collect_join([Token(TokenTypes.LITERAL, ",")])

        # The comma is not there after the last argument
        with self:
            self._get_token(TokenTypes.LITERAL, ",")

        # Leading spaces are removed
        with self:
            self._get_token(TokenTypes.WHITESPACE)

        self._save(UnnamedArgumentNode(value))

        return True

    def process_arguments(self):
        """
        Process the extracted nodes and converts them into args (unnamed arguments),
        kwargs (named arguments), and tags (unnamed arguments whose name begins
        with "#".
        """

        args = [
            node.value for node in self.nodes if node.node_type == "unnamed_argument"
        ]

        kwargs = {
            node.key: node.value
            for node in self.nodes
            if node.node_type == "named_argument"
        }

        # Isolate tags
        tags = [i for i in args if i.startswith("#")]

        # Isolate subtypes
        subtypes = [i for i in args if i.startswith("*")]

        if len(subtypes) == 0:
            subtype = None
        if len(subtypes) == 1:
            # Get the first subtype and remove the leading "*"
            subtype = subtypes[0][1:]
        if len(subtypes) > 1:
            self._error("Multiple subtypes detected")

        # Keep normal args
        args = [i for i in args if i not in tags + subtypes]

        # Remove the "#" from tags
        tags = [i[1:] for i in tags]

        return args, kwargs, tags, subtype
