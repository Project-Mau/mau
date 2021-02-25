from urllib.parse import quote
import copy

from mau.lexers.base_lexer import TokenTypes, Token, TokenError
from mau.lexers.main_lexer import MainLexer
from mau.parsers.base_parser import BaseParser, ParseError, parser, analyse
from mau.parsers.text_parser import TextParser
from mau.parsers.arguments_parser import ArgumentsParser, merge_args
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.nodes import (
    HorizontalRuleNode,
    TextNode,
    BlockNode,
    SourceNode,
    RawNode,
    AdmonitionNode,
    QuoteNode,
    ContentImageNode,
    CommandNode,
    HeaderNode,
    ListNode,
    ListItemNode,
    ParagraphNode,
    TocNode,
)


def header_anchor(text, level):
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]
    )  # pragma: no cover


class MainParser(BaseParser):
    def __init__(self, variables=None):
        super().__init__()

        self.lexer = MainLexer()

        self.variables = copy.deepcopy(variables) if variables else {}
        self.headers = []
        self.footnotes = []
        self.blocks = {}
        self.toc = []

        self._args = []
        self._kwargs = {}
        self._title = None

    def _add_footnotes(self, footnotes):
        self.footnotes.extend(footnotes)

    def _pop_attributes(self):
        _args = copy.deepcopy(self._args)
        _kwargs = copy.deepcopy(self._kwargs)

        self._args = []
        self._kwargs = {}

        return _args, _kwargs

    def _push_attributes(self, args, kwargs):
        self._args = copy.deepcopy(args)
        self._kwargs = copy.deepcopy(kwargs)

    def _pop_title(self):
        title = self._title
        self._title = None
        return title

    def _push_title(self, title):
        self._title = title

    def collect_lines(self, stop_tokens):
        # This collects several lines of text in a list
        # until it gets to a line that begins with one
        # of the tokens listed in stop_tokens.
        lines = []
        while self.peek_token() not in stop_tokens:
            lines.append(self.collect_join([Token(TokenTypes.EOL)]))
            self.get_token(TokenTypes.EOL)

        return lines

    @parser
    def _parse_horizontal_rule(self):
        self.get_token(TokenTypes.LITERAL, "---")
        self.get_token(TokenTypes.EOL)

        self._save(HorizontalRuleNode())

    @parser
    def _parse_single_line_comment(self):
        self.get_token(TokenTypes.TEXT, check=lambda x: x.startswith("//"))
        self.get_token(TokenTypes.EOL)

    @parser
    def _parse_multi_line_comment(self):
        self.get_token(TokenTypes.LITERAL, "////")
        self.collect_lines([Token(TokenTypes.LITERAL, "////"), Token(TokenTypes.EOF)])
        self.force_token(TokenTypes.LITERAL, "////")

    @parser
    def _parse_title(self):
        self.get_token(TokenTypes.LITERAL, ".")

        with self:
            self.get_token(TokenTypes.WHITESPACE)

        text = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.EOL)

        p = analyse(TextParser(footnotes_start_with=len(self.footnotes) + 1), text)
        title = p.nodes[0]

        self._push_title(title)

    @parser
    def _parse_header(self):
        header = self.get_token(
            TokenTypes.LITERAL, check=lambda x: x.startswith("=")
        ).value
        self.get_token(TokenTypes.WHITESPACE)

        in_toc = True
        if header.endswith("!"):
            header = header[:-1]
            in_toc = False

        text = self.get_token(TokenTypes.TEXT).value
        level = len(header)
        anchor = header_anchor(text, level)

        if in_toc:
            self.headers.append((text, level, anchor))

        _, kwargs = self._pop_attributes()

        self._save(HeaderNode(value=text, level=level, anchor=anchor, kwargs=kwargs))

    @parser
    def _parse_content(self):
        self.get_token(TokenTypes.LITERAL, check=lambda x: x.startswith("<<"))
        self.get_token(TokenTypes.WHITESPACE)
        content_type_and_uri = self.get_token(TokenTypes.TEXT).value

        content_type, uri = content_type_and_uri.split(":", maxsplit=1)

        _, kwargs = self._pop_attributes()

        alt_text = kwargs.pop("alt_text", None)
        classes = kwargs.pop("classes", None)
        title = self._pop_title()

        if classes:
            classes = classes.split(",")

        self._save(
            ContentImageNode(
                uri=uri,
                alt_text=alt_text,
                classes=classes,
                title=title,
                kwargs=kwargs,
            )
        )

    @parser
    def _parse_block(self):
        delimiter = self.get_token(TokenTypes.TEXT).value

        if len(delimiter) != 4 or len(set(delimiter)) != 1:
            raise TokenError

        self.get_token(TokenTypes.EOL)

        content = self.collect_lines(
            [Token(TokenTypes.TEXT, delimiter), Token(TokenTypes.EOF)]
        )

        self.force_token(TokenTypes.TEXT, delimiter)
        self.get_token(TokenTypes.EOL)

        secondary_content = self.collect_lines(
            [Token(TokenTypes.EOL), Token(TokenTypes.EOF)]
        )

        args, kwargs = self._pop_attributes()
        title = self._pop_title()

        if len(args) != 0 and args[0] in ["if", "ifnot"]:
            return self._parse_conditional_block(args[0], content, args[1:], kwargs)

        if len(args) != 0 and args[0] in ["raw"]:
            return self._parse_raw_block(content, args[1:], kwargs)

        if len(args) != 0 and args[0] == "source":
            return self._parse_source_block(
                content, secondary_content, title, args[1:], kwargs
            )

        if len(args) != 0 and args[0] == "admonition":
            return self._parse_admonition_block(content, args[1:], kwargs)

        if len(args) != 0 and args[0] == "quote":
            return self._parse_quote_block(content, title, args[1:], kwargs)

        try:
            blocktype = args[0]
            args = args[1:]
        except IndexError:
            blocktype = None

        return self._parse_standard_block(
            blocktype, content, secondary_content, title, args, kwargs
        )

    def _parse_conditional_block(self, condition, content, args, kwargs):
        _, kwargs = merge_args(args, kwargs, ["variable", "value"])

        match = self.variables.get(kwargs["variable"]) == kwargs.get("value", True)
        test = True if condition == "if" else False

        if match is test:
            p = analyse(MainParser(variables=self.variables), "\n".join(content))

            self._add_footnotes(p.footnotes)

            self.nodes.extend(p.nodes)

    def _parse_raw_block(self, content, args, kwargs):
        textlines = [TextNode(line) for line in content]

        self._save(RawNode(content=textlines))

    def _parse_source_block(self, content, secondary_content, title, args, kwargs):
        delimiter = kwargs.pop("callouts", ":")
        highlight_marker = kwargs.pop("highlight", "@")

        # A dictionary that contains callout markers in
        # the form {linenum:name}
        callout_markers = {}

        # A list of highlighted lines
        highlighted_lines = []

        lines_with_callouts = [
            (linenum, line)
            for linenum, line in enumerate(content)
            if line.endswith(delimiter)
        ]

        for linenum, line in lines_with_callouts:
            # Remove the final delimiter
            line = line[:-1]

            splits = line.split(delimiter)
            if len(splits) < 2:
                # It's a trap! There are no separators left
                continue

            callout_name = splits[-1]
            line = delimiter.join(splits[:-1])

            content[linenum] = line

            if callout_name == highlight_marker:
                highlighted_lines.append(linenum)
            else:
                callout_markers[linenum] = callout_name

        # A dictionary that contains the text for each
        # marker in the form {name:text}
        callout_contents = {}

        for line in secondary_content:
            if ":" not in line:
                raise ParseError(
                    f"Callout description should be written as 'linuenum: text'. Missing ':' in '{line}'"
                )

            name, text = line.split(":")

            if name not in callout_markers.values():
                raise ParseError(
                    f"Callout {name} has not been created in the source code"
                )

            text = text.strip()

            callout_contents[name] = text

        # Put markers and contents together
        callouts = {"markers": callout_markers, "contents": callout_contents}

        # Source blocks must preserve the content literally
        textlines = [TextNode(line) for line in content]

        _, kwargs = merge_args(args, kwargs, ["language"])

        language = kwargs.pop("language", "text")

        self._save(
            SourceNode(
                language,
                callouts=callouts,
                highlights=highlighted_lines,
                delimiter=delimiter,
                code=textlines,
                title=title,
                kwargs=kwargs,
            )
        )

    def _parse_admonition_block(self, content, args, kwargs):
        _, kwargs = merge_args(args, kwargs, ["class", "icon", "label"])

        p = analyse(MainParser(variables=self.variables), "\n".join(content))

        self._add_footnotes(p.footnotes)

        self._save(
            AdmonitionNode(
                admclass=kwargs.pop("class"),
                icon=kwargs.pop("icon"),
                label=kwargs.pop("label"),
                content=p.nodes,
                kwargs=kwargs,
            )
        )

    def _parse_quote_block(self, content, title, args, kwargs):
        _, kwargs = merge_args(args, kwargs, ["attribution"])

        p = analyse(MainParser(), "\n".join(content))

        self._save(
            QuoteNode(
                kwargs.pop("attribution"),
                content=p.nodes,
                kwargs=kwargs,
            )
        )

    def _parse_standard_block(
        self, blocktype, content, secondary_content, title, args, kwargs
    ):
        pc = analyse(MainParser(variables=self.variables), "\n".join(content))
        ps = analyse(MainParser(variables=self.variables), "\n".join(secondary_content))

        self._add_footnotes(pc.footnotes)

        self._save(
            BlockNode(
                blocktype=blocktype,
                content=pc.nodes,
                secondary_content=ps.nodes,
                args=args,
                kwargs=kwargs,
                title=title,
            )
        )

    @parser
    def _parse_attributes(self):
        self.get_token(TokenTypes.LITERAL, "[")
        attributes = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "]")

        p = analyse(
            PreprocessVariablesParser(self.variables),
            attributes,
        )

        attributes = p.nodes[0].value

        p = analyse(ArgumentsParser(), attributes)

        self._push_attributes(p.args, p.kwargs)

    def _collect_text_content(self):
        if not self.peek_token_is(TokenTypes.TEXT):
            return None

        values = []

        while self.peek_token_is(TokenTypes.TEXT):
            values.append(self.get_token().value)
            self.get_token(TokenTypes.EOL)

        if len(values) == 0:
            return None

        return " ".join(values)

    def _parse_text_content(self, text):
        if text is None:
            return None

        p = analyse(
            PreprocessVariablesParser(self.variables),
            text,
        )

        text = p.nodes[0].value

        p = analyse(TextParser(footnotes_start_with=len(self.footnotes) + 1), text)

        # Text should return a single sentence node
        result = p.nodes[0]

        if len(p.footnotes) > 0:
            self._add_footnotes(p.footnotes)

        return result

    @parser
    def _parse_command(self):
        self.get_token(TokenTypes.LITERAL, "::")
        name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, ":")

        args = None
        kwargs = None

        with self:
            arguments = self.get_token(TokenTypes.TEXT).value
            p = analyse(ArgumentsParser(), arguments)
            args = p.args
            kwargs = p.kwargs

        self._save(CommandNode(name=name, args=args, kwargs=kwargs))

    @parser
    def _parse_variable_definition(self):
        self.get_token(TokenTypes.LITERAL, ":")
        variable_name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, ":")

        variable_value = True
        if variable_name.startswith("!"):
            variable_value = False
            variable_name = variable_name[1:]

        value = self.collect_join([Token(TokenTypes.EOL)])
        if len(value) > 0:
            variable_value = value

        if "." not in variable_name:
            self.variables[variable_name] = variable_value
        else:
            namespace, variable_name = variable_name.split(".")

            try:
                self.variables[namespace][variable_name] = variable_value
            except KeyError:
                self.variables[namespace] = {variable_name: variable_value}

    def _parse_list_nodes(self):
        with self:
            self.get_token(TokenTypes.WHITESPACE)

        header = self.get_token(TokenTypes.LITERAL, check=lambda x: x[0] in "*#").value
        self.get_token(TokenTypes.WHITESPACE)
        text = self._collect_text_content()

        content = self._parse_text_content(text)
        level = len(header)

        nodes = []
        nodes.append(ListItemNode(level, content))

        while not self.peek_token() in [Token(TokenTypes.EOF), Token(TokenTypes.EOL)]:
            # This is the SentenceNode inside the last node added to the list
            last_node_sentence = nodes[-1].content

            with self:
                self.get_token(TokenTypes.WHITESPACE)

            if len(self.peek_token().value) == level:
                header = self.get_token().value
                self.get_token(TokenTypes.WHITESPACE)
                text = self._collect_text_content()
                content = self._parse_text_content(text)
                nodes.append(ListItemNode(len(header), content))
            elif len(self.peek_token().value) > level:
                numbered = True if self.peek_token().value[0] == "#" else False
                subnodes = self._parse_list_nodes()
                last_node_sentence.content.append(ListNode(numbered, subnodes))
            else:
                break

        return nodes

    @parser
    def _parse_list(self):
        with self:
            self.get_token(TokenTypes.WHITESPACE)

        header = self.peek_token(TokenTypes.LITERAL, check=lambda x: x[0] in "*#")

        numbered = True if header.value[0] == "#" else False
        nodes = self._parse_list_nodes()
        self._save(ListNode(numbered, nodes, main_node=True))

    @parser
    def _parse_paragraph(self):
        lines = self.collect_lines([Token(TokenTypes.EOL), Token(TokenTypes.EOF)])
        text = " ".join(lines)
        sentence = self._parse_text_content(text)

        args, kwargs = self._pop_attributes()

        self._save(ParagraphNode(sentence, args=args, kwargs=kwargs))

    @parser
    def _parse_eol(self):
        self.get_token(TokenTypes.EOL)

    def _parse_functions(self):
        return [
            self._parse_eol,
            self._parse_horizontal_rule,
            self._parse_single_line_comment,
            self._parse_multi_line_comment,
            self._parse_variable_definition,
            self._parse_command,
            self._parse_title,
            self._parse_attributes,
            self._parse_header,
            self._parse_block,
            self._parse_content,
            self._parse_list,
            self._parse_paragraph,
        ]

    def _create_toc(self):
        nodes = []
        latest_by_level = {}

        for i in self.headers:
            text, level, anchor = i

            # This is the current node
            node = TocNode(level, text, anchor)

            # This collects the latest node added with a given level
            latest_by_level[level] = node

            try:
                # Simplest case, add it to the latest one
                # with a level just 1 step lower
                latest_by_level[level - 1].children.append(node)
            except KeyError:
                # Find all the latest ones added with a level lower than this
                latest = [latest_by_level.get(i, None) for i in range(1, level)]

                # Get the children list of each one, plus nodes for the root
                children = [nodes] + [i.children for i in latest if i is not None]

                # Get the nearest one and append to that
                children[-1].append(node)

        return nodes

    def parse(self):
        self._parse()

        self.toc = self._create_toc()
