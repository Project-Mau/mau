from mau.lexers.base_lexer import Token, TokenTypes
from mau.lexers.text_lexer import TextLexer
from mau.parsers.base_parser import BaseParser, analyse, Literal
from mau.parsers.arguments_parser import ArgumentsParser, merge_args
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

MAP_STYLES = {"_": "underscore", "*": "star"}


# Returns the id of the reference
# and the id of the definition
def footnote_anchors(content):
    h = str(hash(content))[:8]
    return f"fr-{h}", f"fd-{h}"  # pragma: no cover


class TextParser(BaseParser):
    def __init__(self, footnotes_start_with=1):
        super().__init__()

        self.lexer = TextLexer()

        self._styles = set()
        self._classes = set()
        self._verbatim = False

        self.footnotes_start_with = footnotes_start_with
        self.footnotes = []
        self._nodes = []
        self.nodes = []

    def parse_word(self):
        return WordNode(self.get_token_value())

    def parse_style(self):
        style = self.get_token_value(TokenTypes.LITERAL, check=lambda x: x in "*_")
        content = self.parse_sentence(stop_tokens={Token(TokenTypes.LITERAL, style)})
        self.get_token(TokenTypes.LITERAL, style)

        return StyleNode(MAP_STYLES[style], content)

    def parse_escape(self):
        self.get_token(TokenTypes.LITERAL, "\\")

        # if self.peek_token() == Literal('"'):
        #     return WordNode('\\"')

        return WordNode(self.get_token_value())

    def parse_styled_text(self, stop_tokens=None):
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
        content = []
        stop_tokens = stop_tokens or set()
        stop_tokens = stop_tokens.union({Token(TokenTypes.EOF), Token(TokenTypes.EOL)})

        result = self.parse_styled_text(stop_tokens)
        while result is not None:
            content.append(result)
            result = self.parse_styled_text(stop_tokens)

        import itertools

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
        self.get_token(TokenTypes.LITERAL, "`")
        content = self.collect_join(
            [Token(TokenTypes.LITERAL, "`"), Token(TokenTypes.EOL)],
        )
        self.get_token(TokenTypes.LITERAL, "`")

        return VerbatimNode(content)

    def parse_class(self):
        self.get_token(TokenTypes.LITERAL, "[")
        classes = self.collect_join(
            [Token(TokenTypes.LITERAL, "]"), Token(TokenTypes.EOL)]
        )
        self.get_token(TokenTypes.LITERAL, "]")
        self.get_token(TokenTypes.LITERAL, "#")
        content = self.parse_sentence(stop_tokens={Token(TokenTypes.LITERAL, "#")})
        self.get_token(TokenTypes.LITERAL, "#")

        classes = classes.split(",")

        return ClassNode(classes, content)

    def parse_macro_link(self, args, kwargs):
        args, kwargs = merge_args(args, kwargs, ["target", "text"])
        return LinkNode(kwargs.get("target"), kwargs.get("text"))

    def parse_macro_mailto(self, args, kwargs):
        args, kwargs = merge_args(args, kwargs, ["email"])
        email = kwargs.get("email")
        target = f"mailto:{email}"
        return LinkNode(target, email)

    def parse_macro_image(self, args, kwargs):
        args, kwargs = merge_args(
            args,
            kwargs,
            ["uri", "alt_text", "width", "height"],
        )

        uri = kwargs.pop("uri", None)
        alt_text = kwargs.pop("alt_text", None)
        width = kwargs.pop("width", None)
        height = kwargs.pop("height", None)

        return ImageNode(uri=uri, alt_text=alt_text, width=width, height=height)

    def parse_macro_footnote(self, args, kwargs):
        args, kwargs = merge_args(args, kwargs, ["content"])
        content_text = kwargs.get("content")
        refanchor, defanchor = footnote_anchors(content_text)
        number = self.footnotes_start_with + len(self.footnotes)

        p = analyse(TextParser(), content_text)

        self.footnotes.append(
            FootnoteDefNode(
                refanchor=refanchor, defanchor=defanchor, number=number, content=p.nodes
            )
        )
        return FootnoteRefNode(refanchor=refanchor, defanchor=defanchor, number=number)

    def parse_macro(self):
        self.get_token(TokenTypes.LITERAL, "[")
        macro_name = self.get_token_value(TokenTypes.TEXT)
        self.get_token(TokenTypes.LITERAL, "]")
        self.get_token(TokenTypes.LITERAL, "(")

        raw = False
        if macro_name == "footnote":
            raw = True

        arguments = self.collect_join(
            stop_tokens=[Token(TokenTypes.LITERAL, ")"), Token(TokenTypes.EOL)],
        )
        p = analyse(ArgumentsParser(raw=raw), arguments)

        self.get_token(TokenTypes.LITERAL, ")")

        if macro_name == "link":
            return self.parse_macro_link(args=p.args, kwargs=p.kwargs)
        if macro_name == "mailto":
            return self.parse_macro_mailto(args=p.args, kwargs=p.kwargs)
        elif macro_name == "image":
            return self.parse_macro_image(args=p.args, kwargs=p.kwargs)
        elif macro_name == "footnote":
            return self.parse_macro_footnote(args=p.args, kwargs=p.kwargs)

        return MacroNode(macro_name, args=p.args, kwargs=p.kwargs)

    def parse_link(self):
        link = self.get_token_value(
            TokenTypes.TEXT,
            check=lambda x: x.startswith("http://") or x.startswith("https://"),
        )

        return LinkNode(link, link)

    def _parse(self):
        self._save(self.parse_sentence())
