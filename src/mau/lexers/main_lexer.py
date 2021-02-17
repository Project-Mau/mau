import re

from mau.lexers.base_lexer import BaseLexer, TokenTypes
from mau.lexers.arguments_lexer import ArgumentsLexer


class MainLexer(BaseLexer):
    def _process_empty_line(self):
        regexp = re.compile(r"^\ +$")

        match = regexp.match(self._current_line)

        if not match:
            return None

        self._skip(len(match.group()))

    def _process_horizontal_rule(self):
        if not self._current_line == "---":
            return None

        return self._create_token_and_skip(TokenTypes.LITERAL, self._current_line)

    def _process_comment(self):
        regexp = re.compile("^(//.*)")

        match = regexp.match(self._current_line)

        if not match:
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.TEXT, match.group(1)),
            self._create_token_and_skip(TokenTypes.EOL),
        ]

        return tokens

    def _process_multiline_comment(self):
        if not self._current_line.startswith("////"):
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, self._current_line),
            self._create_token_and_skip(TokenTypes.EOL),
        ]
        return tokens

    def _process_header(self):
        regexp = re.compile("^(=+!?)( +)(.*)")

        match = regexp.match(self._current_line)

        if not match:
            return None

        if not match.group(2):
            return None

        if not match.group(3):
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, match.group(1)),
            self._create_token_and_skip(TokenTypes.WHITESPACE, match.group(2)),
            self._create_token_and_skip(TokenTypes.TEXT, match.group(3)),
            self._create_token_and_skip(TokenTypes.EOL),
        ]

        return tokens

    def _process_list(self):
        regexp = re.compile(r"^( *)([\*#]+)( +)(.*)")

        match = regexp.match(self._current_line)

        if not match:
            return None

        if not match.group(4):
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

    def _process_id(self):
        if self._current_char != "#":
            return None

        return self._create_token_and_skip(TokenTypes.LITERAL, self._current_char)

    def _process_title(self):
        regexp = re.compile(r"^\.( *)(.*)")

        match = regexp.match(self._current_line)

        if not match:
            return None

        if not match.group(2):
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
        regexp = re.compile(r"^<<( +)([^(]+)((.*))?")

        match = regexp.match(self._current_line)

        if not match:
            return None

        if not match.group(2):
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

        regexp = re.compile(r"::([a-z0-9_]+):(.*)?")

        match = regexp.match(self._current_line)

        if not match:  # pragma: no cover
            return None

        tokens = [
            self._create_token_and_skip(TokenTypes.LITERAL, "::"),
            self._create_token_and_skip(TokenTypes.TEXT, match.group(1)),
            self._create_token_and_skip(TokenTypes.LITERAL, ":"),
        ]

        if match.group(2):
            tokens.append(self._create_token_and_skip(TokenTypes.TEXT, match.group(2)))

        tokens.append(self._create_token_and_skip(TokenTypes.EOL))

        return tokens

    def _process_variable_definition(self):
        if self._current_char != ":":
            return None

        regexp = re.compile(r":([!a-zA-Z0-9\-_\.]+):(.*)?")

        match = regexp.match(self._current_line)

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
            self._process_id,
            self._process_attributes,
            self._process_include_content,
            self._process_variable_definition,
            self._process_text,
        ]
