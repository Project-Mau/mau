from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.parsers.base_parser import create_parser_exception
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.text_buffer import Context
from mau.token import TokenType


def variable_definition_processor(parser: DocumentParser):
    # This parses the definition of a variable
    #
    # Simple variables are defined as :name:value
    # as True booleans as just :name:
    # and as False booleas as :!name:
    #
    # Variable names can use a namespace with
    # :namespace.name:value

    # Get the opening colon.
    opening_colon = parser.tm.get_token(TokenType.VARIABLE, ":")

    # Get the mandatory variable name token.
    variable_token = parser.tm.get_token(TokenType.TEXT)

    # Get the closing colon.
    closing_colon = parser.tm.get_token(TokenType.LITERAL, ":")

    # Get the name of the variable.
    variable_name = variable_token.value

    # Find the final context.
    context = Context.merge_contexts(opening_colon.context, closing_colon.context)

    # Get the optional variable value.
    value: str = ""
    if parser.tm.peek_token().type == TokenType.TEXT:
        value_token = parser.tm.get_token()
        value = value_token.value
        context = Context.merge_contexts(context, value_token.context)

    # Process the variable according to its nature.
    if variable_name.startswith("+"):
        # If the name starts with "+" it's a true flag.
        variable_name = variable_name[1:]
        value = "true"
    elif variable_name.startswith("-"):
        # If the name starts with "-" it's a false flag.
        variable_name = variable_name[1:]
        value = "false"
    elif value:
        # The variable value might contain
        # other variables, so we need to
        # replace them.

        # Unpack the text initial position.
        start_line, start_column = context.start_position

        # Get the text source.
        source_filename = context.source

        preprocess_parser = PreprocessVariablesParser.lex_and_parse(
            text=value,
            message_handler=parser.message_handler,
            environment=parser.environment,
            start_line=start_line,
            start_column=start_column,
            source_filename=source_filename,
        )

        # The preprocess parser returns always
        # a single node.
        value = preprocess_parser.get_processed_text().value

    if value == "":
        raise create_parser_exception(
            f"Error in variable definition. Variable '{variable_name}' has no value.",
            context,
        )

    # Now that we have name and value,
    # create or update the variable in
    # the environment.
    parser.environment[variable_name] = value

    return True
