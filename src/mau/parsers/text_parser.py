import itertools

from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.text_lexer import TextLexer
from mau.parsers.base_parser import BaseParser, Literal
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
    def __init__(self, footnotes_start_with=1):
        super().__init__()

        self.lexer = TextLexer()

        # This makes footnotes counting start from
        # the given number. It is needed because
        # there might be already footnotes in the
        # parent text to take into account.
        self.footnotes_start_with = footnotes_start_with

        # These are the footnotes found in this text
        self.footnotes = []

        # These are the nodes created by the parsing.
        self.nodes = []

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

    def parse_macro_link(self, arguments):
        """
        Parse a link macro in the form [link](target, text).
        """

        p = ArgumentsParser().analyse(arguments)

        # Set the name of the first two unnamed arguments
        p.merge_unnamed_args(["target", "text"])

        # Get the target as it can be used as default text
        target = p.kwargs.get("target")

        return LinkNode(target, p.kwargs.get("text", target))

    def parse_macro_mailto(self, arguments):
        """
        Parse a mailto macro in the form [mailto](email).
        """

        p = ArgumentsParser().analyse(arguments)

        # Set the name of the first unnamed argument
        p.merge_unnamed_args(["email"])

        email = p.kwargs.get("email")
        target = f"mailto:{email}"

        return LinkNode(target, email)

    def parse_macro_image(self, arguments):
        """
        Parse an inline image macro in the form
        [image](uri, alt_text, width, height).
        """

        p = ArgumentsParser().analyse(arguments)

        # Set the name of unnamed arguments
        p.merge_unnamed_args(
            ["uri", "alt_text", "width", "height"],
        )

        return ImageNode(
            uri=p.kwargs.get("uri"),
            alt_text=p.kwargs.get("alt_text", None),
            width=p.kwargs.get("width", None),
            height=p.kwargs.get("height", None),
        )

    def parse_macro_footnote(self, text):
        """
        Parse a footnote macro in the form
        [footnote](content).
        """

        refanchor, defanchor = footnote_anchors(text)
        number = self.footnotes_start_with + len(self.footnotes)

        p = TextParser().analyse(text)

        self.footnotes.append(
            FootnoteDefNode(
                refanchor=refanchor, defanchor=defanchor, number=number, content=p.nodes
            )
        )
        return FootnoteRefNode(
            refanchor=refanchor, defanchor=defanchor, number=number, content=p.nodes
        )

    def parse_macro(self):
        self.get_token(TokenTypes.LITERAL, "[")
        macro_name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "]")
        self.get_token(TokenTypes.LITERAL, "(")

        arguments = self.collect_join(
            stop_tokens=[Token(TokenTypes.LITERAL, ")"), Token(TokenTypes.EOL)],
        )

        self.get_token(TokenTypes.LITERAL, ")")

        if macro_name == "link":
            return self.parse_macro_link(arguments)
        elif macro_name == "mailto":
            return self.parse_macro_mailto(arguments)
        elif macro_name == "image":
            return self.parse_macro_image(arguments)
        elif macro_name == "footnote":
            return self.parse_macro_footnote(arguments)

        return MacroNode(macro_name, arguments)

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
