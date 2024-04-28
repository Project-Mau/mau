# pylint: disable=too-many-lines

from mau.environment.environment import Environment
from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.lexers.main_lexer import MainLexer
from mau.lexers.main_lexer import TokenTypes as MLTokenTypes
from mau.nodes.block import BlockGroupNode, BlockNode
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import RawNode, SentenceNode
from mau.nodes.lists import ListItemNode, ListNode
from mau.nodes.page import ContainerNode, HorizontalRuleNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.attributes import AttributesManager
from mau.parsers.base_parser import BaseParser
from mau.parsers.footnotes import FootnotesManager
from mau.parsers.internal_links import InternalLinksManager
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.text_parser import TextParser
from mau.parsers.toc import TocManager, header_anchor
from mau.tokens.tokens import Token


# The MainParser is in charge of parsing
# the whole input, calling other parsers
# to manage single paragraphs or other
# things like variables.
class MainParser(BaseParser):
    lexer_class = MainLexer

    def __init__(self, environment, parent_node=None, parent_position=None):
        super().__init__(environment, parent_node, parent_position)

        self.internal_links_manager = InternalLinksManager(self)
        self.footnotes_manager = FootnotesManager(self)
        self.toc_manager = TocManager(self)
        self.attributes_manager = AttributesManager(self)

        # These are the default block aliases
        # If subtype is not set it will be the alias itself.
        self.block_aliases = {
            "source": {
                "subtype": None,
                "mandatory_args": ["language"],
                "defaults": {"engine": "source", "language": "text"},
            },
            "footnote": {
                "subtype": None,
                "mandatory_args": ["name"],
                "defaults": {"engine": "footnote"},
            },
            "admonition": {
                "mandatory_args": ["class", "icon"],
            },
        }

        # Iterate through block definitions passed as variables
        self.block_aliases.update(
            self.environment.getvar(
                "mau.parser.block_definitions", Environment()
            ).asdict()
        )

        # This is a buffer for a block title
        self.title = (None, None)

        # This is a buffer for a control
        self.control = (None, None, None)

        # This is the function used to create the header
        # anchors.
        self.header_anchor = self.environment.getvar(
            "mau.parser.header_anchor_function", header_anchor
        )

        # The last index in the latest ordered list,
        # used to calculate the beginning value of them
        # next one when start=auto
        self.latest_ordered_list_index = 0

        # This is the dictionary of block groups
        # defineed in the document
        self.grouped_blocks = {}

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
            self._process_control,
            self._process_arguments,
            self._process_header,
            self._process_block,
            self._process_content,
            self._process_list,
            self._process_paragraph,
        ]

    def _push_title(self, text, context):
        # When we parse a title we can store it here
        # so that it is available to the next block
        # that will use it.
        self.title = (text, context)

    def _pop_title(self, node):
        # This return the title and resets the
        # cached one, so no other block will
        # use it.
        text, context = self.title
        self._reset_title()

        if text is None:
            return None

        text_parser = TextParser.analyse(
            text,
            context,
            self.environment,
            parent_node=node,
            parent_position="title",
        )

        return SentenceNode(
            parent=node,
            parent_position="title",
            children=text_parser.nodes,
        )

    def _reset_title(self):
        self.title = (None, None)

    def _push_control(self, operator, statement, context):
        self.control = (operator, statement, context)

    def _pop_control(self):
        # This return the title and resets the
        # cached one, so no other block will
        # use it.
        operator, statement, context = self.control
        self._reset_control()

        if operator is None:
            return True

        if operator != "if":
            self._error(f"Control operator '{operator}' is not supported")

        try:
            variable, test = statement.split(":", 1)
        except ValueError:
            self._error(f"Statement '{statement}' is not in the form variable:test")

        variable_value = self.environment.getvar(variable, None)

        if variable_value is None:
            self._error(f"Variable '{variable}' has not been defined")

        if test.startswith("="):
            value = test[1:]
            return variable_value == value

        if test.startswith("!="):
            value = test[2:]

            return variable_value != value

        if test.startswith("&"):
            value = test[1:]

            if value not in ["true", "false"]:
                self._error(f"Boolean value '{value}' is invalid")

            # pylint: disable=simplifiable-if-expression
            value = True if value == "true" else False

            return variable_value and value

        self._error(f"Test '{test}' is not supported")

    def _reset_control(self):
        self.control = (None, None, None)

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

    def _parse_text_content(
        self, text, parent_node=None, parent_position=None, context=None
    ):
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
        text_parser = TextParser.analyse(
            text,
            current_context,
            self.environment,
            parent_node=parent_node,
            parent_position=parent_position,
        )

        # Extract the footnote mentions
        # found in this piece of text
        self.footnotes_manager.update_mentions(text_parser.footnotes)

        # Extract the internal links
        # found in this piece of text
        self.internal_links_manager.update_links(text_parser.links)

        return text_parser.nodes

    def _process_eol(self):
        # This simply parses the end of line.

        self._get_token(BLTokenTypes.EOL)

        return True

    def _process_horizontal_rule(self):
        # The horizontal rule ---

        self._get_token(MLTokenTypes.HORIZONTAL_RULE)

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        self._save(
            HorizontalRuleNode(
                subtype=subtype,
                args=args,
                kwargs=kwargs,
                tags=tags,
            )
        )

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
        variable_token = self._get_token(BLTokenTypes.TEXT)
        self._get_token(BLTokenTypes.LITERAL, ":")

        context = variable_token.context
        variable_name = variable_token.value

        # Get the optional value
        value = self._collect_join([Token(BLTokenTypes.EOL)])

        # If the name starts with "+" it's a true flag
        # If the name starts with "-" it's a false flag
        if variable_name.startswith("+"):
            variable_name = variable_name[1:]
            value = True
        elif variable_name.startswith("-"):
            variable_name = variable_name[1:]
            value = False
        else:
            preprocess_parser = PreprocessVariablesParser.analyse(
                value,
                context,
                self.environment,
            )
            value = preprocess_parser.nodes[0].value

        self.environment.setvar(variable_name, value)

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
            arguments = self._get_token(BLTokenTypes.TEXT)

            arguments_parser = ArgumentsParser.analyse(
                arguments.value, arguments.context, self.environment
            )

            (
                command_args,
                command_kwargs,
                _,
                command_subtype,
            ) = arguments_parser.process_arguments()

        if name == "defblock":
            if len(command_args) < 1:
                self._error("Block definitions require at least the alias")

            alias = command_args.pop(0)

            self.block_aliases[alias] = {
                "subtype": command_subtype,
                "mandatory_args": command_args,
                "defaults": command_kwargs,
            }

        elif name == "toc":
            self.toc_manager.create_toc_node(subtype, args, kwargs, tags)

        elif name == "footnotes":
            # Create a footnotes node
            self.footnotes_manager.create_node(subtype, args, kwargs, tags)

        elif name == "blockgroup":
            command_args, command_kwargs = self._set_names_and_defaults(
                command_args,
                command_kwargs,
                ["group"],
            )

            group_name = command_kwargs.pop("group")

            try:
                group = self.grouped_blocks.pop(group_name)
            except KeyError:
                self._error(
                    (
                        f"The group of blocks {group_name} doesn't exist. "
                        "No blocks belong to that group."
                    )
                )

            node = BlockGroupNode(
                group_name=group_name,
                group=group,
                subtype=subtype,
                args=args,
                kwargs=kwargs,
                tags=tags,
            )

            for position, block in group.items():
                block.parent = node
                block.parent_position = position

            self.save(node)

        return True

    def _process_title(self):
        # Parse a title in the form
        #
        # . This is a title
        # or
        # .This is a title

        # Parse the mandatory dot
        dot = self._get_token(MLTokenTypes.TITLE, ".")

        # Parse the optional white spaces
        with self:
            self._get_token(BLTokenTypes.WHITESPACE)

        # Get the text of the title
        text = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.EOL)

        self._push_title(text, dot.context)

        return True

    def _process_control(self):
        # Parse a control statement in the form
        #
        # @operator:control_statement

        # Parse the mandatory @
        at = self._get_token(MLTokenTypes.CONTROL, "@")

        # Get the operator
        operator = self._get_token(BLTokenTypes.TEXT).value

        # Discard the :
        self._get_token(BLTokenTypes.LITERAL, ":")

        # Get the statement
        statement = self._get_token(BLTokenTypes.TEXT).value

        self._get_token(BLTokenTypes.EOL)

        self._push_control(operator, statement, at.context)

        return True

    def _process_arguments(self):
        # Parse arguments in the form
        # [unnamed1, unnamed2, ..., named1=value1, name2=value2, ...]

        self._get_token(MLTokenTypes.ARGUMENTS, "[")
        text_token = self._get_token(BLTokenTypes.TEXT)
        self._get_token(BLTokenTypes.LITERAL, "]")

        preprocess_parser = PreprocessVariablesParser.analyse(
            text_token.value,
            text_token.context,
            self.environment,
        )
        text = preprocess_parser.nodes[0].value

        # Parse the text
        arguments_parser = ArgumentsParser.analyse(
            text, text_token.context, self.environment
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
        text_token = self._get_token(BLTokenTypes.TEXT)
        level = len(header)

        preprocess_parser = PreprocessVariablesParser.analyse(
            text_token.value,
            text_token.context,
            self.environment,
        )
        text = preprocess_parser.nodes[0].value

        # Check the control
        if self._pop_control() is False:
            return True

        # Consume the parser arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Create the anchor
        anchor = kwargs.pop("anchor", self.header_anchor(text, level))

        node = HeaderNode(
            level=str(level),
            anchor=anchor,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        # Titles can contain Mau code
        text_parser = TextParser.analyse(
            text,
            text_token.context,
            self.environment,
            parent_node=node,
        )
        node.value = SentenceNode(
            parent=node,
            children=text_parser.nodes,
        )

        # If there is an id store the header
        # to be processed by internal links
        if "id" in node.kwargs:
            self.internal_links_manager.add_header(node.kwargs["id"], node)

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
        block = BlockNode(children=content, secondary_children=secondary_content)

        block.title = self._pop_title(block)

        # Consume the arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Check the control
        if self._pop_control() is False:
            return True

        # If the subtype is an alias process it
        alias = self.block_aliases.get(subtype, {})
        block.subtype = alias.get("subtype", subtype)
        block_names = alias.get("mandatory_args", [])
        block_defaults = alias.get("defaults", {})

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

        # Extract the preprocessor
        block.preprocessor = kwargs.pop("preprocessor", "none")

        # Extract the engine
        block.engine = kwargs.pop("engine", None)

        block.args = args
        block.kwargs = kwargs
        block.tags = tags

        if block.engine is None:
            self._parse_default_engine(block)
        elif block.engine == "mau":
            self._parse_mau_engine(block)
        elif block.engine == "source":
            self._parse_source_engine(block)
        elif block.engine == "footnote":
            self._parse_footnote_engine(block)
        elif block.engine == "raw":
            self._parse_raw_engine(block)
        elif block.engine == "group":
            self._parse_group_engine(block)
        else:
            self._error(f"Engine {block.engine} is not available")

        return True

    def _parse_block_content(self, block):
        current_context = self._current_token.context

        content_parser = MainParser.analyse(
            "\n".join(block.children),
            current_context,
            Environment(),
            parent_node=block,
            parent_position="primary",
        )
        content_parser.finalise()

        secondary_content_parser = MainParser.analyse(
            "\n".join(block.secondary_children),
            current_context,
            Environment(),
            parent_node=block,
            parent_position="secondary",
        )
        secondary_content_parser.finalise()

        block.children = content_parser.nodes
        block.secondary_children = secondary_content_parser.nodes

    def _parse_block_content_update(self, block):
        current_context = self._current_token.context

        content_parser = MainParser.analyse(
            "\n".join(block.children),
            current_context,
            self.environment,
            parent_node=block,
            parent_position="primary",
        )

        secondary_content_parser = MainParser.analyse(
            "\n".join(block.secondary_children),
            current_context,
            self.environment,
            parent_node=block,
            parent_position="secondary",
        )

        block.children = content_parser.nodes
        block.secondary_children = secondary_content_parser.nodes

        # The footnote mentions and definitions
        # found in this block are part of the
        # main document. Import them.
        self.footnotes_manager.update(content_parser.footnotes_manager)

        # The internal links and headers
        # found in this block are part of the
        # main document. Import them.
        self.internal_links_manager.update(content_parser.internal_links_manager)

        self.toc_manager.update(content_parser.toc_manager)

    def _parse_mau_engine(self, block):
        self._parse_block_content(block)
        self._save(block)

    def _parse_default_engine(self, block):
        self._parse_block_content_update(block)
        self._save(block)

    def _parse_group_engine(self, block):
        block.args, block.kwargs = self._set_names_and_defaults(
            block.args,
            block.kwargs,
            ["group", "position"],
        )

        group_name = block.kwargs.pop("group")
        position = block.kwargs.pop("position")

        group = self.grouped_blocks.setdefault(group_name, {})

        if position in group:
            self._error(
                f"Block with position {position} already defined in group {group_name}"
            )

        group[position] = block

        self._parse_block_content_update(block)

    def _parse_footnote_engine(self, block):
        # The current block contains footnote data.
        # Extract the content and store it in
        # the footnotes manager.
        name = block.kwargs.pop("name")

        content_parser = MainParser.analyse(
            "\n".join(block.children),
            self._current_token.context,
            self.environment,
            parent_node=block,
        )

        self.footnotes_manager.add_data(name, content_parser.nodes)

    def _parse_raw_engine(self, block):
        # Engine "raw" doesn't process the content,
        # so we just pass it untouched in the form of
        # a RawNode per line.
        block.children = [RawNode(line) for line in block.children]
        block.secondary_children = [RawNode(line) for line in block.secondary_children]

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
        # is one of the languages supported by that tool.

        # Get the delimiter for callouts (":" by default)
        delimiter = block.kwargs.pop("callouts", ":")

        # A list that contains callout markers in
        # the form (linenum,name)
        callout_markers = []

        # Get the marker for highlighted lines ("@" by default)
        highlight_marker = block.kwargs.pop("highlight", "@")

        # A list of highlighted lines
        highlighted_lines = []

        # Get the language
        language = block.kwargs.pop("language")

        # Source blocks preserve anything is inside

        # This is a list of all lines that might contain
        # a callout. They will be further processed
        # later to be sure.
        lines_with_callouts = [
            (linenum, line)
            for linenum, line in enumerate(block.children)
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

            block.children[linenum] = line

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
        for line in block.secondary_children:
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
        for line in block.children:
            if line.startswith(r"\::#"):
                line = line[1:]

            textlines.append(RawNode(line))

        node = SourceNode(
            code=textlines,
            language=language,
            callouts=callout_contents,
            highlights=highlighted_lines,
            markers=callout_markers,
            title=block.title,
            subtype=block.subtype,
            args=block.args,
            kwargs=block.kwargs,
            tags=block.tags,
        )

        self._save(node)

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

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        uris = self._get_token(BLTokenTypes.TEXT)

        with self:
            arguments_parser = ArgumentsParser.analyse(
                uris.value, uris.context, self.environment
            )

            uris, _, _, _ = arguments_parser.process_arguments()

        # Check the control
        if self._pop_control() is False:
            return True

        if content_type == "image":
            return self._parse_content_image(uris, subtype, args, kwargs, tags)

        return self._parse_standard_content(
            content_type, uris, subtype, args, kwargs, tags
        )

    def _parse_content_image(self, uris, subtype, args, kwargs, tags):
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

        uri = uris[0]
        alt_text = kwargs.pop("alt_text")
        classes = kwargs.pop("classes")

        if classes:
            classes = classes.split(",")

        node = ContentImageNode(
            uri=uri,
            alt_text=alt_text,
            classes=classes,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        node.title = self._pop_title(node)
        self._save(node)

        return True

    def _parse_standard_content(self, content_type, uris, subtype, args, kwargs, tags):
        # This is the fallback for an unknown content type

        node = ContentNode(
            content_type=content_type,
            uris=uris,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        node.title = self._pop_title(node)
        self._save(node)

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
        ordered = header.value[0] == "#"

        args, kwargs, tags, subtype = self.attributes_manager.pop()

        # Parse all the following items
        nodes = self._process_list_nodes()

        if (start := kwargs.pop("start", 1)) == "auto":
            start = self.latest_ordered_list_index
            self.latest_ordered_list_index += len(nodes)
        else:
            start = int(start)
            self.latest_ordered_list_index = len(nodes) + start

        self._save(
            ListNode(
                ordered=ordered,
                main_node=True,
                start=start,
                children=nodes,
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
        content = self._parse_text_content(
            text,
            parent_node=self.parent_node,
            parent_position=self.parent_position,
            context=context,
        )

        # Compute the level of the item
        level = len(header)

        nodes = []
        nodes.append(ListItemNode(level=str(level), children=content))

        while self._peek_token() not in [
            Token(BLTokenTypes.EOF),
            Token(BLTokenTypes.EOL),
        ]:
            # This are the nodes inside the last element added to the list
            # which is used to append potential nested elements
            last_element_nodes = nodes[-1].children

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
                content = self._parse_text_content(
                    text,
                    parent_node=self.parent_node,
                    parent_position=self.parent_position,
                    context=context,
                )

                level = len(header)

                nodes.append(ListItemNode(level=str(level), children=content))
            elif len(self._peek_token().value) > level:
                # The new item is on a deeper level

                # Treat the new line as a new list
                numbered = self._peek_token().value[0] == "#"
                subnodes = self._process_list_nodes()

                last_element_nodes.append(ListNode(ordered=numbered, children=subnodes))
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

        # Check the control
        if self._pop_control() is False:
            return True

        text = " ".join(lines)

        # Consume the arguments
        args, kwargs, tags, subtype = self.attributes_manager.pop()

        node = ParagraphNode(
            parent=self.parent_node,
            parent_position=self.parent_position,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        node.title = self._pop_title(node)

        node.children = self._parse_text_content(
            text, parent_node=node, context=context
        )

        self._save(node)

        return True

    def finalise(self):
        super().finalise()

        # This processes all footnotes stored in
        # the manager merging mentions and data
        # and updating the nodes that contain
        # a list of footnotes
        self.footnotes_manager.process_footnotes()

        # This processes all links stored in
        # the manager linking them to the
        # correct headers
        self.internal_links_manager.process_links()

        # Process ToC
        toc = self.toc_manager.process_toc()

        # The content wrappers are cloned to avoid
        # storing the whole parsed document in the
        # environment.
        content_wrapper = self.environment.getvar(
            "mau.parser.content_wrapper", ContainerNode()
        ).clone()
        content_wrapper.children = self.nodes

        toc_wrapper = self.environment.getvar(
            "mau.parser.toc_wrapper", ContainerNode()
        ).clone()
        toc_wrapper.add_children([toc])

        self.output.update(
            {
                "content": content_wrapper,
                "toc": toc_wrapper,
            }
        )
