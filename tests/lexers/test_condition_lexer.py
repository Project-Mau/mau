from mau.lexers.base_lexer import TokenType
from mau.lexers.condition_lexer import ConditionLexer
from mau.test_helpers import (
    compare_asdict_list,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.token import Token

init_lexer = init_lexer_factory(ConditionLexer)

runner = lexer_runner_factory(ConditionLexer)


def test_condition():
    lex = runner("somevar==value")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "somevar", generate_context(0, 0, 0, 7)),
            Token(TokenType.TEXT, "==", generate_context(0, 7, 0, 9)),
            Token(TokenType.TEXT, "value", generate_context(0, 9, 0, 14)),
            Token(TokenType.EOF, "", generate_context(0, 14, 0, 14)),
        ],
    )


def test_condition_with_space():
    lex = runner("somevar  !=   value")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "somevar", generate_context(0, 0, 0, 7)),
            Token(TokenType.TEXT, "!=", generate_context(0, 9, 0, 11)),
            Token(TokenType.TEXT, "value", generate_context(0, 14, 0, 19)),
            Token(TokenType.EOF, "", generate_context(0, 19, 0, 19)),
        ],
    )
