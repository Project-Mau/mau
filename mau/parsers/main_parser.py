# pylint: disable=too-many-lines

from mau.environment.environment import Environment
from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.lexers.main_lexer import MainLexer
from mau.lexers.main_lexer import TokenTypes as MLTokenTypes
from mau.nodes.block import BlockNode
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import RawNode
from mau.nodes.lists import ListItemNode, ListNode
from mau.nodes.page import ContainerNode, HorizontalRuleNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.attributes import AttributesManager
from mau.parsers.base_parser import BaseParser
from mau.parsers.footnotes import FootnotesManager
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.references import ReferencesManager
from mau.parsers.text_parser import TextParser
from mau.parsers.toc import TocManager, header_anchor
from mau.tokens.tokens import Token


# The MainParser is in charge of parsing
# the whole input, calling other parsers
# to manage single paragraphs or other
# things like variables.
class MainParser(BaseParser):
    lexer_class = MainLexer

    def __init__(self, environment):
        super().__init__(environment)

        self.footnotes_manager = FootnotesManager(self)
        self.references_manager = ReferencesManager(self)
        self.toc_manager = TocManager(self)
        self.attributes_manager = AttributesManager(self)

        # When we define a block we establish an alias
        # {alias:actual_block_name}.
        self.block_aliases = {}

        # Each block we define can have default values
        # {actual_block_name:kwargs}.
        self.block_defaults = {}

        # Each block we define can have names for unnamed arguments
        # {actual_block_name:kwargs}.
        self.block_names = {}

        # This establishes a default block definition so that
        # [source] = [source, engine=source]
        # This definition can be overridden by custom block definitions.
        self.block_aliases["source"] = None
        self.block_defaults["source"] = {"engine": "source", "language": "text"}
        self.block_names["source"] = ["language"]

        self.block_aliases["footnote"] = None
        self.block_defaults["footnote"] = {"engine": "footnote"}
        self.block_names["footnote"] = ["name"]

        self.block_aliases["reference"] = None
        self.block_defaults["reference"] = {"engine": "reference"}
        self.block_names["reference"] = ["type", "name"]

        self.block_aliases["admonition"] = "admonition"
        self.block_names["admonition"] = ["class", "icon", "label"]

        # Iterate through block definitions passed as variables
        # for alias, block_definition in (
        #     self.variables["mau"].get("block_definitions", {}).items()
        # ):
        #     try:
        #         subtype = block_definition["subtype"]
        #         self.block_aliases[alias] = subtype
        #     except KeyError:
        #         raise ConfigurationError(
        #             f"Block definition '{alias}' is missing key 'subtype'"
        #         )

        #     try:
        #         self.block_defaults[subtype] = block_definition["kwargs"]
        #     except KeyError:
        #         raise ConfigurationError(
        #             f"Block definition '{alias}' is missing key 'kwargs'"
        #         )

        # This is a buffer for a block title
        self._title = None

        # This is the function used to create the header
        # anchors. It can be specified through
        # mau.header_anchor_function to override
        # the default one.
        self.header_anchor = self.environment.getvar(
            "mau.parser.header_anchor_function", header_anchor
        )

        # The number of nodes in the latest ordered list,
        # used to calculate the beginning value of them
        # next one when start=auto
        self.latest_ordered_list_length = 0

        # This is the final output of the parser
        self.output = {}

    def _process_functions(self):
        # All the functions that this parser provides.

        return [
            self._process_eol,
            self._process_horizontal_rule,
            self._process_single_line_comment,
            self._process_multi_line_comment,
            self._parse_variable_definition,
            self._process_command,
            self._process_title,
            self._process_arguments,
            self._process_header,
            self._process_block,
            self._process_content,
            self._process_list,
            self._process_paragraph,
        ]

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

    def _collect_text_content(self):
        # Collects all adjacent text tokens
        # into a single string

        if not self._peek_token_is(BLTokenTypes.TEXT):  # pragma: no cover
            return None

        values = []

        # Get all tokens
        while self._peek_token_is(BLTokenTypes.TEXT):
            values.append(self._get_token().value)
            self._get_token(BLTokenTypes.EOL)

        return " ".join(values)

    def _parse_text_content(self, text, context=None):
        # Parse a piece of text using the TextParser.

        current_context = context or self._current_token.context

        # Replace variables
        preprocess_parser = PreprocessVariablesParser.analyse(
            text,
            current_context,
            self.environment,
        )
        text = preprocess_parser.nodes[0].value

        # Parse the text
        text_parser = TextParser.analyse(text, current_context, self.environment)

        # A text parser returns a single sentence node
        result = text_parser.nodes[0]

        # Extract the footnote mentions
        # found in this piece of text
        self.footnotes_manager.update_mentions(text_parser.footnotes)

        # Extract the reference mentions
        # found in this piece of text
        self.references_manager.update_mentions(text_parser.references)

        return result

    def _process_eol(self):
        # This simply parses the end of line.

        self._get_token(BLTokenTypes.EOL)

        return True

    def _process_horizontal_rule(self):
        # The horizontal rule ---

        self._get_token(MLTokenTypes.HORIZONTAL_RULE)

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        self._save(HorizontalRuleNode(subtype, args, kwargs, tags))

        return True

    def _process_single_line_comment(self):
        # // A comment on a single line

        self._get_token(MLTokenTypes.COMMENT)
        self._get_token(BLTokenTypes.EOL)

        return True

    def _process_multi_line_comment(self):
        # ////
        # A comment
        # on multiple lines
        # ////

        self._get_token(MLTokenTypes.MULTILINE_COMMENT)
        self._collect([Token(MLTokenTypes.MULTILINE_COMMENT, "////")])
        self._force_token(MLTokenTypes.MULTILINE_COMMENT, "////")

        return True

    def _parse_variable_definition(self):
        # This parses the definition of a variable
        #
        # Simple variables are defined as :name:value
        # as True booleans as just :name:
        # and as False booleas as :!name:
        #
        # Variable names can use a namespace with
        # :namespace.name:value

        # Get the mandatory variable name
        self._get_token(MLTokenTypes.VARIABLE, ":")
        variable_name = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.LITERAL, ":")

        # Assume the variable is a flag
        variable_value = True

        # If the name starts with ! it's a false flag
        if variable_name.startswith("!"):
            variable_value = False
            variable_name = variable_name[1:]

        # Get the optional value
        value = self._collect_join([Token(BLTokenTypes.EOL)])

        # The value is assigned only if the variable
        # is not a negative flag. In that case it is ignored
        if variable_value and len(value) > 0:
            variable_value = value

        self.environment.setvar(variable_name, variable_value)

        return True

    def _process_command(self):
        # Parse a command in the form ::command:arguments

        self._get_token(MLTokenTypes.COMMAND, "::")
        name = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.LITERAL, ":")

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Commands can have arguments
        command_args = []
        command_kwargs = {}
        with self:
            arguments = self._get_token(BLTokenTypes.TEXT).value

            current_context = self._current_token.context

            arguments_parser = ArgumentsParser.analyse(
                arguments, current_context, self.environment
            )

            command_args, command_kwargs, _, _ = arguments_parser.process_arguments()

        if name == "defblock":
            # Block definitions must have at least 2 arguments,
            # the alias and the block type.
            if len(command_args) < 2:
                self._error(
                    "Block definitions require at least two unnamed arguments: ALIAS and SUBTYPE"
                )

            block_alias = command_args.pop(0)
            block_type = command_args.pop(0)

            self.block_aliases[block_alias] = block_type
            self.block_defaults[block_alias] = command_kwargs
            self.block_names[block_alias] = command_args

        elif name == "toc":
            self.toc_manager.create_toc_node(subtype, args, kwargs, tags)

        elif name == "footnotes":
            # Create a footnotes node
            self.footnotes_manager.create_node(subtype, args, kwargs, tags)

        elif name == "references":
            # Assign names
            command_args, command_kwargs = self._set_names_and_defaults(
                command_args, command_kwargs, ["content_type"]
            )

            content_type = command_kwargs.pop("content_type")

            # Create a references node
            self.references_manager.create_node(
                content_type,
                subtype,
                args,
                kwargs,
                tags,
            )

        return True

    def _process_title(self):
        # Parse a title in the form
        #
        # . This is a title
        # or
        # .This is a title

        # Parse the mandatory dot
        self._get_token(MLTokenTypes.TITLE, ".")

        # Parse the optional white spaces
        with self:
            self._get_token(BLTokenTypes.WHITESPACE)

        # Get the text of the title
        text = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.EOL)

        current_context = self._current_token.context

        # Titles can contain Mau code
        text_parser = TextParser.analyse(text, current_context, self.environment)

        title = text_parser.nodes[0]

        self._push_title(title)

        return True

    def _process_arguments(self):
        # Parse arguments in the form
        # [unnamed1, unnamed2, ..., named1=value1, name2=value2, ...]

        self._get_token(MLTokenTypes.ARGUMENTS, "[")
        text = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.LITERAL, "]")

        current_context = self._current_token.context

        preprocess_parser = PreprocessVariablesParser.analyse(
            text,
            current_context,
            self.environment,
        )
        text = preprocess_parser.nodes[0].value

        # Parse the text
        arguments_parser = ArgumentsParser.analyse(
            text, current_context, self.environment
        )

        args, kwargs, tags, subtype = arguments_parser.process_arguments()
        self.attributes_manager.push(args, kwargs, tags, subtype)

        return True

    def _process_header(self):
        # Parse a header in the form
        #
        # = Header
        #
        # The number of equal signs is arbitrary
        # and represents the level of the header.
        # Headers are automatically assigned an anchor
        # created using the provided function self.header_anchor

        # Get all the equal signs
        header = self._get_token(MLTokenTypes.HEADER).value

        # Get the mandatory white spaces
        self._get_token(BLTokenTypes.WHITESPACE)

        # Get the text of the header and calculate the level
        text = self._get_token(BLTokenTypes.TEXT).value
        level = len(header)

        # Create the anchor
        anchor = self.header_anchor(text, level)

        # Consume the parser arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        node = HeaderNode(
            value=text,
            level=str(level),
            anchor=anchor,
            subtype=subtype,
            args=args,
            tags=tags,
            kwargs=kwargs,
        )

        self.toc_manager.add_header_node(node)

        self._save(node)

        return True

    def _collect_lines(self, stop_tokens):
        # This collects several lines of text in a list
        # until it gets to a line that begins with one
        # of the tokens listed in stop_tokens.
        # It is useful for block or other elements that
        # are clearly surrounded by delimiters.
        lines = []

        while self._peek_token() not in stop_tokens:
            lines.append(self._collect_join([Token(BLTokenTypes.EOL)]))
            self._get_token(BLTokenTypes.EOL)

        return lines

    def _process_block(
        self,
    ):  # pylint: disable=too-many-statements, too-many-branches, too-many-locals
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
        delimiter = self._get_token(MLTokenTypes.BLOCK).value

        self._get_token(BLTokenTypes.EOL)

        # Collect everything until the next delimiter
        content = self._collect_lines(
            [Token(MLTokenTypes.BLOCK, delimiter), Token(BLTokenTypes.EOF)]
        )

        self._force_token(MLTokenTypes.BLOCK, delimiter)
        self._get_token(BLTokenTypes.EOL)

        # Get the optional secondary content
        secondary_content = self._collect_lines(
            [Token(BLTokenTypes.EOL), Token(BLTokenTypes.EOF)]
        )

        if delimiter in secondary_content:
            # This probably means that the input contains an error
            # and we are in a situation like

            # ----
            #
            # ----
            # Text
            # ----

            # Where ["Text", "----"] is considered the secondary content
            # of an empty block.
            self._error(
                "Detected unclosed block (possibly before this line)"
            )  # pragma: no cover

        # Create the block
        block = BlockNode(content, secondary_content)

        # Consume the title
        block.title = self._pop_title()

        # Consume the arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # The first unnamed argument is the block type
        # try:
        #     subtype = args.pop(0)
        # except IndexError:
        #     subtype = None

        # If there is a block alias for subtype replace it
        # otherwise use the subtype we already have

        # Retrieve the block names and defaults for the
        # specific type of block

        block_names = self.block_names.get(subtype, [])
        block_defaults = self.block_defaults.get(subtype, {})

        # Now replace the alias with the true block type
        block.subtype = self.block_aliases.get(subtype, subtype)

        # Assign names
        args, kwargs = self._set_names_and_defaults(
            args,
            kwargs,
            block_names,
            block_defaults,
        )

        # Extract classes and convert them into a list
        classes = []
        if "classes" in kwargs:
            classes = kwargs.pop("classes")

            if classes:
                classes = classes.split(",")
        block.classes = classes

        # Extract condition if present and process it
        condition = kwargs.pop("condition", None)

        # Run this only if there is a condition on this block
        if condition is not None:
            try:
                # The condition should be either test:variable:value or test:variable:
                test, variable, value = condition.split(":")
            except ValueError:
                self._error(
                    (
                        f"Condition {condition} is not in the form"
                        '"test:variable:value" or "test:variable:'
                    )
                )

            # If there is no value use True
            if len(value) == 0:
                value = True

            # Check if the variable matches the value and apply the requested test
            match = self.environment.getvar(variable) == value
            result = test == "if"

            # If the condition is not satisfied return
            if match is not result:
                return True

        # Extract the preprocessor
        block.preprocessor = kwargs.pop("preprocessor", "none")

        # Extract the engine
        block.engine = kwargs.pop("engine", None)

        block.args = args
        block.kwargs = kwargs
        block.tags = tags

        if block.engine is None:
            self._parse_default_engine(block)
        elif block.engine == "source":
            self._parse_source_engine(block)
        elif block.engine == "footnote":
            self._parse_footnote_engine(block)
        elif block.engine == "reference":
            self._parse_reference_engine(block)
        elif block.engine == "raw":
            self._parse_raw_engine(block)
        elif block.engine == "mau":
            self._parse_mau_engine(block)
        else:
            self._error(f"Engine {block.engine} is not available")

        return True

    def _parse_footnote_engine(self, block):
        # The current block contains footnote data.
        # Extract the content and store it in
        # the footnotes manager.
        name = block.kwargs.pop("name")

        content_parser = MainParser.analyse(
            "\n".join(block.content),
            self._current_token.context,
            self.environment,
        )

        self.footnotes_manager.add_data(name, content_parser.nodes)

    def _parse_reference_engine(self, block):
        content_type = block.kwargs["type"]
        name = block.kwargs["name"]

        content_parser = MainParser.analyse(
            "\n".join(block.content),
            self._current_token.context,
            self.environment,
        )

        self.references_manager.add_data(content_type, name, content_parser.nodes)

    def _parse_raw_engine(self, block):
        # Engine "raw" doesn't process the content,
        # so we just pass it untouched in the form of
        # a RawNode per line.
        block.content = [RawNode(line) for line in block.content]
        block.secondary_content = [RawNode(line) for line in block.secondary_content]

        self._save(block)

    def _parse_default_engine(self, block):
        current_context = self._current_token.context

        environment = self.environment

        content_parser = MainParser.analyse(
            "\n".join(block.content),
            current_context,
            environment,
        )

        secondary_content_parser = MainParser.analyse(
            "\n".join(block.secondary_content),
            current_context,
            environment,
        )

        block.content = content_parser.nodes
        block.secondary_content = secondary_content_parser.nodes

        # The footnote mentions and definitions
        # found in this block are part of the
        # main document. Import them.
        self.footnotes_manager.update(content_parser.footnotes_manager)

        # The reference mentions and definitions
        # found in this block are part of the
        # main document. Import them.
        self.references_manager.update(content_parser.references_manager)

        self.toc_manager.update(content_parser.toc_manager)

        self._save(block)

    def _parse_mau_engine(self, block):
        current_context = self._current_token.context

        environment = Environment()

        content_parser = MainParser.analyse(
            "\n".join(block.content),
            current_context,
            environment,
        )

        secondary_content_parser = MainParser.analyse(
            "\n".join(block.secondary_content),
            current_context,
            environment,
        )

        block.content = content_parser.nodes
        block.secondary_content = secondary_content_parser.nodes

        self._save(block)

    def _parse_source_engine(self, block):  # pylint: disable=too-many-locals
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
        delimiter = block.kwargs.pop("callouts", ":")

        # A list that contains callout markers in
        # the form (linenum,name)
        callout_markers = []

        # Get the marker for highlighted lines ("@" by default)
        highlight_marker = block.kwargs.pop("highlight", "@")

        # A list of highlighted lines
        highlighted_lines = []

        # Source blocks preserve anything is inside

        # This is a list of all lines that might contain
        # a callout. They will be further processed
        # later to be sure.
        lines_with_callouts = [
            (linenum, line)
            for linenum, line in enumerate(block.content)
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

            block.content[linenum] = line

            # Check if we want to just highlight the line
            if callout_name == highlight_marker:
                highlighted_lines.append(linenum)
            else:
                callout_markers.append(CalloutNode(linenum, callout_name))

        # A list of CalloutEntryNode objects that contain the
        # text for each marker
        callout_contents = []

        # If there was secondary content it should be formatted
        # with callout names followed by colon and the
        # callout text.
        for line in block.secondary_content:
            if ":" not in line:
                self._error(
                    (
                        "Callout description should be written "
                        f"as 'name: text'. Missing ':' in '{line}'"
                    )
                )

            name, text = line.split(":")

            text = text.strip()

            callout_contents.append(CalloutsEntryNode(name, text))

        # Source blocks must preserve the content literally.
        # However, we need to remove escape characters from directives.
        # Directives are processed by the lexer, so if we want to
        # prevent Mau from interpreting them we have to escape them.
        # Escape characters are preserved by source blocks as anything
        # else, but in this case the character should be removed.
        textlines = []
        for line in block.content:
            if line.startswith(r"\::#"):
                line = line[1:]

            textlines.append(RawNode(line))

        self._save(
            SourceNode(
                subtype=block.subtype,
                code=textlines,
                language=block.kwargs["language"],
                callouts=callout_contents,
                highlights=highlighted_lines,
                markers=callout_markers,
                title=block.title,
            )
        )

    def _process_content(self):
        # Parse content in the form
        #
        # << content_type:URI

        # Get the mandatory "<<"
        self._get_token(MLTokenTypes.CONTENT)

        with self:
            self._get_token(BLTokenTypes.WHITESPACE)

        # Get the content type
        content_type = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.LITERAL, ":")

        title = self._pop_title()

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Read the content URIs
        uri_args = []
        uri_kwargs = {}
        with self:
            arguments = self._get_token(BLTokenTypes.TEXT).value

            current_context = self._current_token.context

            arguments_parser = ArgumentsParser.analyse(
                arguments, current_context, self.environment
            )

            uri_args, uri_kwargs, _, _ = arguments_parser.process_arguments()

        if content_type == "image":
            return self._parse_content_image(
                uri_args, uri_kwargs, title, subtype, args, kwargs, tags
            )

        return self._parse_standard_content(
            content_type, uri_args, uri_kwargs, title, subtype, args, kwargs, tags
        )

    def _parse_content_image(
        self, uri_args, uri_kwargs, title, subtype, args, kwargs, tags
    ):
        # Parse a content image in the form
        #
        # << image:uri,alt_text,classes
        #
        # alt_text is the alternate text to use is the image is not reachable
        # and classes is a comma-separated list of classes

        # Consume the arguments
        args, kwargs = self._set_names_and_defaults(
            args,
            kwargs,
            ["alt_text", "classes"],
            {"alt_text": None, "classes": None},
        )

        uri = uri_args[0]
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
                subtype=subtype,
                args=args,
                kwargs=kwargs,
                tags=tags,
            )
        )

        return True

    def _parse_standard_content(
        self, content_type, uri_args, uri_kwargs, title, subtype, args, kwargs, tags
    ):
        # This is the fallback for an unknown content type

        self._save(
            ContentNode(
                content_type=content_type,
                uri_args=uri_args,
                uri_kwargs=uri_kwargs,
                title=title,
                subtype=subtype,
                args=args,
                kwargs=kwargs,
                tags=tags,
            )
        )

        return True

    def _process_list(self):
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
            self._get_token(BLTokenTypes.WHITESPACE)

        # Get the header and decide if it's a numbered or unnumbered list
        header = self._peek_token(MLTokenTypes.LIST)
        numbered = header.value[0] == "#"

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Parse all the following items
        nodes = self._process_list_nodes()

        if kwargs.get("start") == "auto":
            kwargs["start"] = str(self.latest_ordered_list_length + 1)
            self.latest_ordered_list_length += len(nodes)
        else:
            self.latest_ordered_list_length = len(nodes)

        self._save(
            ListNode(
                numbered,
                nodes,
                main_node=True,
                subtype=subtype,
                args=args,
                kwargs=kwargs,
                tags=tags,
            )
        )

        return True

    def _process_list_nodes(self):
        # This parses all items of a list

        # Ignore initial white spaces
        with self:
            self._get_token(BLTokenTypes.WHITESPACE)

        # Parse the header and ignore the following white spaces
        header = self._get_token(MLTokenTypes.LIST).value
        self._get_token(BLTokenTypes.WHITESPACE)

        # Get the context of the first text token
        context = self._peek_token().context

        # Collect and parse the text of the item
        text = self._collect_text_content()
        content = self._parse_text_content(text, context)

        # Compute the level of the item
        level = len(header)

        nodes = []
        nodes.append(ListItemNode(str(level), content))

        while self._peek_token() not in [
            Token(BLTokenTypes.EOF),
            Token(BLTokenTypes.EOL),
        ]:
            # This is the SentenceNode inside the last node added to the list
            # which is used to append potential nested nodes
            last_node_sentence = nodes[-1].content

            # Ignore the initial white spaces
            with self:
                self._get_token(BLTokenTypes.WHITESPACE)

            if len(self._peek_token().value) == level:
                # The new item is on the same level

                # Get the header
                header = self._get_token().value

                # Ignore white spaces
                self._get_token(BLTokenTypes.WHITESPACE)

                # Get the context of the first text token
                context = self._peek_token().context

                # Collect and parse the text of the item
                text = self._collect_text_content()
                content = self._parse_text_content(text, context)

                level = len(header)

                nodes.append(ListItemNode(str(level), content))
            elif len(self._peek_token().value) > level:
                # The new item is on a deeper level

                # Treat the new line as a new list
                numbered = self._peek_token().value[0] == "#"
                subnodes = self._process_list_nodes()

                last_node_sentence.content.append(ListNode(numbered, subnodes))
            else:
                break

        return nodes

    def _process_paragraph(self):
        # This parses a paragraph.
        # Paragraphs can be written on multiple lines and
        # end with an empty line.

        # Get the context of the first token we are going to process
        context = self._peek_token().context

        # Each line ends with EOL. This collects everything
        # until the EOL, then removes it. If the next token
        # is EOL we know that the paragraph is ended, otherwise
        # we continue to collect. If the token is EOF we
        # reached the end and we have to stop anyway.
        lines = []
        while self._peek_token() not in [
            Token(BLTokenTypes.EOL),
            Token(BLTokenTypes.EOF),
        ]:
            lines.append(
                self._collect_join(
                    [
                        Token(BLTokenTypes.EOL),
                    ]
                )
            )
            self._get_token(BLTokenTypes.EOL)

        text = " ".join(lines)
        sentence = self._parse_text_content(text, context)

        # Consume the arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        self._save(
            ParagraphNode(
                sentence, subtype=subtype, args=args, kwargs=kwargs, tags=tags
            )
        )

        return True

    def parse(self, tokens):
        super().parse(tokens)

        # This processes all footnotes stored in
        # the manager merging mentions and data
        # and updating the nodes that contain
        # a list of footnotes
        footnotes = self.footnotes_manager.process_footnotes()

        # This processes all references stored in
        # the manager merging mentions and data
        # and updating the nodes that contain
        # a list of references
        references = self.references_manager.process_references()

        # Process ToC
        toc = self.toc_manager.process_toc()

        custom_filters = {}

        for name, func in (
            self.environment.getvar("mau.parser.custom_filters", Environment())
            .asdict()
            .items()
        ):
            custom_filters[name] = func(self.nodes)

        wrapper_node_class = self.environment.getvar(
            "mau.parser.content_wrapper", ContainerNode
        )

        self.output.update(
            {
                "content": wrapper_node_class(self.nodes),
                "toc": toc,
                "references": references,
                "footnotes": footnotes,
                "custom_filters": custom_filters,
            }
        )
