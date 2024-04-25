from mau.helpers import rematch
from mau.lexers.base_lexer import BaseLexer
from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.text_buffer.context import Context


class TokenTypes:
    ARGUMENTS = "ARGUMENTS"
    BLOCK = "BLOCK"
    COMMAND = "COMMAND"
    COMMENT = "COMMENT"
    CONTENT = "CONTENT"
    CONTROL = "CONTROL"
    HEADER = "HEADER"
    HORIZONTAL_RULE = "HORIZONTAL_RULE"
    LIST = "LIST"
    MULTILINE_COMMENT = "MULTILINE_COMMENT"
    TITLE = "TITLE"
    VARIABLE = "VARIABLE"


class MainLexer(BaseLexer):
    def _process_functions(self):
        return [
            self._process_multiline_comment,
            self._process_comment,
            self._process_horizontal_rule,
            self._process_block,
            self._process_command_or_directive,
            self._process_control,
            self._process_include,
            self._process_variable,
            self._process_arguments,
            self._process_title,
            self._process_list,
            self._process_header,
            # This is provided by BaseLexer
            self._process_text_line,
        ]

    def _process_multiline_comment(self):
        if self._current_line != "////":
            return None

        return self._create_tokens_from_line(TokenTypes.MULTILINE_COMMENT)

    def _process_comment(self):
        match = rematch(r"^(//.*)", self._current_line)

        if not match:
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.COMMENT, match.group(1)),
            self._create_token(BLTokenTypes.EOL),
        ]

        self._nextline()

        return tokens

    def _process_horizontal_rule(self):
        match = rematch(r"---$", self._current_line)

        if match is None:
            return None

        return [self._create_token_and_skip(TokenTypes.HORIZONTAL_RULE, "---")]

    def _process_block(self):
        if len(self._current_line) != 4:
            return None

        # Try to match the block delimiter
        match = rematch(r"^(.)\1{3}$", self._current_line)

        if match is None:
            return None

        return self._create_tokens_from_line(TokenTypes.BLOCK)

    def _run_directive(self, name, value):
        if name == "include":
            with open(value, encoding="utf-8") as included_file:
                text = included_file.read()
                text_buffer = self.text_buffer.__class__(text, Context(source=value))

                lexer = MainLexer(self.environment)
                lexer.process(text_buffer)

                # Remove the last token as it is an EOF
                self.tokens.extend(lexer.tokens[:-1])

    def _process_command_or_directive(self):
        match = rematch(r"::([a-z0-9_#]+):(.*)?", self._current_line)

        if not match:
            return None

        command_name = match.group(1)

        if command_name.startswith("#"):
            # This is a lexer directive
            self._run_directive(command_name[1:], match.group(2))

            self._nextline()

            return []

        tokens = [
            self._create_token_and_skip(TokenTypes.COMMAND, "::"),
            self._create_token_and_skip(BLTokenTypes.TEXT, command_name),
            self._create_token_and_skip(BLTokenTypes.LITERAL, ":"),
        ]

        if match.group(2):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(2))
            )

        tokens.append(self._create_token(BLTokenTypes.EOL))

        self._nextline()

        return tokens

    def _process_control(self):
        match = rematch(r"@([^:]+):(.*)", self._current_line)

        if not match:
            return None

        operator = match.group(1)
        statement = match.group(2)

        tokens = [
            self._create_token_and_skip(TokenTypes.CONTROL, "@"),
            self._create_token_and_skip(BLTokenTypes.TEXT, operator),
            self._create_token_and_skip(BLTokenTypes.LITERAL, ":"),
            self._create_token_and_skip(BLTokenTypes.TEXT, statement),
        ]

        tokens.append(self._create_token(BLTokenTypes.EOL))

        self._nextline()

        return tokens

    def _process_include(self):
        match = rematch(r"^<<( *)([a-z0-9_#\\\.]+):(.*)?", self._current_line)

        if not match:
            return None

        if not match.group(2):  # pragma: no cover
            return None

        tokens = [self._create_token_and_skip(TokenTypes.CONTENT, "<<")]

        if match.group(1):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.WHITESPACE, match.group(1))
            )

        tokens.extend(
            [
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(2)),
                self._create_token_and_skip(BLTokenTypes.LITERAL, ":"),
            ]
        )

        if match.group(3):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(3))
            )

        tokens.append(self._create_token(BLTokenTypes.EOL))

        self._nextline()

        return tokens

    def _process_variable(self):
        if not self._current_line.startswith(":"):
            return None

        match = rematch(r":([a-zA-Z0-9_\.\+\-]+):(.*)?", self._current_line)

        if not match:  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.VARIABLE, ":"),
            self._create_token_and_skip(BLTokenTypes.TEXT, match.group(1)),
            self._create_token_and_skip(BLTokenTypes.LITERAL, ":"),
        ]

        if match.group(2):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.TEXT, (match.group(2)))
            )

        tokens.append(self._create_token(BLTokenTypes.EOL))

        self._nextline()

        return tokens

    def _process_arguments(self):
        if not self._current_line.startswith("["):
            return None

        if not self._current_line.endswith("]"):
            return None

        line = self._current_line[1:-1]

        tokens = [
            self._create_token(TokenTypes.ARGUMENTS, "["),
            self._create_token(BLTokenTypes.TEXT, line),
            self._create_token(BLTokenTypes.LITERAL, "]"),
            self._create_token(BLTokenTypes.EOL),
        ]

        self._nextline()

        return tokens

    def _process_title(self):
        match = rematch(r"^\.( *)(.*)", self._current_line)

        if not match:
            return None

        if not match.group(2):  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.TITLE, "."),
        ]

        if match.group(1):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.WHITESPACE, match.group(1))
            )

        tokens.extend(
            [
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(2)),
                self._create_token(BLTokenTypes.EOL),
            ]
        )

        self._nextline()

        return tokens

    def _process_list(self):
        match = rematch(r"^( *)([\*#]+)( +)(.*)", self._current_line)

        if not match:
            return None

        if not match.group(4):  # pragma: no cover
            return None

        tokens = []

        if match.group(1):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.WHITESPACE, match.group(1))
            )

        tokens.extend(
            [
                self._create_token_and_skip(TokenTypes.LIST, match.group(2)),
                self._create_token_and_skip(BLTokenTypes.WHITESPACE, match.group(3)),
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(4)),
                self._create_token(BLTokenTypes.EOL),
            ]
        )

        self._nextline()

        return tokens

    def _process_header(self):
        match = rematch("^(=+)( *)(.*)", self._current_line)

        if not match:
            return None

        if not match.group(3):
            return None

        tokens = [self._create_token_and_skip(TokenTypes.HEADER, match.group(1))]

        if match.group(2):
            tokens.append(
                self._create_token_and_skip(BLTokenTypes.WHITESPACE, match.group(2))
            )

        tokens.extend(
            [
                self._create_token_and_skip(BLTokenTypes.TEXT, match.group(3)),
                self._create_token(BLTokenTypes.EOL),
            ]
        )

        self._nextline()

        return tokens
