from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.parsers.base_parser import BaseParser, create_parser_exception
from mau.text_buffer import Context
from mau.token import Token, TokenType


# The PreprocessVariablesParser processes tokens,
# scans for variables in the form `{name}`,
# replaces them, and finally outputs a single
# node that contains the whole text.
class PreprocessVariablesParser(BaseParser):
    lexer_class = PreprocessVariablesLexer

    def _process_escaped_char(self):
        # Process escaped characters.
        # This checks if the escaped character
        # is the opening or closing curly brace, in
        # which case it stores it as it is
        # preventing the variable replacement
        # process to take place.

        # Check is the token is an escape backslash.
        backslash = self.tm.get_token(TokenType.LITERAL, "\\")

        # Get the following character.
        char = self.tm.get_token()

        # If the character is not a curly brace
        # restore the escape backslash.
        if char.value not in "{}":
            char.value = f"\\{char.value}"

        # Merge the two contexts.
        context = Context.merge_contexts(backslash.context, char.context)

        self._save(
            TextNode(
                char.value,
                info=NodeInfo(context=context),
            )
        )

        return True

    def _process_verbatim(self):
        # Process text surrounded by backticks.
        # Such text should be left untouched.
        # Verbatim is often used for code and
        # chances are that the syntax `{name}`
        # might be used as curly braces are
        # widespread in coding.

        # Check if the token is the opening backtick.
        opening_tick = self.tm.get_token(TokenType.LITERAL, "`")

        # Get everything before the closing backtick.
        text = self.tm.collect_join(
            [Token.generate(TokenType.LITERAL, "`")],
            preserve_escaped_stop_tokens=True,
        )

        # Check if the token is the closing backtick.
        closing_tick = self.tm.get_token(TokenType.LITERAL, "`")

        # Find the final context.
        context = Context.merge_contexts(opening_tick.context, closing_tick.context)

        # Restore the original form of the text
        # with the surrounding backticks.
        text_content = f"`{text.value}`"

        self._save(
            TextNode(
                text_content,
                info=NodeInfo(context=context),
            )
        )

        return True

    def _process_curly(self):
        # This is the core of the replacement process.
        # If the function detects text between curly
        # braces it uses it as the name of a variable
        # and replaces it.

        # Check if the token is the opening curly brace.
        opening_bracket = self.tm.get_token(TokenType.LITERAL, "{")

        # Get everything before the closing brace.
        variable_name = self.tm.collect_join(
            stop_tokens=[Token.generate(TokenType.LITERAL, "}")]
        )

        # Check if the token is the closing curly brace.
        closing_bracket = self.tm.get_token(TokenType.LITERAL, "}")

        # Find the final context.
        context = Context.merge_contexts(
            opening_bracket.context, closing_bracket.context
        )

        if variable_name.value.startswith("{"):
            # We might be trying to escape a piece of text
            # in the form "{text}" that should be kept
            # as it is, with curly braces surrounding it.
            # In that case the input would be
            # {{text}}
            # and we would have variable_name equal to
            # {text, as the final } would be mistaken
            # for the closing bracket.

            # Check if there is another bracket after
            # the closing one.
            if not self.tm.peek_token_is(TokenType.LITERAL, "}"):
                raise create_parser_exception(
                    f"Incomplete variable declaration '{variable_name.value}'. Variable names cannot contain curly braces.",
                    context=variable_name.context,
                )

            # There is another bracket. Consume it.
            actual_closing_bracket = self.tm.get_token(TokenType.LITERAL, "}")

            # The text is not a variable, restore it
            # adding a final "}"
            text = variable_name.value + "}"

            # Calculate the final context.
            context = Context.merge_contexts(
                opening_bracket.context, actual_closing_bracket.context
            )

            self._save(
                TextNode(
                    text,
                    info=NodeInfo(context=context),
                )
            )

            return True

        try:
            # Extract from the environment the variable
            # mentioned between curly braces.
            variable_value = self.environment[variable_name.value]

            # Make sure the variable value is text.
            # When the environment is created externally,
            # all sorts of Python types can be passed
            # but once we enter the Mau space, it has to
            # be a string. Not string no party.
            variable_value = str(variable_value)
        except KeyError as exp:
            raise create_parser_exception(
                f"Variable '{variable_name.value}' has not been defined.",
                context=context,
            ) from exp

        self._save(
            TextNode(
                variable_value,
                info=NodeInfo(context=context),
            )
        )

        return True

    def _process_pass(self):
        # None of the previous functions succeeded,
        # so we are in front of a pure text token.
        # Just store it and move on.

        text_token = self.tm.get_token()

        self._save(
            TextNode(
                text_token.value,
                info=NodeInfo(context=text_token.context),
            )
        )

        return True

    def _process_functions(self):
        return [
            self._process_escaped_char,
            self._process_verbatim,
            self._process_curly,
            self._process_pass,
        ]

    def get_processed_text(self) -> Token:
        # After having parsed the text and replaced the
        # variables, this parser should eventually return
        # a single piece of text.
        # However, the method `parse()` is bound to return
        # a list of nodes as per the definition in it parent.
        # This method groups the value of all text nodes
        # and returns a single token.

        text_tokens = [
            Token(
                TokenType.TEXT,
                i.value,
                i.info.context,
            )
            for i in self.nodes
        ]

        return Token.from_token_list(text_tokens)
