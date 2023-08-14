# pylint: disable=too-many-lines

import hashlib
import re

from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.lexers.main_lexer import MainLexer
from mau.lexers.main_lexer import TokenTypes as MLTokenTypes
from mau.nodes.footnotes import CommandFootnotesNode, FootnotesEntryNode
from mau.nodes.inline import ListItemNode, TextNode
from mau.nodes.page import (
    BlockNode,
    CommandTocNode,
    ContentImageNode,
    ContentNode,
    HeaderNode,
    HorizontalRuleNode,
    ListNode,
    ParagraphNode,
)
from mau.nodes.references import CommandReferencesNode, ReferencesEntryNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.base_parser import BaseParser
from mau.parsers.environment import Environment
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.text_parser import TextParser
from mau.tokens.tokens import Token


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

    hashed_value = hashlib.md5(f"{level} {text}".encode("utf-8")).hexdigest()[:4]

    return f"{sanitised_text}-{hashed_value}"


def footnote_anchor(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()[:8]


def reference_anchor(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()[:8]


# The MainParser is in charge of parsing
# the whole input, calling other parsers
# to manage single paragraphs or other
# things like variables.
class MainParser(BaseParser):
    lexer_class = MainLexer

    def __init__(
        self, tokens, environment=None, references=None, reference_entries=None
    ):
        super().__init__(tokens)

        self.environment = environment or Environment()

        self.headers = []

        # This dictionary containes the footnotes created
        # in the text through a macro.
        self.footnotes = {}

        # This dictionary contains the content of each
        # footnote created through blocks.
        # This is a helper dictionary that will be merged
        # with self.footnotes once the parsing is completed.
        self.footnotes_data = {}

        # This list contains all the footnote entries
        # that will be shown by a footnotes command.
        self.footnote_entries = []

        # This dictionary containes the references created
        # in the text through a macro.
        self.reference_mentions = {}

        # This dictionary contains the content of each
        # reference created through blocks.
        self.reference_data = {}

        # This list contains all the references contained
        # in this parser in the form
        # {content_type:[references]}.
        self.references = references if references is not None else {}

        # This list contains all the reference entries
        # that will be shown by a references command in the form
        # {content_type:[references]}.
        # This is a copy of self.references that however
        # contains ReferencesEntryNode nodes.
        self.reference_entries = (
            reference_entries if reference_entries is not None else {}
        )

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
        self.block_aliases["source"] = "default"
        self.block_defaults["source"] = {"engine": "source", "language": "text"}
        self.block_names["source"] = ["language"]

        self.block_aliases["footnote"] = "default"
        self.block_defaults["footnote"] = {"engine": "footnote"}
        self.block_names["footnote"] = ["name"]

        self.block_aliases["reference"] = "default"
        self.block_defaults["reference"] = {"engine": "reference"}
        self.block_names["reference"] = ["type", "name"]

        self.block_aliases["admonition"] = "admonition"
        self.block_names["admonition"] = ["class", "icon", "label"]

        # Iterate through block definitions passed as variables
        # for alias, block_definition in (
        #     self.variables["mau"].get("block_definitions", {}).items()
        # ):
        #     try:
        #         blocktype = block_definition["blocktype"]
        #         self.block_aliases[alias] = blocktype
        #     except KeyError:
        #         raise ConfigurationError(
        #             f"Block definition '{alias}' is missing key 'blocktype'"
        #         )

        #     try:
        #         self.block_defaults[blocktype] = block_definition["kwargs"]
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
            "mau.header_anchor_function", header_anchor
        )

        # A temporary space to store parsed arguments
        # The tuple represents (args, kwargs, tags)
        self.arguments = ([], {}, [])

    def create_footnotes(self):
        for num, footnote in enumerate(self.footnotes.values(), start=1):
            footnote.number = num

        for key, footnote in self.footnotes.items():
            data = self.footnotes_data[key]
            footnote.content = data["content"]
            anchor = footnote_anchor(footnote.content)

            footnote.reference_anchor = f"fr-{anchor}-{footnote.number}"
            footnote.content_anchor = f"fd-{anchor}-{footnote.number}"

            self.footnote_entries.append(
                FootnotesEntryNode(
                    content=footnote.content,
                    number=footnote.number,
                    reference_anchor=footnote.reference_anchor,
                    content_anchor=footnote.content_anchor,
                )
            )

    def process_references(self):
        # Example of stored content
        # self.references = {
        #  (type1, name1) = node1
        #  (type1, name2) = node2
        #  (type2, name3) = node3
        # }
        #
        # self.reference_data = {
        #  (type1, name1) = content
        #  (type1, name2) = content
        #  (type2, name3) = content
        # }

        content_types = {i[0] for i in self.reference_data}
        content_types_num = {}

        for content_type in content_types:
            content_types_num[content_type] = 1

        for key, value in self.reference_mentions.items():
            data = self.reference_data[key]
            content_type = value.content_type

            value.content = data["content"]
            value.title = data["title"]
            anchor = reference_anchor(value.content)

            value.number = content_types_num[content_type]
            content_types_num[content_type] += 1

            value.reference_anchor = f"ref-{content_type}-{value.number}-{anchor}"
            value.content_anchor = f"cnt-{content_type}-{value.number}-{anchor}"

            self.references[key] = value
            self.reference_entries[key] = ReferencesEntryNode(
                content_type=value.content_type,
                name=value.name,
                category=value.category,
                content=value.content,
                number=value.number,
                title=value.title,
                reference_anchor=value.reference_anchor,
                content_anchor=value.content_anchor,
            )

    def _pop_arguments(self):
        # This return the arguments and resets the
        # cached ones.
        args, kwargs, tags = self.arguments
        self.arguments = ([], {}, [])

        return args, kwargs, tags

    def _push_arguments(self, args, kwargs, tags):
        self.arguments = (args, kwargs, tags)

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
            self._process_include_content,
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

    def _parse_text_content(self, text):
        # Parse a piece of text using the TextParser.

        current_context = self._current_token.context

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
        )

        # A text parser returns a single sentence node
        result = text_parser.nodes[0]

        # Store the footnotes
        self.footnotes.update(text_parser.footnotes)

        # The format of the stored content dictionary is
        # {(content_type,name): node}
        self.reference_mentions.update(text_parser.references)

        return result

    def _process_eol(self):
        # This simply parses the end of line.

        self._get_token(BLTokenTypes.EOL)

        return True

    def _process_horizontal_rule(self):
        # The horizontal rule ---

        self._get_token(MLTokenTypes.HORIZONTAL_RULE)

        args, kwargs, tags = self._pop_arguments()

        self._save(HorizontalRuleNode(args, kwargs, tags))

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
        self._force_token(MLTokenTypes.MULTILINE_COMMENT)

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

        args = []
        kwargs = {}
        tags = []

        # Commands can have arguments
        arguments = ""
        with self:
            arguments = self._get_token(BLTokenTypes.TEXT).value

            current_context = self._current_token.context

            arguments_parser = ArgumentsParser.analyse(
                arguments,
                current_context,
            )

            args, kwargs, tags = arguments_parser.process_arguments()

        if name == "defblock":
            # Block definitions must have at least 2 arguments,
            # the alias and the block type.
            if len(args) < 2:
                self._error(
                    "Block definitions require at least two unnamed arguments: ALIAS and BLOCKTYPE"
                )

            block_alias = args.pop(0)
            block_type = args.pop(0)

            self.block_aliases[block_alias] = block_type
            self.block_defaults[block_alias] = kwargs
            self.block_names[block_alias] = args

        elif name == "toc":
            self._save(
                CommandTocNode(
                    entries=self.headers, args=args, kwargs=kwargs, tags=tags
                )
            )

        elif name == "footnotes":
            self._save(
                CommandFootnotesNode(
                    entries=self.footnote_entries, args=args, kwargs=kwargs, tags=tags
                )
            )

        elif name == "references":
            # Assign names
            args, kwargs = self._set_names_and_defaults(
                args,
                kwargs,
                ["content_type", "category", "name"],
                {"category": None, "name": None},
            )

            content_type = kwargs.pop("content_type")
            category = kwargs.pop("category")
            name = kwargs.pop("name")

            self._save(
                CommandReferencesNode(
                    entries=self.reference_entries,
                    content_type=content_type,
                    name=name,
                    category=category,
                    args=args,
                    kwargs=kwargs,
                    tags=tags,
                )
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
        text_parser = TextParser.analyse(text, current_context)

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
            environment=self.environment,
        )
        text = preprocess_parser.nodes[0].value

        # Parse the text
        arguments_parser = ArgumentsParser.analyse(
            text,
            current_context,
        )

        args, kwargs, tags = arguments_parser.process_arguments()
        self._push_arguments(args, kwargs, tags)

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

        # Generate the anchor and append it to the TOC
        anchor = self.header_anchor(text, level)

        # Consume the arguments
        args, kwargs, tags = self._pop_arguments()

        # Generate the header node
        header_node = HeaderNode(
            value=text,
            level=str(level),
            anchor=anchor,
            args=args,
            tags=tags,
            kwargs=kwargs,
        )

        self.headers.append(header_node)

        self._save(header_node)

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

        # Consume the title
        title = self._pop_title()

        # Consume the arguments
        args, kwargs, _ = self._pop_arguments()

        # The first unnamed argument is the block type
        try:
            blocktype = args.pop(0)
        except IndexError:
            blocktype = "default"

        # If there is a block alias for blocktype replace it
        # otherwise use the blocktype we already have

        # Retrieve the block names and defaults for the
        # specific type of block

        block_names = self.block_names.get(blocktype, [])
        block_defaults = self.block_defaults.get(blocktype, {})

        # Now replace the alias with the true block type
        blocktype = self.block_aliases.get(blocktype, blocktype)

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
        preprocessor = kwargs.pop("preprocessor", "none")

        # Extract the engine
        engine = kwargs.pop("engine", "default")

        if engine == "source":
            # Engine "source" extracts the content (source code),
            # the callouts, and the highlights.
            # The default language is "text".

            self._parse_source_engine(
                blocktype, content, secondary_content, title, kwargs
            )

            return True

        if engine == "footnote":
            name = kwargs.pop("name")

            current_context = self._current_token.context

            environment = self.environment

            content_parser = MainParser.analyse(
                "\n".join(content),
                current_context,
                environment=environment,
                references=self.references,
                reference_entries=self.reference_entries,
            )

            content = content_parser.nodes

            self.footnotes_data[name] = {
                "content": content,
            }

            return True

        if engine == "reference":
            content_type = kwargs["type"]
            name = kwargs["name"]

            current_context = self._current_token.context

            environment = self.environment

            content_parser = MainParser.analyse(
                "\n".join(content),
                current_context,
                environment=environment,
                references=self.references,
                reference_entries=self.reference_entries,
            )

            content = content_parser.nodes

            self.reference_data[(content_type, name)] = {
                "content": content,
                "title": title,
            }

            return True

        # Create the node parameters according to the engine
        if engine == "raw":
            # Engine "raw" doesn't process the content,
            # so we just pass it untouched in the form of
            # a TextNode per line.
            content = [TextNode(line) for line in content]
            secondary_content = [TextNode(line) for line in secondary_content]
        elif engine in ["default", "mau"]:
            # Both engines parse content and secondary content
            # using a new parser but the default one should merge
            # headers and footnotes into the current one.

            current_context = self._current_token.context

            if engine == "default":
                environment = self.environment
            else:
                environment = Environment()

            content_parser = MainParser.analyse(
                "\n".join(content),
                current_context,
                environment=environment,
                references=self.references,
                reference_entries=self.reference_entries,
            )

            secondary_content_parser = MainParser.analyse(
                "\n".join(secondary_content),
                current_context,
                environment=environment,
            )

            content = content_parser.nodes
            secondary_content = secondary_content_parser.nodes

            if engine == "default":
                self.footnotes.update(content_parser.footnotes)
                self.footnotes_data.update(content_parser.footnotes_data)
                self.headers.extend(content_parser.headers)
                self.reference_mentions.update(content_parser.reference_mentions)
                self.reference_data.update(content_parser.reference_data)
            else:
                content_parser.create_footnotes()
                content_parser.process_references()
        else:
            self._error(f"Engine {engine} is not available")

        self._save(
            BlockNode(
                blocktype=blocktype,
                content=content,
                secondary_content=secondary_content,
                classes=classes,
                title=title,
                engine=engine,
                preprocessor=preprocessor,
                args=args,
                kwargs=kwargs,
            )
        )

        return True

    def _parse_source_engine(
        self, blocktype, content, secondary_content, title, kwargs
    ):  # pylint: disable=too-many-locals
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

        # A list that contains callout markers in
        # the form (linenum,name)
        callout_markers = []

        # Get the marker for highlighted lines ("@" by default)
        highlight_marker = kwargs.pop("highlight", "@")

        # A list of highlighted lines
        highlighted_lines = []

        # Source blocks preserve anything is inside

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
                callout_markers.append(CalloutNode(linenum, callout_name))

        # A list of CalloutEntryNode objects that contain the
        # text for each marker
        callout_contents = []

        # If there was secondary content it should be formatted
        # with callout names followed by colon and the
        # callout text.
        for line in secondary_content:
            if ":" not in line:
                self._error(
                    (
                        "Callout description should be written"
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
        for line in content:
            if line.startswith(r"\::#"):
                line = line[1:]

            textlines.append(TextNode(line))

        self._save(
            SourceNode(
                blocktype=blocktype,
                code=textlines,
                language=kwargs["language"],
                callouts=callout_contents,
                highlights=highlighted_lines,
                markers=callout_markers,
                title=title,
            )
        )

    def _process_include_content(self):
        # Parse include content in the form
        #
        # << content_type:arguments

        # Get the mandatory "<<"
        self._get_token(MLTokenTypes.INCLUDE)

        with self:
            self._get_token(BLTokenTypes.WHITESPACE)

        # Get the content type
        content_type = self._get_token(BLTokenTypes.TEXT).value
        self._get_token(BLTokenTypes.LITERAL, ":")

        title = self._pop_title()

        args = []
        kwargs = {}
        tags = []

        # Commands can have arguments
        arguments = ""
        with self:
            arguments = self._get_token(BLTokenTypes.TEXT).value

            current_context = self._current_token.context

            arguments_parser = ArgumentsParser.analyse(
                arguments,
                current_context,
            )

            args, kwargs, tags = arguments_parser.process_arguments()

        if content_type == "image":
            return self._parse_content_image(title, args, kwargs, tags)

        return self._parse_standard_content(content_type, title, args, kwargs, tags)

    def _parse_content_image(self, title, args, kwargs, tags):
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
            ["uri", "alt_text", "classes"],
            {"alt_text": None, "classes": None},
        )

        uri = kwargs.pop("uri")
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
                tags=tags,
            )
        )

        return True

    def _parse_standard_content(self, content_type, title, args, kwargs, tags):
        # This is the fallback for an unknown content type

        self._save(
            ContentNode(
                content_type=content_type,
                title=title,
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

        args, kwargs, tags = self._pop_arguments()

        # Parse all the following items
        nodes = self._process_list_nodes()

        self._save(
            ListNode(
                numbered, nodes, main_node=True, args=args, kwargs=kwargs, tags=tags
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

        # Collect and parse the text of the item
        text = self._collect_text_content()
        content = self._parse_text_content(text)

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

                # Collect and parse the text of the item
                text = self._collect_text_content()
                content = self._parse_text_content(text)

                nodes.append(ListItemNode(str(len(header)), content))
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
        sentence = self._parse_text_content(text)

        # Consume the arguments
        args, kwargs, tags = self._pop_arguments()

        self._save(ParagraphNode(sentence, args=args, kwargs=kwargs, tags=tags))

        return True
