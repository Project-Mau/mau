import itertools

from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.text_lexer import TextLexer
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.inline import SentenceNode, StyleNode, TextNode, VerbatimNode, WordNode
from mau.nodes.macros import (
    MacroClassNode,
    MacroHeaderNode,
    MacroImageNode,
    MacroLinkNode,
    MacroNode,
)
from mau.parsers.arguments import set_names_and_defaults
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.base_parser import BaseParser

# This is a simple map to keep track of the official
# name of styles introduced by special characters
MAP_STYLES = {"_": "underscore", "*": "star", "^": "caret", "~": "tilde"}


# The TextParser is a nested parser.
# The parsing always starts with parse_sentence
# and from there all components of the text are explored
class TextParser(BaseParser):
    lexer_class = TextLexer

    def __init__(self, environment, parent_node=None, parent_position=None):
        super().__init__(environment, parent_node, parent_position)

        # These are the footnotes found in this text
        # The format of this dictionary is
        # {"name": node}
        self.footnotes = {}

        # These are the internal links found in this text
        self.links = []

    def _process_functions(self):
        return [self._process_eol, self._process_sentence]

    def _process_eol(self):
        # This simply parses the end of line.

        self._get_token(TokenTypes.EOL)

        return True

    def _process_sentence(self):
        for node in self._parse_sentence():
            self._save(node)

        return True

    def _parse_word(self):
        """
        Parse a single word.
        """
        return WordNode(
            value=self._get_token().value,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_style(self):
        """
        Parse a sentence surrounded by style markers.
        """

        # Get the style marker
        style = self._get_token(
            TokenTypes.LITERAL, check=lambda x: x in MAP_STYLES
        ).value

        # Get everything until the next marker
        content = self._parse_sentence(stop_tokens={Token(TokenTypes.LITERAL, style)})

        # Get the closing marker
        self._get_token(TokenTypes.LITERAL, style)

        return StyleNode(
            value=MAP_STYLES[style],
            children=content,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_escape(self):
        """
        Parse an escaped element.
        """

        # Drop the backslash
        self._get_token(TokenTypes.LITERAL, "\\")

        return WordNode(
            value=self._get_token().value,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_styled_text(self, stop_tokens=None):
        """
        Parse multiple possible elements: escapes, classes,
        macros, verbatim, styles, links, words.
        This is a helper for the function _parse_sentence
        that takes into account all possible elements of
        syntax, stopping if the token is among the listed ones.
        """
        stop_tokens = stop_tokens or set()

        if self._peek_token() in stop_tokens:
            return None

        with self:
            return self._parse_escape()

        with self:
            return self._parse_macro()

        with self:
            return self._parse_verbatim()

        with self:
            return self._parse_escaped()

        with self:
            return self._parse_style()

        return self._parse_word()

    def _parse_sentence(self, stop_tokens=None):
        """
        Parse a sentence, which is made of multiple
        elements identified by _parse_styled_text, until
        the EOF, the EOL, or a specific set of tokens
        passed as argument.
        """

        content = []
        stop_tokens = stop_tokens or set()
        stop_tokens = stop_tokens.union({Token(TokenTypes.EOF), Token(TokenTypes.EOL)})

        result = self._parse_styled_text(stop_tokens)
        while result is not None:
            content.append(result)
            result = self._parse_styled_text(stop_tokens)

        # Group consecutive WordNode nodes into a single TextNode
        grouped_nodes = []
        for key, group in itertools.groupby(content, lambda x: x.__class__ == WordNode):
            if key:
                text = "".join([n.value for n in group])
                grouped_nodes.append(
                    TextNode(
                        value=text,
                        parent=self.parent_node,
                        parent_position=self.parent_position,
                    )
                )
            else:
                grouped_nodes.extend(list(group))

        return grouped_nodes

    def _parse_verbatim(self):
        """
        Parse text in `verbatim`.
        """

        # Get the verbatim marker
        self._get_token(TokenTypes.LITERAL, "`")

        # Get the content tokens until the
        # next verbatim marker or EOL
        content = self._collect_join(
            [Token(TokenTypes.LITERAL, "`"), Token(TokenTypes.EOL)],
        )

        # Remove the closing marker
        self._get_token(TokenTypes.LITERAL, "`")

        return VerbatimNode(
            content, parent=self.parent_node, parent_position=self.parent_position
        )

    def _parse_escaped(self):
        """
        Parse $escaped$ or %escaped% text.
        """

        # Get the escaped marker
        marker = self._get_token(TokenTypes.LITERAL, check=lambda x: x in "$%").value

        # Get the content tokens until the
        # next verbatim marker or EOL
        content = self._collect_join(
            [Token(TokenTypes.LITERAL, marker), Token(TokenTypes.EOL)],
        )

        # Remove the closing marker
        self._get_token(TokenTypes.LITERAL, marker)

        return TextNode(
            content, parent=self.parent_node, parent_position=self.parent_position
        )

    def _parse_macro_link(self, args, kwargs):
        """
        Parse a link macro in the form [link](target, text).
        """

        args, kwargs = set_names_and_defaults(
            args, kwargs, ["target", "text"], {"text": None}
        )

        target = kwargs.get("target")

        text = kwargs["text"]
        if text is None:
            text = target

        current_context = self._current_token.context
        par = self.analyse(text, current_context, self.environment)

        return MacroLinkNode(
            target=target,
            children=par.nodes,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_macro_header(self, args, kwargs):
        """
        Parse a link macro in the form [header](header_id, text).
        """

        args, kwargs = set_names_and_defaults(
            args, kwargs, ["target", "text"], {"text": ""}
        )

        target = kwargs.get("target")
        text = kwargs["text"]

        current_context = self._current_token.context
        par = self.analyse(text, current_context, self.environment)

        node = MacroHeaderNode(
            header_id=target,
            children=par.nodes,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

        self.links.append(node)

        return node

    def _parse_macro_mailto(self, args, kwargs):
        """
        Parse a mailto macro in the form [mailto](email).
        """

        args, kwargs = set_names_and_defaults(
            args, kwargs, ["email", "text"], {"text": None}
        )

        email = kwargs.get("email")
        text = kwargs.get("text")

        target = f"mailto:{email}"
        if text is None:
            text = email

        current_context = self._current_token.context
        par = self.analyse(text, current_context, self.environment)

        return MacroLinkNode(
            target=target,
            children=par.nodes,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_macro_class(self, args, kwargs):
        """
        Parse a class macro in the form [class](text, class1, class2, ...).
        """

        args, kwargs = set_names_and_defaults(args, kwargs, ["text"])

        current_context = self._current_token.context

        text = kwargs.get("text")

        par = self.analyse(text, current_context, self.environment)

        return MacroClassNode(
            classes=args,
            children=par.nodes,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_macro_control(self, macro_name, args, kwargs):
        """
        Parse a class macro in the form [@if:variable:test](true, false).
        """

        # Skip the initial @
        macro_name = macro_name[1:]

        try:
            operator, variable, test = macro_name.split(":", 2)
        except ValueError:
            self._error(
                f"Macro '{macro_name}' is not in the form @operator:variable:test"
            )

        if operator not in ["if", "ifeval"]:
            self._error(f"Control operator '{operator}' is not supported")

        args, kwargs = set_names_and_defaults(
            args,
            kwargs,
            ["true", "false"],
            {"false": ""},
        )

        current_context = self._current_token.context

        variable_value = self.environment.getvar(variable, None)

        if variable_value is None:
            self._error(f"Variable '{variable}' has not been defined")

        test_result = False

        if test.startswith("="):
            value = test[1:]
            test_result = variable_value == value
        elif test.startswith("!="):
            value = test[2:]
            test_result = variable_value != value
        elif test.startswith("&"):
            value = test[1:]

            if value not in ["true", "false"]:
                self._error(f"Boolean value '{value}' is invalid")

            # pylint: disable=simplifiable-if-expression
            value = True if value == "true" else False

            test_result = variable_value and value
        else:
            self._error(f"Test '{test}' is not supported")

        if operator == "if":
            if test_result is True:
                text = kwargs.get("true")
            else:
                text = kwargs.get("false")
        else:
            if test_result is True:
                text_variable = kwargs.get("true")
            else:
                text_variable = kwargs.get("false")

            text = self.environment.getvar(text_variable)

            if text is None:
                self._error(f"Variable '{text_variable}' has not been defined")

        par = self.analyse(text, current_context, self.environment)

        return SentenceNode(
            children=par.nodes,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_macro_image(self, args, kwargs):
        """
        Parse an inline image macro in the form
        [image](uri, alt_text, width, height).
        """

        # Assign names and get the arguments
        args, kwargs = set_names_and_defaults(
            args,
            kwargs,
            ["uri", "alt_text", "width", "height"],
            {"alt_text": None, "width": None, "height": None},
        )

        return MacroImageNode(
            uri=kwargs.get("uri"),
            alt_text=kwargs.get("alt_text"),
            width=kwargs.get("width"),
            height=kwargs.get("height"),
            parent=self.parent_node,
            parent_position=self.parent_position,
        )

    def _parse_macro_footnote(self, args, kwargs):
        """
        Parse a footnote macro in the form
        [footnote](name).
        """

        args, kwargs = set_names_and_defaults(args, kwargs, ["name"])

        name = kwargs["name"]

        node = FootnoteNode(
            parent=self.parent_node, parent_position=self.parent_position
        )

        self.footnotes[name] = node

        return node

    def _collect_macro_args(self):
        self._get_token(TokenTypes.LITERAL, "(")

        all_args = []

        while not (
            self._peek_token_is(TokenTypes.LITERAL, ")")
            or self._peek_token_is(TokenTypes.EOL)
        ):
            if self._peek_token_is(TokenTypes.LITERAL, '"'):
                self._get_token(TokenTypes.LITERAL, '"')

                value = self._collect_join(
                    stop_tokens=[
                        Token(TokenTypes.LITERAL, '"'),
                        Token(TokenTypes.EOL),
                    ],
                )

                self._get_token(TokenTypes.LITERAL, '"')

                arguments = f'"{value}"'
            else:
                arguments = self._collect_join(
                    stop_tokens=[
                        Token(TokenTypes.LITERAL, ","),
                        Token(TokenTypes.LITERAL, ")"),
                        Token(TokenTypes.EOL),
                    ],
                )

            all_args.append(arguments)

        self._get_token(TokenTypes.LITERAL, ")")

        return "".join(all_args)

    def _parse_macro(self):
        self._get_token(TokenTypes.LITERAL, "[")
        macro_name = self._get_token(TokenTypes.TEXT).value
        self._get_token(TokenTypes.LITERAL, "]")

        arguments = self._collect_macro_args()

        current_context = self._peek_token().context

        par = ArgumentsParser.analyse(arguments, current_context, self.environment)

        args, kwargs, _, _ = par.process_arguments()

        if macro_name.startswith("@"):
            return self._parse_macro_control(macro_name, args, kwargs)

        if macro_name == "link":
            return self._parse_macro_link(args, kwargs)

        if macro_name == "header":
            return self._parse_macro_header(args, kwargs)

        if macro_name == "mailto":
            return self._parse_macro_mailto(args, kwargs)

        if macro_name == "image":
            return self._parse_macro_image(args, kwargs)

        if macro_name == "footnote":
            return self._parse_macro_footnote(args, kwargs)

        if macro_name == "class":
            return self._parse_macro_class(args, kwargs)

        # if macro_name == "if":
        #     return self._parse_macro_if(args, kwargs)

        # if macro_name == "ifeval":
        #     return self._parse_macro_ifeval(args, kwargs)

        return MacroNode(
            macro_name,
            args=args,
            kwargs=kwargs,
            parent=self.parent_node,
            parent_position=self.parent_position,
        )
