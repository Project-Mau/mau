from mau.lexers.base_lexer import BaseLexer, TokenTypes


class MainLexer(BaseLexer):
    def _process_empty_line(self):
        match = self._rematch(r"^\ +$")

        if not match:  # pragma: no cover
            return None

        self._skip(len(match.group()))

    def _process_horizontal_rule(self):
        if not self._current_line == "---":
            return None

        return self._create_token_and_skip(TokenTypes.LITERAL, self._current_line)

    def _process_comment(self):
        match = self._rematch(r"^(//.*)")

        if not match:  # pragma: no cover
            return None

        return [
            self._create_token_and_skip(TokenTypes.TEXT, match.group(1)),
            self._create_token_and_skip(TokenTypes.EOL),
        ]

    def _process_multiline_comment(self):
        if not self._current_line.startswith("////"):
            return None

        return [
            self._create_token_and_skip(TokenTypes.LITERAL, self._current_line),
            self._create_token_and_skip(TokenTypes.EOL),
        ]

    def _process_header(self):
        match = self._rematch("^(=+!?)( +)(.*)")

        if not match:  # pragma: no cover
            return None

        if not match.group(2):  # pragma: no cover
            return None

        if not match.group(3):  # pragma: no cover
            return None

        return [
            self._create_token_and_skip(TokenTypes.LITERAL, match.group(1)),
            self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(2)),
            self._create_token_and_skip(TokenTypes.TEXT, match.group(3)),
            self._create_token_and_skip(TokenTypes.EOL),
        ]

    def _process_list(self):
        match = self._rematch(r"^( *)([\*#]+)( +)(.*)")

        if not match:  # pragma: no cover
            return None

        if not match.group(4):  # pragma: no cover
            return None

        tokens = []

        if match.group(1):
            tokens.append(
                self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(1))
            )

        tokens.extend(
            [
                self._create_token_and_skip(TokenTypes.LITERAL, match.group(2)),
                self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(3)),
                self._create_token_and_skip(TokenTypes.TEXT, match.group(4)),
            ]
        )

        return tokens

    def _process_title(self):
        match = self._rematch(r"^\.( *)(.*)")

        if not match:  # pragma: no cover
            return None

        if not match.group(2):  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, "."),
        ]

        if match.group(1):
            tokens.append(
                self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(1))
            )

        tokens.extend(
            [
                self._create_token_and_skip(TokenTypes.TEXT, match.group(2)),
                self._create_token_and_skip(TokenTypes.EOL),
            ]
        )

        return tokens

    def _process_attributes(self):
        if self._current_char != "[":
            return None

        if not self._current_line.endswith("]"):
            return None

        tokens = [self._create_token_and_skip(TokenTypes.LITERAL, "[")]

        line = self._current_line[1:-1]

        tokens.append(self._create_token_and_skip(TokenTypes.TEXT, line))
        tokens.append(self._create_token_and_skip(TokenTypes.LITERAL, "]"))
        tokens.append(self._create_token_and_skip(TokenTypes.EOL))

        return tokens

    def _process_include_content(self):
        match = self._rematch(r"^<<( +)([^(]+)((.*))?")

        if not match:  # pragma: no cover
            return None

        if not match.group(2):  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, "<<"),
            self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(1)),
            self._create_token_and_skip(TokenTypes.TEXT, match.group(2)),
        ]

        if match.group(3):
            tokens.extend(
                [
                    self._create_token_and_skip(TokenTypes.LITERAL, "("),
                    self._create_token_and_skip(TokenTypes.TEXT, match.group(3)[1:-1]),
                    self._create_token_and_skip(TokenTypes.LITERAL, ")"),
                ]
            )

        tokens.append(self._create_token_and_skip(TokenTypes.EOL))

        return tokens

    def _process_command(self):
        if not self._current_line.startswith("::"):
            return None

        match = self._rematch(r"::([a-z0-9_#\\]+):(.*)?")

        if not match:  # pragma: no cover
            return None

        value = match.group(1)

        if value.startswith("#"):
            # This is a directive
            self._nextline()

            return self._process_directive(match.group(1)[1:], match.group(2))
        elif value.startswith("\\#"):
            # This is an escaped directive,
            # remove the escape and do not process the directive
            value = value[1:]

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, "::"),
            self._create_token_and_skip(TokenTypes.TEXT, value),
            self._create_token_and_skip(TokenTypes.LITERAL, ":"),
        ]

        if match.group(2):
            tokens.append(self._create_token_and_skip(TokenTypes.TEXT, match.group(2)))

        tokens.append(self._create_token_and_skip(TokenTypes.EOL))

        return tokens

    def _process_directive(self, directive, value):
        # Process a directive

        if directive == "include":
            with open(value) as f:
                self._insert(f.read())

        return []

    def _process_variable_definition(self):
        if self._current_char != ":":
            return None

        match = self._rematch(r":([!a-zA-Z0-9\-_\.]+):(.*)?")

        if not match:  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, ":"),
            self._create_token_and_skip(TokenTypes.TEXT, match.group(1)),
            self._create_token_and_skip(TokenTypes.LITERAL, ":"),
        ]

        if match.group(2):
            tokens.append(
                self._create_token_and_skip(TokenTypes.TEXT, (match.group(2)))
            )

        tokens.append(self._create_token_and_skip(TokenTypes.EOL))

        return tokens

    def _process_text(self):
        tokens = [
            self._create_token_and_skip(TokenTypes.TEXT, self._tail),
            self._create_token_and_skip(TokenTypes.EOL),
        ]
        return tokens

    def _process_functions(self):
        return [
            self._process_eof,
            self._process_empty_line,
            self._process_eol,
            self._process_horizontal_rule,
            self._process_multiline_comment,
            self._process_comment,
            self._process_command,
            self._process_header,
            self._process_list,
            self._process_title,
            self._process_attributes,
            self._process_include_content,
            self._process_variable_definition,
            self._process_text,
        ]
