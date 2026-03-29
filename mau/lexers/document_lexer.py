import logging
from typing import Callable

from mau.lexers.base_lexer import BaseLexer, create_lexer_exception, rematch
from mau.text_buffer import Context
from mau.token import Token, TokenType

logger = logging.getLogger(__name__)


class DocumentLexer(BaseLexer):
    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_multiline_comment,
            self._process_comment,
            self._process_horizontal_rule,
            self._process_block,
            self._process_control,
            self._process_include,
            self._process_variable,
            self._process_arguments,
            self._process_label,
            self._process_list,
            self._process_header,
            # This is provided by BaseLexer
            self._process_text,
        ]

    def _process_multiline_comment(self) -> list[Token] | None:
        # Detect the beginning of a multiline comment
        # represented by four slashes ////.

        # If the current line does not
        # contain the opening slashes
        # just move on.
        if self._current_line != "////":
            return None

        # Record the initial position.
        initial_position = self._position

        # Move to the next line.
        self._nextline()

        # Keep checking if we reached the
        # end of the multiline comment
        # section or if we reach EOF.
        while True:
            # If we reached the EOF we have a problem.
            if self.text_buffer.eof:
                raise create_lexer_exception(
                    text="Unclosed multiline comment.",
                    source=self.text_buffer.source_filename,
                    position=initial_position,
                )

            # If reached the closing slashes
            # we need to stop this loop.
            if self._current_line == "////":
                break

            # If we get here it's because
            # we haven't reached the closing
            # slashes, so the line is still
            # a comment that we should ignore.
            self._nextline()

        # The current line contains the
        # closing slashes, skip it.
        self._nextline()

        return []

    def _process_comment(self) -> list[Token] | None:
        # Detect a single line comment that
        # starts with two slashes //.

        # Check if the line starts with two slashes.
        match = rematch(r"^//.*", self._current_line)

        # If the current line does not match just move on.
        if not match:
            return None

        # Move to the next line.
        self._nextline()

        return []

    def _process_horizontal_rule(self) -> list[Token] | None:
        # Detect a horizontal rule represented by
        # three dashes ---.

        # Check if the three dashes are the
        # only content of the line.
        match = rematch(r"^---$", self._current_line)

        # If the current line does not match just move on.
        if match is None:
            return None

        tokens = [
            self._create_token_and_skip(TokenType.HORIZONTAL_RULE, self._current_line)
        ]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_block(self) -> list[Token] | None:
        # Detect a block of text surrounded by
        # a delimiter made of four identical characters,
        # e.g. @@@@ or ####

        # If the line doesn't contain exactly
        # 4 characters this is not a block.
        if len(self._current_line) != 4:
            return None

        # Try to match the block delimiter
        # finding four repetitions of the
        # same character.
        match = rematch(r"^(.)\1{3}$", self._current_line)

        # If the current line does not match just move on.
        if match is None:
            return None

        # Create the token for the delimiter.
        delimiter = self._create_token_and_skip(TokenType.BLOCK, self._current_line)

        tokens = [
            delimiter,
        ]

        # Move to the next line.
        self._nextline()

        # Get the initial position of the block content.
        initial_position = self._position

        # We need to collect all text lines
        # contained between two delimiters.
        text_lines = []

        while True:
            # Check if we reached the EOF.
            if self.text_buffer.eof:
                raise create_lexer_exception(
                    text="Unclosed block.",
                    source=self.text_buffer.source_filename,
                    position=delimiter.context.start_position,
                )

            # If the current line contains only the
            # closing delimiter we can stop the loop.
            if self._current_line == delimiter.value:
                break

            # If we reach this point we are looking
            # at a line inside the block.
            # Store it and move on.
            text_lines.append(self._current_line)

            # Move to the next line.
            self._nextline()

        # If we collected text lines create a
        # text token that contains them.
        if text_lines:
            # Find the final position after
            # the end of the block content.
            end_line = initial_position[0] + len(text_lines) - 1
            end_column = initial_position[1] + len(text_lines[-1])

            # Create the context of the
            # block content.
            context = Context(
                *initial_position,
                end_line,
                end_column,
                self.text_buffer.source_filename,
            )

            # Create the token value joining
            # all the block content lines.
            content = "\n".join(text_lines)

            # Create the content token.
            tokens.append(Token(TokenType.TEXT, content, context))

        # Create the token for the closing delimiter.
        closing_delimiter = self._create_token_and_skip(
            TokenType.BLOCK, self._current_line
        )

        tokens.append(
            Token(TokenType.BLOCK, self._current_line, closing_delimiter.context)
        )

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_control(self) -> list[Token] | None:
        # Detect control logic in the form
        #
        # @OPERATOR CONDITION
        #

        # Try to match the syntax shown above.
        match = rematch(
            (
                r"^(?P<prefix>@)(?P<operator>[a-z]+)(?P<whitespace> *)"
                r"(?P<condition>.*)$"
            ),
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        operator = match.groupdict().get("operator")
        whitespace = match.groupdict().get("whitespace")
        condition = match.groupdict().get("condition")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.CONTROL, prefix)
        operator_token = self._create_token_and_skip(TokenType.TEXT, operator)
        self._skip(whitespace)
        condition_token = self._create_token_and_skip(TokenType.TEXT, condition)

        tokens = [
            prefix_token,
            operator_token,
            condition_token,
        ]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_include(self) -> list[Token] | None:
        # Detect included content in the form
        #
        # <<TYPE[:ARGUMENTS]
        # or
        # << TYPE[:ARGUMENTS]
        #
        # The content TYPE can contain lowercase
        # letters, numbers, and the characters
        # _ # .

        # Try to match the syntax shown above.
        match = rematch(
            r"^(?P<prefix><<)(?P<whitespace> *)(?P<type>[a-z0-9_#\.]+)(?P<separator>:)?(?P<arguments>.*)?",
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        whitespace = match.groupdict().get("whitespace")
        content_type = match.groupdict().get("type")
        separator = match.groupdict().get("separator")
        arguments = match.groupdict().get("arguments")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.INCLUDE, prefix)
        self._skip(whitespace)
        content_type_token = self._create_token_and_skip(TokenType.TEXT, content_type)
        separator_token = self._create_token_and_skip(TokenType.LITERAL, separator)
        arguments_token = self._create_token_and_skip(TokenType.TEXT, arguments)

        tokens = [prefix_token, content_type_token]

        # The separator is optional, the value can be None.
        if separator:
            tokens.append(separator_token)

        # The arguments are optional, the value can be None.
        if arguments:
            tokens.append(arguments_token)

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_variable(self) -> list[Token] | None:
        # Detect a variable definition in the form
        #
        # :NAME[:VALUE]
        #
        # The variable NAME can contain alphanumeric
        # characters and the characters
        # _ . + -

        # Try to match the syntax shown above.
        match = rematch(
            r"^(?P<prefix>:)(?P<name>[a-zA-Z0-9_\.\+\-]+)(?P<separator>:)?(?P<value>.*)?",
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        name = match.groupdict().get("name")
        separator = match.groupdict().get("separator")
        value = match.groupdict().get("value")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.VARIABLE, prefix)
        name_token = self._create_token_and_skip(TokenType.TEXT, name)
        separator_token = self._create_token_and_skip(TokenType.LITERAL, separator)
        value_token = self._create_token_and_skip(TokenType.TEXT, value)

        tokens = [prefix_token, name_token]

        # The separator is optional, the value can be None.
        if separator:
            tokens.append(separator_token)

        # The arguments are optional, the value can be None.
        if value:
            tokens.append(value_token)

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_arguments(self) -> list[Token] | None:
        # Detect arguments in the form
        #
        # [ARGUMENTS]

        # Try to match the syntax shown above.
        match = rematch(
            r"^(?P<prefix>\[)(?P<arguments>.*)(?P<suffix>\])$",
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        arguments = match.groupdict().get("arguments")
        suffix = match.groupdict().get("suffix")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.ARGUMENTS, prefix)
        arguments_token = self._create_token_and_skip(TokenType.TEXT, arguments)
        suffix_token = self._create_token_and_skip(TokenType.LITERAL, suffix)

        tokens = [
            prefix_token,
            arguments_token,
            suffix_token,
        ]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_label(self) -> list[Token] | None:
        # Detect a label in the form
        #
        # . LABEL
        # or
        # .role LABEL

        # Try to match the syntax shown above.
        match = rematch(
            r"^(?P<prefix>\.[a-z0-9-_]*)(?P<whitespace> *)(?P<label>.*)",
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        whitespace = match.groupdict().get("whitespace")
        label = match.groupdict().get("label")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.LABEL, prefix)
        self._skip(whitespace)
        label_token = self._create_token_and_skip(TokenType.TEXT, label)

        tokens = [
            prefix_token,
            label_token,
        ]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_list(self) -> list[Token] | None:
        # Detect a list item in the form
        #
        # * ITEM
        # or
        # # ITEM
        #
        # Multiple prefix symbols can be specified.
        # Withespace at the beginning of the line is ignored,
        # as Mau considers only the number of prefix symbols
        # to decide the nesting level.
        # Space between the prefix symbol and text is ignored as well.

        # Try to match the syntax shown above.
        match = rematch(
            r"^(?P<whitespace1> *)(?P<prefix>[\*#]+)(?P<whitespace2> +)(?P<item>.*)",
            self._current_line,
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        whitespace1 = match.groupdict().get("whitespace1")
        prefix = match.groupdict().get("prefix")
        whitespace2 = match.groupdict().get("whitespace2")
        item = match.groupdict().get("item")

        # Create the tokens we want to keep.
        self._skip(whitespace1)
        prefix_token = self._create_token_and_skip(TokenType.LIST, prefix)
        self._skip(whitespace2)
        item_token = self._create_token_and_skip(TokenType.TEXT, item)

        tokens = [
            prefix_token,
            item_token,
        ]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_header(self) -> list[Token] | None:
        # Detect a header in the form
        #
        # =HEADER
        # or
        # = HEADER
        #
        # Multiple prefix symbols can be specified.

        # Try to match the syntax shown above.
        match = rematch(
            "^(?P<prefix>=+)(?P<whitespace> *)(?P<header>.+)", self._current_line
        )

        # If the current line does not match just move on.
        if not match:
            return None

        # Extract the values of all groups.
        prefix = match.groupdict().get("prefix")
        whitespace = match.groupdict().get("whitespace")
        header = match.groupdict().get("header")

        # Create the tokens we want to keep.
        prefix_token = self._create_token_and_skip(TokenType.HEADER, prefix)
        self._skip(whitespace)
        header_token = self._create_token_and_skip(TokenType.TEXT, header)

        tokens = [
            prefix_token,
            header_token,
        ]

        # Move to the next line.
        self._nextline()

        return tokens
