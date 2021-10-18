import re
import copy

from mau.lexers.base_lexer import TokenTypes, Token
from mau.lexers.main_lexer import MainLexer
from mau.parsers.base_parser import (
    BaseParser,
    TokenError,
    ConfigurationError,
    parser,
)
from mau.parsers.text_parser import TextParser
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.nodes import (
    HorizontalRuleNode,
    TextNode,
    BlockNode,
    ContentNode,
    ContentImageNode,
    CommandNode,
    HeaderNode,
    ListNode,
    ListItemNode,
    ParagraphNode,
    TocNode,
    TocEntryNode,
    FootnotesNode,
)


class EngineError(ValueError):
    """ Used to signal that the engine selected for a code block is not known """


def header_anchor(text, level):
    """
    Return a sanitised anchor for a header.
    """

    # Everything lowercase
    sanitised_text = text.lower()

    # Get only letters, numbers, dashes, spaces, and dots
    sanitised_text = "".join(re.findall("[a-z0-9-\\. ]+", sanitised_text))

    # Remove multiple spaces
    sanitised_text = "-".join(sanitised_text.split())

    return sanitised_text


# The MainParser is in charge of parsing
# the whole input, calling other parsers
# to manage single paragraphs or other
# things like variables.
class MainParser(BaseParser):
    def __init__(self, variables=None):
        super().__init__()

        self.lexer = MainLexer()

        # This is used as a storage for attributes.
        # Block attributes are defined before the block
        # so when we parse them we store them here and
        # then use them when dealing with the block itself.
        self.argsparser = ArgumentsParser()

        # Copy the variables and make sure the "mau" namespace exists
        self.variables = copy.deepcopy(variables) if variables else {}
        if "mau" not in self.variables:
            self.variables["mau"] = {}

        self.headers = []
        self.footnote_defs = []
        self.blocks = {}
        self.toc = None

        # When we define a block we establish an alias
        # {alias:actual_block_name}
        self.block_aliases = {}

        # Each block we define can have default values
        # {actual_block_name:kwargs}
        self.block_defaults = {}

        # Each block we define can have names for unnamed arguments
        # {actual_block_name:kwargs}
        self.block_names = {}

        # Backward compatibility with Mau 1.x
        # Mau 1.x used [source] to format source, while Mau 2.x
        # uses [myblock, engine=source], so this establishes
        # a default block definition so that
        # [source] = [source, engine=source]
        # In Mau 2.x this block uses the template "block-source"
        # so any template called "source" (e.g. "source.html")
        # must be renamed.
        # This definition can be overridden by custom block definitions
        self.block_aliases["source"] = "source"
        self.block_defaults["source"] = {"engine": "source", "language": "text"}
        self.block_names["source"] = ["language"]

        self.block_aliases["admonition"] = "admonition"
        self.block_names["admonition"] = ["class", "icon", "label"]

        self.block_aliases["quote"] = "quote"
        self.block_defaults["quote"] = {"attribution": None}
        self.block_names["quote"] = ["attribution"]

        # Iterate through block definitions passed as variables
        for alias, block_definition in (
            self.variables["mau"].get("block_definitions", {}).items()
        ):
            try:
                blocktype = block_definition["blocktype"]
                self.block_aliases[alias] = blocktype
            except KeyError:
                raise ConfigurationError(
                    f"Block definition '{alias}' is missing key 'blocktype'"
                )

            try:
                self.block_defaults[blocktype] = block_definition["kwargs"]
            except KeyError:
                raise ConfigurationError(
                    f"Block definition '{alias}' is missing key 'kwargs'"
                )

        # This is a buffer for a block title
        self._title = None

        # This is the function used to create the header
        # anchors. It can be specified through
        # mau.header_anchor_function to override
        # the default one.
        self.header_anchor = self.variables["mau"].get(
            "header_anchor_function", header_anchor
        )

        self.v1_backward_compatibility = self.variables["mau"].get(
            "v1_backward_compatibility", False
        )

    def _pop_title(self):
        # This return the title and resets the
        # cached one, so no other block will
        # use it.
        title = self._title
        self._title = None
        return title

    def _push_title(self, title):
        # When we parse a title we can store it here
        # so that it is available to the next block
        # that will use it.
        self._title = title

    def _collect_lines(self, stop_tokens):
        # This collects several lines of text in a list
        # until it gets to a line that begins with one
        # of the tokens listed in stop_tokens.
        # It is useful for block or other elements that
        # are clearly surrounded by delimiters.
        lines = []

        while self.peek_token() not in stop_tokens:
            lines.append(self.collect_join([Token(TokenTypes.EOL)]))
            self.get_token(TokenTypes.EOL)

        return lines

    def _collect_text_content(self):
        # Collects all adjacent text tokens
        # into a single string

        if not self.peek_token_is(TokenTypes.TEXT):
            return None

        values = []

        # Get all tokens
        while self.peek_token_is(TokenTypes.TEXT):
            values.append(self.get_token().value)
            self.get_token(TokenTypes.EOL)

        return " ".join(values)

    def _parse_text_content(self, text):
        # Parse a text using the TextParser.

        # Replace variables
        p = PreprocessVariablesParser(self.variables).analyse(
            text,
        )
        text = p.nodes[0].value

        # Parse the text
        p = TextParser(
            footnotes_start_with=len(self.footnote_defs) + 1,
            v1_backward_compatibility=self.v1_backward_compatibility,
        ).analyse(text)

        # Text should return a single sentence node
        result = p.nodes[0]

        # Store the footnotes
        self.footnote_defs.extend(p.footnote_defs)

        return result

    @parser
    def _parse_eol(self):
        # This simply parses the end of line.

        self.get_token(TokenTypes.EOL)

    @parser
    def _parse_horizontal_rule(self):
        # The horizontal rule ---

        self.get_token(TokenTypes.LITERAL, "---")
        self.get_token(TokenTypes.EOL)

        self._save(HorizontalRuleNode())

    @parser
    def _parse_single_line_comment(self):
        # // A comment on a single line

        self.get_token(TokenTypes.TEXT, check=lambda x: x.startswith("//"))
        self.get_token(TokenTypes.EOL)

    @parser
    def _parse_multi_line_comment(self):
        # ////
        # A comment
        # on multiple lines
        # ////

        self.get_token(TokenTypes.LITERAL, "////")
        self._collect_lines([Token(TokenTypes.LITERAL, "////"), Token(TokenTypes.EOF)])
        self.force_token(TokenTypes.LITERAL, "////")

    @parser
    def _parse_variable_definition(self):
        # This parses a variable definition
        #
        # Simple variables are defined as :name:value
        # as True booleans as just :name:
        # and as False booleas as :!name:
        #
        # Variable names can use a namespace with
        # :namespace.name:value

        # Get the mandatory variable name
        self.get_token(TokenTypes.LITERAL, ":")
        variable_name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, ":")

        # Assume the variable is a flag
        variable_value = True

        # If the name starts with ! it's a false flag
        if variable_name.startswith("!"):
            variable_value = False
            variable_name = variable_name[1:]

        # Get the optional value
        value = self.collect_join([Token(TokenTypes.EOL)])

        # The value is assigned only if the variable
        # is not a negative flag. In that case it is ignored
        if variable_value and len(value) > 0:
            variable_value = value

        # If the variable name contains a dot we
        # want to use a namespace
        if "." not in variable_name:
            self.variables[variable_name] = variable_value
        else:
            # Let's ignore all others dots
            namespace, variable_name = variable_name.split(".", maxsplit=1)

            # This defines the namespace if it's not already there
            try:
                self.variables[namespace][variable_name] = variable_value
            except KeyError:
                self.variables[namespace] = {variable_name: variable_value}

    @parser
    def _parse_command(self):
        # Parse a command in the form ::command:

        self.get_token(TokenTypes.LITERAL, "::")
        name = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, ":")

        args = []
        kwargs = {}

        # Commands can have arguments
        with self:
            arguments = self.get_token(TokenTypes.TEXT).value
            self.argsparser.analyse(arguments)

            # Consume the attributes
            args, kwargs = self.argsparser.get_arguments_and_reset()

        if name == "defblock":
            # Block definitions must have at least 2 arguments,
            # the alias and the block type.
            if len(args) < 2:
                self.error(
                    "Block definitions require at least two unnamed arguments: ALIAS and BLOCKTYPE"
                )

            block_alias = args.pop(0)
            block_type = args.pop(0)

            self.block_aliases[block_alias] = block_type
            self.block_defaults[block_type] = kwargs
            self.block_names[block_type] = args

            return None

        self._save(CommandNode(name=name, args=args, kwargs=kwargs))

    @parser
    def _parse_title(self):
        # Parse a title in the form
        #
        # . This is a title
        # or
        # .This is a title

        # Parse the mandatory dot
        self.get_token(TokenTypes.LITERAL, ".")

        # Parse the optional white spaces
        with self:
            self.get_token(TokenTypes.WHITESPACE)

        # Get the text of the title
        text = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.EOL)

        # Titles can contain Mau code
        p = TextParser(
            footnotes_start_with=len(self.footnote_defs) + 1,
            v1_backward_compatibility=self.v1_backward_compatibility,
        ).analyse(text)
        title = p.nodes[0]

        self._push_title(title)

    @parser
    def _parse_attributes(self):
        # Parse block attributes in the form
        # [unnamed1, unnamed2, ..., named1=value1, name2=value2, ...]

        self.get_token(TokenTypes.LITERAL, "[")
        attributes = self.get_token(TokenTypes.TEXT).value
        self.get_token(TokenTypes.LITERAL, "]")

        # Attributes can use variables
        p = PreprocessVariablesParser(self.variables).analyse(
            attributes,
        )
        attributes = p.nodes[0].value

        # Parse the arguments
        self.argsparser.analyse(attributes)

    @parser
    def _parse_header(self):
        # Parse a header in the form
        #
        # = Header
        #
        # The number of equal signs is arbitrary
        # and represents the level of the header.
        # Headers are automatically assigned an anchor
        # created using the provided function self.header_anchor
        #
        # Headers in the form
        # =! Header
        # are rendered but not included in the TOC

        # Get all the equal signs
        header = self.get_token(
            TokenTypes.LITERAL, check=lambda x: x.startswith("=")
        ).value

        # Get the mandatory white spaces
        self.get_token(TokenTypes.WHITESPACE)

        # Check if the header has to be in the TOC
        in_toc = True
        if header.endswith("!"):
            header = header[:-1]
            in_toc = False

        # Get the text of the header and calculate the level
        text = self.get_token(TokenTypes.TEXT).value
        level = len(header)

        # Generate the anchor and append it to the TOC
        anchor = self.header_anchor(text, level)

        # Consume the attributes
        args, kwargs = self.argsparser.get_arguments_and_reset()

        # Generate the header node
        header_node = HeaderNode(value=text, level=level, anchor=anchor, kwargs=kwargs)

        if in_toc:
            self.headers.append(header_node)

        self._save(header_node)

    @parser
    def _parse_block(self):
        # Parse a block in the form
        #
        # [block_type]
        # ----
        # Content
        # ----
        # Optional secondary content
        #
        # Blocks are delimited by 4 consecutive identical characters.

        # Get the delimiter and check the length
        delimiter = self.get_token(TokenTypes.TEXT).value
        if len(delimiter) != 4 or len(set(delimiter)) != 1:
            raise TokenError
        self.get_token(TokenTypes.EOL)

        # Collect everything until the next delimiter
        content = self._collect_lines(
            [Token(TokenTypes.TEXT, delimiter), Token(TokenTypes.EOF)]
        )
        self.force_token(TokenTypes.TEXT, delimiter)
        self.get_token(TokenTypes.EOL)

        # Get the optional secondary content
        secondary_content = self._collect_lines(
            [Token(TokenTypes.EOL), Token(TokenTypes.EOF)]
        )

        # Consume the title
        title = self._pop_title()

        # The first unnamed argument is the block type
        blocktype = self.argsparser.pop()

        # If there is a block alias for blocktype replace it
        # otherwise use the blocktype we already have
        blocktype = self.block_aliases.get(blocktype, blocktype)

        # Assign names

        self.argsparser.set_names_and_defaults(
            self.block_names.get(blocktype, []), self.block_defaults.get(blocktype, {})
        )

        # Consume the attributes
        args, kwargs = self.argsparser.get_arguments_and_reset()

        # Extract classes and convert them into a list
        classes = [i for i in kwargs.pop("classes", "").split(",") if len(i) > 0]

        # Extract condition if present and process it
        condition = kwargs.pop("condition", "")

        # Run this only if there is a condition on this block
        if len(condition) > 0:
            try:
                # The condition should be either test:variable:value or test:variable:
                test, variable, value = condition.split(":")
            except ValueError:
                self.error(
                    f'Condition {condition} is not in the form "test:variable:value" or "test:variable:'
                )

            # If there is no value use True
            if len(value) == 0:
                value = True

            # Check if the variable matches the value and apply the requested test
            match = self.variables.get(variable) == value
            result = True if test == "if" else False

            # If the condition is not satisfied return
            if match is not result:
                return

        # Extract the preprocessor
        preprocessor = kwargs.pop("preprocessor", "none")

        # Extract the engine
        engine = kwargs.pop("engine", "default")

        # Create the node parameters according to the engine
        if engine in ["raw", "mau"]:
            # Engine "raw" doesn't process the content,
            # so we just pass it untouched in the form of
            # a TextNode per line. The same is true for "mau"
            # as the visitor will have to fire up an new parser
            # to process the content.
            content = [TextNode(line) for line in content]
            secondary_content = [TextNode(line) for line in secondary_content]
        elif engine == "source":
            # Engine "source" extracts the content (source code),
            # the callouts, and the highlights.
            # The default language is "text".

            content, callouts, highlights = self._parse_source_engine(
                content, secondary_content, kwargs
            )
            secondary_content = []

            kwargs["callouts"] = callouts
            kwargs["highlights"] = highlights
            kwargs["language"] = kwargs.get("language", "text")

        elif engine == "default":
            # This is the default engine and it parses
            # both content and secondary content using a new parser
            # but then merges headers and footnotes into the
            # current one.

            # Parse the primary and secondary content and record footnotes
            pc = MainParser(variables=self.variables).analyse("\n".join(content))
            ps = MainParser(variables=self.variables).analyse(
                "\n".join(secondary_content)
            )
            content = pc.nodes
            secondary_content = ps.nodes

            self.footnote_defs.extend(pc.footnote_defs)
            self.headers.extend(pc.headers)
        else:
            raise EngineError(f"Engine {engine} is not available")

        self._save(
            BlockNode(
                blocktype=blocktype,
                content=content,
                secondary_content=secondary_content,
                args=args,
                classes=classes,
                engine=engine,
                preprocessor=preprocessor,
                kwargs=kwargs,
                title=title,
            )
        )

    def _parse_source_engine(self, content, secondary_content, kwargs):
        # Parse a source block in the form
        #
        # [source, language, attributes...]
        # ----
        # content
        # ----
        #
        # Source blocks support the following attributes
        #
        # callouts=":" The separator used by callouts
        # highlight="@" The special character to turn on highlight
        #
        # [source, language, attributes...]
        # ----
        # content:1:
        # ----
        #
        # [source, language, attributes...]
        # ----
        # content:@:
        # ----
        #
        # Callout descriptions can be added to the block
        # as secondary content with the syntax
        #
        # [source, language, attributes...]
        # ----
        # content:name:
        # ----
        # <name>: <description>
        #
        # Since Mau uses Pygments, the attribute language
        # is one of the langauges supported by that tool.

        # Get the delimiter for callouts (":" by default)
        delimiter = kwargs.pop("callouts", ":")

        # A dictionary that contains callout markers in
        # the form {linenum:name}
        callout_markers = {}

        # Get the marker for highlighted lines ("@" by default)
        highlight_marker = kwargs.pop("highlight", "@")

        # A list of highlighted lines
        highlighted_lines = []

        # This is a list of all lines that might contain
        # a callout. They will be further processed
        # later to be sure.
        lines_with_callouts = [
            (linenum, line)
            for linenum, line in enumerate(content)
            if line.endswith(delimiter)
        ]

        # Each line in the previous list is processed
        # and stored if it contains a callout
        for linenum, line in lines_with_callouts:
            # Remove the final delimiter
            line = line[:-1]

            splits = line.split(delimiter)
            if len(splits) < 2:
                # It's a trap! There are no separators left
                continue

            # Get the callout and the line
            callout_name = splits[-1]
            line = delimiter.join(splits[:-1])

            content[linenum] = line

            # Check if we want to just highlight the line
            if callout_name == highlight_marker:
                highlighted_lines.append(linenum)
            else:
                callout_markers[linenum] = callout_name

        # A dictionary that contains the text for each
        # marker in the form {name:text}
        callout_contents = {}

        # If there was secondary content it should be formatted
        # with callout names followed by colon and the
        # callout text.
        for line in secondary_content:
            if ":" not in line:
                self.error(
                    f"Callout description should be written as 'name: text'. Missing ':' in '{line}'"
                )

            name, text = line.split(":")

            if name not in callout_markers.values():
                self.error(f"Callout {name} has not been created in the source code")

            text = text.strip()

            callout_contents[name] = text

        # Put markers and contents together
        callouts = {"markers": callout_markers, "contents": callout_contents}

        # Source blocks must preserve the content literally
        textlines = [TextNode(line) for line in content]

        return textlines, callouts, highlighted_lines

        # self._save(
        #     SourceNode(
        #         language,
        #         callouts=callouts,
        #         highlights=highlighted_lines,
        #         delimiter=delimiter,
        #         code=textlines,
        #         title=title,
        #         kwargs=kwargs,
        #     )
        # )

    @parser
    def _parse_content(self):
        # Parse attached content in the form
        #
        # [attributes]
        # << content_type:uri

        # Get the mandatory "<<" and white spaces
        self.get_token(TokenTypes.LITERAL, check=lambda x: x.startswith("<<"))
        self.get_token(TokenTypes.WHITESPACE)

        # Get the content type and the content URI
        content_type_and_uri = self.get_token(TokenTypes.TEXT).value
        content_type, uri = content_type_and_uri.split(":", maxsplit=1)

        title = self._pop_title()

        if content_type == "image":
            return self._parse_content_image(uri, title)

        return self._parse_standard_content(content_type, uri, title)

    def _parse_content_image(self, uri, title):
        # Parse a content image in the form
        #
        # [alt_text, classes]
        # << image:uri
        #
        # alt_text is the alternate text to use is the image is not reachable
        # and classes is a comma-separated list of classes

        # Assign names and consume the attributes
        self.argsparser.set_names_and_defaults(
            ["alt_text", "classes"], {"alt_text": None, "classes": None}
        )
        args, kwargs = self.argsparser.get_arguments_and_reset()

        alt_text = kwargs.pop("alt_text")
        classes = kwargs.pop("classes")

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

    def _parse_standard_content(self, content_type, uri, title):
        # This is the fallback for an unknown content type

        # Consume the attributes
        args, kwargs = self.argsparser.get_arguments_and_reset()

        self._save(
            ContentNode(
                uri=uri,
                title=title,
                args=args,
                kwargs=kwargs,
            )
        )

    @parser
    def _parse_list(self):
        # Parse a list.
        # Lists can be ordered (using numbers)
        #
        # * One item
        # * Another item
        #
        # or unordered (using bullets)
        #
        # # Item 1
        # # Item 2
        #
        # The number of headers increases
        # the depth of each item
        #
        # # Item 1
        # ## Sub-Item 1.1
        #
        # Spaces before and after the header are ignored.
        # So the previous list can be also written
        #
        # # Item 1
        #   ## Sub-Item 1.1
        #
        # Ordered and unordered lists can be mixed.
        #
        # * One item
        # ## Sub Item 1
        # ## Sub Item 2
        #

        # Ignore initial white spaces
        with self:
            self.get_token(TokenTypes.WHITESPACE)

        # Get the header and decide if it's a numbered or unnumbered list
        header = self.peek_token(TokenTypes.LITERAL, check=lambda x: x[0] in "*#")
        numbered = True if header.value[0] == "#" else False

        # Parse all the following items
        nodes = self._parse_list_nodes()

        self._save(ListNode(numbered, nodes, main_node=True))

    def _parse_list_nodes(self):
        # This parses all items of a list

        # Ignore initial white spaces
        with self:
            self.get_token(TokenTypes.WHITESPACE)

        # Parse the header and ignore the following white spaces
        header = self.get_token(TokenTypes.LITERAL, check=lambda x: x[0] in "*#").value
        self.get_token(TokenTypes.WHITESPACE)

        # Collect and parse the text of the item
        text = self._collect_text_content()
        content = self._parse_text_content(text)

        # Compute the level of the item
        level = len(header)

        nodes = []
        nodes.append(ListItemNode(level, content))

        while not self.peek_token() in [Token(TokenTypes.EOF), Token(TokenTypes.EOL)]:
            # This is the SentenceNode inside the last node added to the list
            # which is used to append potential nested nodes
            last_node_sentence = nodes[-1].content

            # Ignore the initial white spaces
            with self:
                self.get_token(TokenTypes.WHITESPACE)

            if len(self.peek_token().value) == level:
                # The new item is on the same level

                # Get the header
                header = self.get_token().value

                # Ignore white spaces
                self.get_token(TokenTypes.WHITESPACE)

                # Collect and parse the text of the item
                text = self._collect_text_content()
                content = self._parse_text_content(text)

                nodes.append(ListItemNode(len(header), content))
            elif len(self.peek_token().value) > level:
                # The new item is on a deeper level

                # Treat the new line as a new list
                numbered = True if self.peek_token().value[0] == "#" else False
                subnodes = self._parse_list_nodes()
                last_node_sentence.content.append(ListNode(numbered, subnodes))
            else:
                break

        return nodes

    @parser
    def _parse_paragraph(self):
        # This parses a paragraph.
        # Paragraphs can be written on multiple lines and
        # end with an empty line.

        # Get all the lines, join them and parse them
        lines = self._collect_lines([Token(TokenTypes.EOL), Token(TokenTypes.EOF)])
        text = " ".join(lines)
        sentence = self._parse_text_content(text)

        # Consume the attributes
        args, kwargs = self.argsparser.get_arguments_and_reset()

        self._save(ParagraphNode(sentence, args=args, kwargs=kwargs))

    def _parse_functions(self):
        # All the functions that this parser provides.

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
        # Create the TOC from the list of headers.

        nodes = []
        latest_by_level = {}

        for header_node in self.headers:
            # This is the current node
            node = TocEntryNode(header_node)
            level = header_node.level

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

        return TocNode(entries=nodes)

    def parse(self):
        super().parse()

        self.toc = self._create_toc()
        self.footnotes = FootnotesNode(entries=self.footnote_defs)
