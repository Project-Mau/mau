import itertools
import logging

from mau.environment.environment import Environment
from mau.lexers.text_lexer import TextLexer
from mau.message import BaseMessageHandler, MauException
from mau.nodes.inline import (
    StyleNode,
    TextNode,
    VerbatimNode,
    WordNode,
)
from mau.nodes.macro import (
    MacroClassNode,
    MacroFootnoteNode,
    MacroHeaderNode,
    MacroImageNode,
    MacroLinkNode,
    MacroNode,
    MacroRawNode,
    MacroUnicodeNode,
)
from mau.nodes.node import Node, NodeInfo
from mau.parsers.arguments_parser import (
    ArgumentsParser,
    process_arguments,
)
from mau.parsers.base_parser import BaseParser, create_parser_exception
from mau.parsers.buffers.control_buffer import Control
from mau.parsers.condition_parser import ConditionParser
from mau.text_buffer import Context
from mau.token import EOF, EOL, Token, TokenType

logger = logging.getLogger(__name__)

# This is a simple map to keep track of the official
# name of styles introduced by special characters.
MAP_STYLES = {"_": "underscore", "*": "star", "^": "caret", "~": "tilde"}


# The TextParser is a recursive parser.
# The parsing always starts with parse_sentence
# and from there all components of the text are explored.
class TextParser(BaseParser):
    lexer_class = TextLexer

    def __init__(
        self,
        tokens: list[Token],
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
        parent_node=None,
    ):
        super().__init__(tokens, message_handler, environment, parent_node)

        # These are the footnote macros found in this piece of text.
        self.footnote_macros: list[MacroFootnoteNode] = []

        # These are the internal links found
        # in this piece of text.
        self.header_links: list[Node] = []

    def _collect_macro_args(self) -> Token:
        # A helper that reads macro arguments.
        # We already consumed the opening
        # round bracket.
        #
        # This is not a trivial task. Arguments
        # might contain a closing round bracket,
        # but if the argument is between double quotes
        # we ignore such brackets.

        all_args: list[Token] = []

        # Continue until you find a closing round bracket or EOF.
        while not (
            self.tm.peek_token_is(TokenType.LITERAL, ")")
            or self.tm.peek_token_is(TokenType.EOF)
        ):
            # If we find double quotes we need to blindly
            # collect everything until we meet the closing
            # double quotes or EOL.
            if self.tm.peek_token_is(TokenType.LITERAL, '"'):
                # Consume the double quotes.
                opening_quotes = self.tm.get_token(TokenType.LITERAL, '"')

                # Collect and join everything.
                # Stop at quotes or EOL.
                text_token = self.tm.collect_join(
                    stop_tokens=[
                        Token.generate(TokenType.LITERAL, '"'),
                        EOF,
                    ],
                )

                # As we stopped, the next token should be
                # double quotes. If not, we hit EOL and
                # macro arguments are not closed correctly.
                closing_quotes = self.tm.get_token(TokenType.LITERAL, '"')

                context = Context.merge_contexts(
                    opening_quotes.context, closing_quotes.context
                )

                token = Token(
                    TokenType.TEXT, value=f'"{text_token.value}"', context=context
                )
            else:
                # No double quotes, we can proceed,
                # until we find the closing round bracket
                # or a comma, which is the arguments separator.
                token = self.tm.collect_join(
                    stop_tokens=[
                        Token.generate(TokenType.LITERAL, ","),
                        Token.generate(TokenType.LITERAL, ")"),
                        EOF,
                    ],
                )

            # We can add the arguments we found to the
            # global list.
            all_args.append(token)

        # Arguments will be processed by the arguments
        # parser, for now just merge all of them into
        # a single piece of text.
        return Token.from_token_list(all_args)

    def _process_functions(self):
        # This is a recursive parser, so the list
        # of processing functions is pretty small.
        # We check for the EOL to skip empty
        # lines and then we move on with a sentence.
        return [self._process_sentence]

    def _process_sentence(self) -> bool:
        # A sentence node is a pure container for other
        # nodes. The parsing starts at _parse_sentence
        # and recursively explores the other functions.

        for node in self._parse_sentence():
            self._save(node)

        return True

    def _parse_sentence(self, stop_tokens=None) -> list[Node]:
        # Parse a sentence, which is made of multiple
        # elements identified by _parse_text, before
        # the EOF, the EOL, or a specific set of tokens
        # passed as argument.
        #
        # Custom stop tokens are useful for example when
        # parsing text like *text*. In this case we need
        # to stop parsing when we meet the second asterisk.

        # The list of nodes we find in this process.
        content = []

        # The set of tokens that trigger the end of
        # the process.
        stop_tokens = stop_tokens or set()

        # EOF and EOL always act as stoppers.
        stop_tokens = stop_tokens.union({EOF, EOL})

        # Try to parse some text.
        nodes = self._parse_text(stop_tokens)

        # Continue parsing text until it
        # stops returning nodes.
        while nodes:
            content.extend(nodes)
            nodes = self._parse_text(stop_tokens)

        # Group consecutive WordNode nodes into a single TextNode.
        # This scans the nodes we found and tries to collect consecutive
        # word nodes. We want to merge all of them into a single text node.

        # This iterator yields (key, group) where key is the grouping
        # key according to the lambda function. In this case it's
        # either True if the group contains word nodes or False otherwise.
        grouped_iter = itertools.groupby(content, lambda x: x.__class__ == WordNode)

        # The final list of nodes.
        nodes = []

        # Here, key is True if the group is made of word nodes,
        # which means that we need to merge them.
        for key, group in grouped_iter:
            # Read the whole group of
            # tokens into a list.
            group_nodes = list(group)

            if key:
                # Merge the values.
                word_nodes: list[WordNode] = group_nodes  # type: ignore[assignment]
                text = "".join([n.value for n in word_nodes])

                # Create the merged context.
                context = Context.merge_contexts(
                    group_nodes[0].info.context,
                    group_nodes[-1].info.context,
                )

                node = TextNode(
                    text,
                    parent=self.parent_node,
                    info=NodeInfo(
                        context=context,
                    ),
                )

                nodes.append(node)
            else:
                # This is a group of non-word nodes.
                # Just add them to the list.
                nodes.extend(group_nodes)

        return nodes

    def _parse_text(self, stop_tokens=None) -> list[Node]:
        # Parse multiple possible elements: escapes, classes,
        # macros, verbatim, styles, links, words.
        # This is the non-recursive part of the parser. It tries
        # each function until one of them returns a node
        # without raising an exception.
        # Each function is wrapped in a context manager to
        # make sure the index is restored to the original
        # value when a function raises an exception.

        stop_tokens = stop_tokens or set()

        if self.tm.peek_token() in stop_tokens:
            return []

        with self.tm:
            return self._parse_backslash_escaped()

        with self.tm:
            return self._parse_macro()

        with self.tm:
            return self._parse_verbatim()

        with self.tm:
            return self._parse_escaped()

        with self.tm:
            return self._parse_style()

        return self._parse_word()

    def _parse_backslash_escaped(self) -> list[Node]:
        # This tries to parse a backslash-escaped element.
        # Backslash escape allows Mau special characters
        # to be interpreted as simple text.
        # E.g "\_" or "\[text\]"

        # Drop the backslash.
        backslash = self.tm.get_token(TokenType.LITERAL, "\\")

        # Get the text.
        text = self.tm.get_token()

        # Merge the two contexts.
        context = Context.merge_contexts(backslash.context, text.context)

        # Create a word node with the next token.
        node = WordNode(
            text.value,
            parent=self.parent_node,
            info=NodeInfo(
                context=context,
            ),
        )

        return [node]

    def _parse_macro(self) -> list[Node]:
        # Parse a macro in the form
        # [name](arguments)

        # Extract the macro name getting rid
        # of the square brackets.
        # If the processing succeds, we need the
        # opening bracket to store the context
        # in the resulting node.
        opening_bracket = self.tm.get_token(TokenType.LITERAL, "[")
        macro_name_token = self.tm.get_token(TokenType.TEXT)
        self.tm.get_token(TokenType.LITERAL, "]")

        # If this is a macro, there should be an
        # opening round bracket that contains arguments.
        self.tm.get_token(TokenType.LITERAL, "(")

        # Get the macro arguments between round brackets.
        arguments_token = self._collect_macro_args()

        # If we get here, we stopped because of
        # closing brackets or EOL. If we can't find
        # the closing bracket the next token is EOL
        # and macro arguments are not closed correctly.
        closing_bracket = self.tm.get_token(TokenType.LITERAL, ")")

        arguments_parser = process_arguments(
            arguments_token, self.message_handler, self.environment
        )

        context = Context.merge_contexts(
            opening_bracket.context, closing_bracket.context
        )

        # Select the specific parsing function
        # according to the name of the macro.
        # All the parsing functons receive the arguments
        # parser instead of just the arguments as macro
        # arguments might contain Mau syntax and thus
        # might need to be parsed. This means that we
        # need to have the nodes and not just the text
        # values of all the arguments.

        if macro_name_token.value.startswith("if"):
            return self._parse_macro_control(
                macro_name_token, arguments_parser, context=context
            )

        if macro_name_token.value == "link":
            return self._parse_macro_link(arguments_parser, context=context)

        if macro_name_token.value == "header":
            return self._parse_macro_header_link(arguments_parser, context=context)

        if macro_name_token.value == "mailto":
            return self._parse_macro_mailto(arguments_parser, context=context)

        if macro_name_token.value == "image":
            return self._parse_macro_image(arguments_parser, context=context)

        if macro_name_token.value == "footnote":
            return self._parse_macro_footnote(arguments_parser, context=context)

        if macro_name_token.value == "class":
            return self._parse_macro_class(arguments_parser, context)

        if macro_name_token.value == "unicode":
            return self._parse_macro_unicode(arguments_parser, context)

        if macro_name_token.value == "raw":
            return self._parse_macro_raw(arguments_parser, context)

        # This is a generic macro, there is no
        # special code for it.
        node = MacroNode(
            name=macro_name_token.value,
            parent=self.parent_node,
            arguments=arguments_parser.arguments,
            info=NodeInfo(
                context=context,
            ),
        )

        return [node]

    def _parse_verbatim(self) -> list[Node]:
        # Parse verbatim text between backticks.
        # E.g. `text`.

        # Get the verbatim marker.
        opening_marker = self.tm.get_token(TokenType.LITERAL, "`")

        # Get all tokens from here to the next
        # verbatim marker or EOL.
        content = self.tm.collect_join(
            [Token.generate(TokenType.LITERAL, "`"), EOL],
        )

        # Remove the closing marker.
        closing_marker = self.tm.get_token(TokenType.LITERAL, "`")

        # Find the final context.
        context = Context.merge_contexts(opening_marker.context, closing_marker.context)

        node = VerbatimNode(
            content.value,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_escaped(self) -> list[Node]:
        # Parse text between dollar or percent signs.
        # This is useful when we need to escape multiple
        # character and we don't want to put a backslash
        # in front of all of them.
        # E.g. $escaped$ or %escaped%.

        # Get the escaped marker.
        opening_marker = self.tm.get_token(
            TokenType.LITERAL, value_check_function=lambda x: x in "$%"
        )

        # Get the content tokens before the
        # next escaped marker or EOL.
        content = self.tm.collect_join(
            [Token.generate(TokenType.LITERAL, opening_marker.value), EOL],
        )

        # Remove the closing marker
        closing_marker = self.tm.get_token(TokenType.LITERAL, opening_marker.value)

        # Find the final context.
        context = Context.merge_contexts(opening_marker.context, closing_marker.context)

        node = TextNode(
            content.value,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_style(self) -> list[Node]:
        # Parse text surrounded by style markers.

        # Get the style marker
        opening_marker = self.tm.get_token(
            TokenType.LITERAL,
            value_check_function=lambda x: x in MAP_STYLES,
        )

        # Get everything before the next marker
        content = self._parse_sentence(
            stop_tokens={Token.generate(TokenType.LITERAL, opening_marker.value)}
        )

        # Get the closing marker
        closing_marker = self.tm.get_token(TokenType.LITERAL, opening_marker.value)

        # Find the final context.
        context = Context.merge_contexts(opening_marker.context, closing_marker.context)

        node = StyleNode(
            MAP_STYLES[opening_marker.value],
            content=content,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        # Make the style node the parent
        # of each text node in it.
        for i in content:
            i.parent = node

        return [node]

    def _parse_word(self) -> list[Node]:
        # Parse a single word.

        token = self.tm.get_token()

        node = WordNode(
            token.value,
            parent=self.parent_node,
            info=NodeInfo(
                context=token.context,
            ),
        )

        return [node]

    def _parse_macro_link(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a link macro in the form [link](target, text).

        # Assign names to arguments.
        parser.set_names(["target", "text"])

        # Extract the target of the link.
        try:
            target = parser.named_argument_nodes["target"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory TARGET. Syntax: [link](TARGET, text).",
                context=context,
            ) from exc

        # Extract the text of the link if present.
        text = parser.named_argument_nodes.get("text")

        # If the text is present we need to parse it
        # as it might contain Mau syntax.
        # If the text is not present we use the
        # link as text.
        if text is not None:
            # Unpack the text initial position.
            start_line, start_column = text.info.context.start_position

            # Get the text source.
            source_filename = text.info.context.source

            # Parse the text.
            parser = self.lex_and_parse(
                text.value,
                self.message_handler,
                self.environment,
                start_line=start_line,
                start_column=start_column,
                source_filename=source_filename,
            )
            nodes = parser.nodes
        else:
            nodes = [
                TextNode(
                    target.value,
                    info=target.info,
                )
            ]

        node = MacroLinkNode(
            target.value,
            content=nodes,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_header_link(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a header link macro in the form [header](header_id, text).
        # This is similar to a macro link but the URI is an internal header ID.

        # Assign names to arguments.
        parser.set_names(["header_id", "text"])

        # Extract the header ID.
        try:
            header_id = parser.named_argument_nodes["header_id"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory ID. Syntax: [header](ID, TEXT).",
                context=context,
            ) from exc

        node = MacroHeaderNode(
            header_id.value,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        # Extract the text of the link if present.
        text = parser.named_argument_nodes.get("text")

        # If the text is present we need to parse it
        # as it might contain Mau syntax.
        # If the text is not present we skip this
        # step as the header link manager will
        # inject the header text.
        if text is not None:
            # Unpack the text initial position.
            start_line, start_column = text.info.context.start_position

            # Get the text source.
            source_filename = text.info.context.source

            # Parse the text
            parser = self.lex_and_parse(
                text.value,
                self.message_handler,
                self.environment,
                start_line=start_line,
                start_column=start_column,
                source_filename=source_filename,
            )
            node.content = parser.nodes

        self.header_links.append(node)

        return [node]

    def _parse_macro_mailto(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a mailto macro in the form [mailto](email, text).
        # This is similar to a macro link but the URI is a `mailto:`.

        # Assign names to arguments.
        parser.set_names(["email", "text"])

        # Extract the linked email and add the `mailto:` prefix.
        try:
            target = parser.named_argument_nodes["email"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory EMAIL. Syntax: [mailto](EMAIL, text).",
                context=context,
            ) from exc

        # Extract the text of the link if present.
        text = parser.named_argument_nodes.get("text")

        # If the text is present we need to parse it
        # as it might contain Mau syntax.
        # If the text is not present we use the
        # link as text.
        if text is not None:
            # Unpack the text initial position.
            start_line, start_column = text.info.context.start_position

            # Get the text source.
            source_filename = text.info.context.source

            # Parse the text
            parser = self.lex_and_parse(
                text.value,
                self.message_handler,
                self.environment,
                start_line=start_line,
                start_column=start_column,
                source_filename=source_filename,
            )
            nodes = parser.nodes
        else:
            nodes = [
                TextNode(
                    target.value,
                    info=target.info,
                )
            ]

        node = MacroLinkNode(
            f"mailto:{target.value}",
            content=nodes,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_class(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a class macro in the form [class](text, class1, class2, ...).

        # Assign names to arguments.
        parser.set_names(["text"])

        # Extract the classes.
        classes = [node.value for node in parser.unnamed_argument_nodes]

        # Extract the text.
        try:
            text = parser.named_argument_nodes["text"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory TEXT. Syntax: [class](TEXT, class1, class2, ...).",
                context=context,
            ) from exc

        # Unpack the text initial position.
        start_line, start_column = text.info.context.start_position

        # Get the text source.
        source_filename = text.info.context.source

        # Parse the text
        parser = self.lex_and_parse(
            text.value,
            self.message_handler,
            self.environment,
            start_line=start_line,
            start_column=start_column,
            source_filename=source_filename,
        )

        node = MacroClassNode(
            classes,
            content=parser.nodes,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_unicode(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a unicode macro in the form [unicode](value).

        # Assign names to arguments.
        parser.set_names(["value"])

        # Extract the value.
        try:
            value = parser.named_argument_nodes["value"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory VALUE. Syntax: [unicode](VALUE).",
                context=context,
            ) from exc

        node = MacroUnicodeNode(
            value.value,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_raw(self, parser: ArgumentsParser, context: Context) -> list[Node]:
        # Parse a raw macro in the form [raw](value).

        # Assign names to arguments.
        parser.set_names(["value"])

        # Extract the value.
        try:
            value = parser.named_argument_nodes["value"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory VALUE. Syntax: [raw](VALUE).",
                context=context,
            ) from exc

        node = MacroRawNode(
            value.value,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_image(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse an inline image macro in the form [image](uri, alt_text, width, height).

        # Assign names to arguments.
        parser.set_names(["uri", "alt_text", "width", "height"])

        # Extract the URI.
        try:
            uri = parser.named_argument_nodes["uri"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory URI. Syntax: [image](URI, alt_text, width, height).",
                context=context,
            ) from exc

        # Get the remaining parameters
        alt_text_node = parser.named_argument_nodes.get("alt_text")
        width_node = parser.named_argument_nodes.get("width")
        height_node = parser.named_argument_nodes.get("height")

        # Extract the value if the parameter is not None.
        alt_text = alt_text_node.value if alt_text_node else None
        width = width_node.value if width_node else None
        height = height_node.value if height_node else None

        node = MacroImageNode(
            uri=uri.value,
            alt_text=alt_text,
            width=width,
            height=height,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        return [node]

    def _parse_macro_footnote(
        self, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a footnote macro in the form [footnote](name).

        # Assign names to arguments.
        parser.set_names(["name"])

        # Extract the footnote name.
        try:
            name_node = parser.named_argument_nodes["name"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Missing mandatory NAME. Syntax: [footnote](NAME).",
                context=context,
            ) from exc

        name = name_node.value

        node = MacroFootnoteNode(
            name=name,
            parent=self.parent_node,
            info=NodeInfo(context=context),
        )

        self.footnote_macros.append(node)

        return [node]

    def _parse_macro_control(
        self, macro_name_token: Token, parser: ArgumentsParser, context: Context
    ) -> list[Node]:
        # Parse a class macro in the form [if:condition](true, false) or
        # [ifeval:condition](var1, var2).
        #
        # Example:
        #
        # If the value of flag is 42 return "TRUE", otherwise return "FALSE"
        # [if:flag==42]("TRUE", "FALSE")

        # Get the name of the macro.
        name = macro_name_token.value

        # Split the name into operator:condition
        try:
            operator, condition = name.split(":")
        except ValueError as exc:
            raise create_parser_exception(
                f"Macro name '{name}' must be in the form 'operator:condition'.",
                context=context,
            ) from exc

        # Check if the operator is supported.
        if operator not in ["if", "ifeval"]:
            raise create_parser_exception(
                f"Control operator '{operator}' is not supported.",
                context=context,
            )

        # Remember if we need to evaluate the result.
        evaluate = operator == "ifeval"

        # Both ifeval and if are checking the same logic.
        operator = "if"

        # We need to find the context of the condition.
        # It is the macro name token context shifted
        # by the legth of the operator plus the colon.
        shift = len(f"@{operator}:")
        condition_context = macro_name_token.context.clone()
        condition_context.start_column += shift

        # Unpack the text initial position.
        start_line, start_column = condition_context.start_position

        # Get the text source.
        source_filename = condition_context.source

        # Replace variables
        try:
            condition_parser = ConditionParser.lex_and_parse(
                text=condition,
                message_handler=parser.message_handler,
                environment=parser.environment,
                start_line=start_line,
                start_column=start_column,
                source_filename=source_filename,
            )
        except MauException as exc:
            raise create_parser_exception(
                f"Wrong condition syntax: '{condition}' (probably missing or incorrect comparison).",
                condition_context,
            ) from exc

        # At the moment we support only one condition.
        condition_node = condition_parser.condition_node

        control = Control(
            operator,
            condition_node.variable,
            condition_node.comparison,
            condition_node.value,
            macro_name_token.context,
        )

        # Assign names to arguments.
        parser.set_names(["true_case", "false_case"])

        # Get the mandatory values
        try:
            true_case = parser.named_argument_nodes["true_case"]
        except KeyError as exc:
            raise create_parser_exception(
                text="Control macro is missing the mandatory value for the true case.",
                context=context,
            ) from exc

        # The false case is not mandatory, default is None.
        false_case = parser.named_argument_nodes.get("false_case")

        # Check if the condition is true or false.
        test = control.process(self.environment)

        result = true_case if test else false_case

        # Let's evaluate the result if we need to.
        if evaluate:
            if result is None:
                raise create_parser_exception(
                    "The test result is negative but no value has been defined for that case.",
                    context=context,
                )

            # Find the value of the variable.
            variable_value = self.environment.get(
                result.value,
            )

            # If the variable wasn't defined yell at the user.
            if variable_value is None:
                raise create_parser_exception(
                    f"Variable '{result.value}' has not been defined.",
                    context=context,
                )

            result.value = variable_value

        nodes = []
        if result is not None:
            parser = self.lex_and_parse(
                result.value,
                self.message_handler,
                self.environment,
                *result.info.context.start_position,
                result.info.context.source,
            )
            nodes = parser.nodes

        return nodes
