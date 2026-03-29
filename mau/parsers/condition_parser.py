from __future__ import annotations

from mau.environment.environment import Environment
from mau.lexers.condition_lexer import ConditionLexer
from mau.message import BaseMessageHandler
from mau.nodes.condition import ConditionNode
from mau.nodes.node import NodeInfo
from mau.parsers.base_parser import BaseParser
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.text_buffer import Context
from mau.token import Token, TokenType


class ConditionParser(BaseParser):
    lexer_class = ConditionLexer

    def __init__(
        self,
        tokens: list[Token],
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
        parent_node=None,
    ):
        super().__init__(tokens, message_handler, environment, parent_node)

        # This is the list of condition nodes.
        self.condition_node: ConditionNode = None

    def _process_functions(self):
        return [
            self._process_condition,
        ]

    def _process_condition(self):
        # This parses a condition in the form
        # variable comparison value
        # e.g. flag == 42 or flag != off

        # Get the variable
        variable_token = self.tm.get_token(TokenType.TEXT)

        # Get the comparison
        comparison_token = self.tm.get_token(TokenType.TEXT)

        # Get the value
        value_token = self.tm.get_token(TokenType.TEXT)

        # Find the final context.
        context = Context.merge_contexts(variable_token.context, value_token.context)

        # Save the node.
        node = ConditionNode(
            variable=variable_token.value,
            comparison=comparison_token.value,
            value=value_token.value,
            info=NodeInfo(context=context),
            parent=self.parent_node,
        )

        self.condition_node = node

        return True


def process_condition_with_variables(
    condition_token: Token,
    message_handler: BaseMessageHandler,
    environment: Environment | None = None,
) -> ConditionParser:
    # Unpack the text initial position.
    start_line, start_column = condition_token.context.start_position

    # Get the text source.
    source_filename = condition_token.context.source

    # Replace variables in the text.
    preprocess_parser = PreprocessVariablesParser.lex_and_parse(
        text=condition_token.value,
        message_handler=message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
    )

    # The preprocess parser outputs a single node.
    text_token = preprocess_parser.get_processed_text()

    # Parse the arguments.
    condition_parser = ConditionParser.lex_and_parse(
        text=text_token.value,
        message_handler=message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
    )

    return condition_parser
