import itertools

from mau.lexers.base_lexer import Token, TokenTypes, Literal
from mau.lexers.text_lexer import TextLexer
from mau.parsers.base_parser import BaseParser, ParserError
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.nodes import (
    WordNode,
    SentenceNode,
    TextNode,
    StyleNode,
    VerbatimNode,
    ClassNode,
    MacroNode,
    LinkNode,
    ImageNode,
    FootnoteRefNode,
    FootnoteDefNode,
)

# This is a simple map to keep track of the official
# name of styles introduced by special characters
MAP_STYLES = {"_": "underscore", "*": "star"}


def footnote_anchors(content):
    """
    Return the id of the reference and the id of the definition.
    """
    h = str(hash(content))[:8]
    return f"fr-{h}", f"fd-{h}"  # pragma: no cover


# The TextParser is a nested parser.
# The parsing always starts with parse_sentence
# and from there all components of the text are explored
class TextParser(BaseParser):
    def __init__(self, footnotes_start_with=1, v1_backward_compatibility=False):
        super().__init__()

        self.lexer = TextLexer()

        # This makes footnotes counting start from
        # the given number. It is needed because
        # there might be already footnotes in the
        # parent text to take into account.
        self.footnotes_start_with = footnotes_start_with

        # These are the footnotes found in this text
        self.footnote_defs = []

        # This enables backward compatibility with Mau 1.x
        # Footnotes didn't require quotes if they
        # contain commas. In Mau 2.x footnotes accept
        # arguments as the other macros so the text
        # should be wrapped in quotes.
        self.v1_backward_compatibility = v1_backward_compatibility

        # These are the nodes created by the parsing.
        self.nodes = []

        # This is used as a storage for macro arguments.
        self.argsparser = ArgumentsParser()

    def set_names_and_defaults(self, positional_names, default_values=None):
        """
        A wrapper for the method set_names_and_defaults() of ArgumentParser
        that raises a ParserError with a broader context.
        The argument parser is applied on the arguments only, so the error
        reporting is limited to that string, while the TextParser has knowledge
        of the whole line.
        """

        try:
            self.argsparser.set_names_and_defaults(positional_names, default_values)
        except ParserError as e:
            self.error(str(e))

    def parse_word(self):
        """
        Parse a single word.
        """
        return WordNode(self.get_token().value)

    def parse_style(self):
        """
        Parse a sentence surrounded by style markers.
        """

        # Get the style marker
        style = self.get_token(TokenTypes.LITERAL, check=lambda x: x in "*_").value

        # Get everything until the next marker
        content = self.parse_sentence(stop_tokens={Token(TokenTypes.LITERAL, style)})

        # Get the closing marker
        self.get_token(TokenTypes.LITERAL, style)

        return StyleNode(MAP_STYLES[style], content)

    def parse_escape(self):
        """
        Parse an escaped element.
        """

        # Drop the backslash
        self.get_token(TokenTypes.LITERAL, "\\")

        return WordNode(self.get_token().value)

    def parse_styled_text(self, stop_tokens=None):
        """
        Parse multiple possible elements: escapes, classes,
        macros, verbatim, styles, links, words.
        This is a helper for the function parse_sentence
        that takes into account all possible elements of
        syntax, stopping if the token is among the listed ones.
        """
        stop_tokens = stop_tokens or set()

        if self.peek_token() in stop_tokens:
            return None

        with self:
            return self.parse_escape()

        with self:
            return self.parse_class()

        with self:
            return self.parse_macro()

        with self:
            return self.parse_verbatim()

        with self:
            return self.parse_style()

        with self:
            return self.parse_link()

        return self.parse_word()

    def parse_sentence(self, stop_tokens=None):
        """
        Parse a sentence, which is made of multiple
        elements identified by parse_styled_text, until
        the EOF, the EOL, or a specific set of tokens
        passed as argument.
        """

        content = []
        stop_tokens = stop_tokens or set()
        stop_tokens = stop_tokens.union({Token(TokenTypes.EOF), Token(TokenTypes.EOL)})

        result = self.parse_styled_text(stop_tokens)
        while result is not None:
            content.append(result)
            result = self.parse_styled_text(stop_tokens)

        # Group consecutive WordNode nodes into a single TextNode
        grouped_nodes = []
        for key, group in itertools.groupby(content, lambda x: x.__class__ == WordNode):
            if key:
                text = "".join([n.value for n in group])
                grouped_nodes.append(TextNode(text))
            else:
                grouped_nodes.extend(list(group))

        return SentenceNode(content=grouped_nodes)

    def parse_verbatim(self):
        """
        Parse text in `verbatim`.
        """

        # Get the verbatim marker
        self.get_token(TokenTypes.LITERAL, "`")

        # Get the content tokens until the
        # next verbatim marker or EOL
        content = self.collect_join(
            [Token(TokenTypes.LITERAL, "`"), Token(TokenTypes.EOL)],
        )

        # Remove the closing marker
        self.get_token(TokenTypes.LITERAL, "`")

        return VerbatimNode(content)

    def parse_class(self):
        """
        Parse a class in the form [class]#content#.
        """

        # Get the opening square bracket
        self.get_token(TokenTypes.LITERAL, "[")

        # Get everything up to the closing bracket
        classes = self.collect_join(
            [Token(TokenTypes.LITERAL, "]"), Token(TokenTypes.EOL)]
        )

        # Get the closing bracket
        self.get_token(TokenTypes.LITERAL, "]")

        # Multiple classes are separated by commas
        classes = classes.split(",")

        # Get the opening number sign
        self.get_token(TokenTypes.LITERAL, "#")

        # Get the content of the class
        content = self.parse_sentence(stop_tokens={Token(TokenTypes.LITERAL, "#")})

        # Get the closing number sign
        self.get_token(TokenTypes.LITERAL, "#")

        return ClassNode(classes, content)

    def parse_macro_link(self):
        """
        Parse a link macro in the form [link](target, text).
        """

        # Assign names and get the arguments
        self.set_names_and_defaults(["target", "text"], {"text": None})
        args, kwargs = self.argsparser.get_arguments_and_reset()

        # Set the name of the first two unnamed arguments

        # Get the target as it can be used as default text
        target = kwargs.get("target")

        # We might omit text
        text = kwargs.get("text")
        if text is None:
            text = target

        return LinkNode(target, text)

    def parse_macro_mailto(self):
        """
        Parse a mailto macro in the form [mailto](email).
        """

        # Assign names and get the arguments
        self.set_names_and_defaults(["email"])
        args, kwargs = self.argsparser.get_arguments_and_reset()

        email = kwargs.get("email")
        target = f"mailto:{email}"

        return LinkNode(target, email)

    def parse_macro_class(self):
        """
        Parse a class macro in the form [class](text, "class1,class2,...").
        """

        # Assign names and get the arguments
        self.set_names_and_defaults(["text", "classes"])
        args, kwargs = self.argsparser.get_arguments_and_reset()

        # Parse the text
        pt = TextParser().analyse(kwargs.get("text"))

        # Text should return a single sentence node
        result = pt.nodes[0]

        # Multiple classes are separated by commas
        classes = kwargs.get("classes").split(",")

        return ClassNode(classes, result)

    def parse_macro_image(self):
        """
        Parse an inline image macro in the form
        [image](uri, alt_text, width, height).
        """

        # Assign names and get the arguments
        self.set_names_and_defaults(
            ["uri", "alt_text", "width", "height"],
            {"alt_text": None, "width": None, "height": None},
        )
        args, kwargs = self.argsparser.get_arguments_and_reset()

        return ImageNode(
            uri=kwargs.get("uri"),
            alt_text=kwargs.get("alt_text"),
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        )

    def parse_macro_footnote(self, arguments):
        """
        Parse a footnote macro in the form
        [footnote](content).
        """

        if self.v1_backward_compatibility:
            self.argsparser.get_arguments_and_reset()
            footnote_text = arguments
        else:
            # Assign names and get the arguments
            self.set_names_and_defaults(["text"])
            args, kwargs = self.argsparser.get_arguments_and_reset()
            footnote_text = kwargs["text"]

        refanchor, defanchor = footnote_anchors(footnote_text)
        number = self.footnotes_start_with + len(self.footnote_defs)

        p = TextParser().analyse(footnote_text)

        self.footnote_defs.append(
            FootnoteDefNode(
                refanchor=refanchor, defanchor=defanchor, number=number, content=p.nodes
            )
        )
        return FootnoteRefNode(
            refanchor=refanchor, defanchor=defanchor, number=number, content=p.nodes
        )

    def _collect_macro_args(self):
        self.get_token(TokenTypes.LITERAL, "(")

        all_args = []

        while not (
            self.peek_token_is(TokenTypes.LITERAL, ")")
            or self.peek_token_is(TokenTypes.EOL)
        ):
            if self.peek_token_is(TokenTypes.LITERAL, '"'):
                self.get_token(TokenTypes.LITERAL, '"')

                value = self.collect_join(
                    stop_tokens=[Token(TokenTypes.LITERAL, '"'), Token(TokenTypes.EOL)],
                )

                self.get_token(TokenTypes.LITERAL, '"')

                arguments = f'"{value}"'
            else:
                arguments = self.collect_join(
                    stop_tokens=[
                        Token(TokenTypes.LITERAL, ","),
                        Token(TokenTypes.LITERAL, ")"),
                        Token(TokenTypes.EOL),
                    ],
                )

            all_args.append(arguments)

        self.get_token(TokenTypes.LITERAL, ")")

        return "".join(all_args)

    def parse_macro(self):
        self.get_token(TokenTypes.LITERAL, "[")
        macro_name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "]")

        arguments = self._collect_macro_args()

        self.argsparser.analyse(arguments)

        if macro_name == "link":
            return self.parse_macro_link()
        elif macro_name == "mailto":
            return self.parse_macro_mailto()
        elif macro_name == "class":
            return self.parse_macro_class()
        elif macro_name == "image":
            return self.parse_macro_image()
        elif macro_name == "footnote":
            return self.parse_macro_footnote(arguments)

        # Get the arguments
        args, kwargs = self.argsparser.get_arguments_and_reset()

        return MacroNode(macro_name, args, kwargs)

    def parse_link(self):
        link = self.get_token(
            TokenTypes.TEXT,
            check=lambda x: x.startswith("http://") or x.startswith("https://"),
        ).value

        # Check the last character.
        # Common punctuation shouldn't be part of the link
        if link[-1] in [".", ","]:
            self.put_token(Literal(link[-1]))
            link = link[:-1]

        return LinkNode(link, link)

    def parse(self):
        self._save(self.parse_sentence())
