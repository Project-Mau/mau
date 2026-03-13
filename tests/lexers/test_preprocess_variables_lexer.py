from mau.lexers.base_lexer import TokenType
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.test_helpers import (
    compare_asdict_list,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.token import Token

init_lexer = init_lexer_factory(PreprocessVariablesLexer)

runner = lexer_runner_factory(PreprocessVariablesLexer)


def test_normal_text():
    lex = runner("Some text")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Some text", generate_context(0, 0, 0, 9)),
            Token(TokenType.EOF, "", generate_context(0, 9, 0, 9)),
        ],
    )


def test_match_only_backticks_and_curly_braces():
    lex = runner("Normal text `{curly}` _other_ *text*")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Normal text ", generate_context(0, 0, 0, 12)),
            Token(TokenType.LITERAL, "`", generate_context(0, 12, 0, 13)),
            Token(TokenType.LITERAL, "{", generate_context(0, 13, 0, 14)),
            Token(TokenType.TEXT, "curly", generate_context(0, 14, 0, 19)),
            Token(TokenType.LITERAL, "}", generate_context(0, 19, 0, 20)),
            Token(TokenType.LITERAL, "`", generate_context(0, 20, 0, 21)),
            Token(TokenType.TEXT, " _other_ *text*", generate_context(0, 21, 0, 36)),
            Token(TokenType.EOF, "", generate_context(0, 36, 0, 36)),
        ],
    )


def test_escape_curly_braces():
    lex = runner(r"Normal text \{curly\} _other_ *text*")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Normal text ", generate_context(0, 0, 0, 12)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 12, 0, 13)),
            Token(TokenType.LITERAL, "{", generate_context(0, 13, 0, 14)),
            Token(TokenType.TEXT, "curly", generate_context(0, 14, 0, 19)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 19, 0, 20)),
            Token(TokenType.LITERAL, "}", generate_context(0, 20, 0, 21)),
            Token(TokenType.TEXT, " _other_ *text*", generate_context(0, 21, 0, 36)),
            Token(TokenType.EOF, "", generate_context(0, 36, 0, 36)),
        ],
    )


def test_preserve_escapes():
    lex = runner(r"Normal \text \_other\_")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Normal ", generate_context(0, 0, 0, 7)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 7, 0, 8)),
            Token(TokenType.TEXT, "text ", generate_context(0, 8, 0, 13)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 13, 0, 14)),
            Token(TokenType.TEXT, "_other", generate_context(0, 14, 0, 20)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 20, 0, 21)),
            Token(TokenType.TEXT, "_", generate_context(0, 21, 0, 22)),
            Token(TokenType.EOF, "", generate_context(0, 22, 0, 22)),
        ],
    )


def test_match_curly_braces_at_beginning_and_end():
    lex = runner("{begin} and {end}")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "{", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "begin", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, "}", generate_context(0, 6, 0, 7)),
            Token(TokenType.TEXT, " and ", generate_context(0, 7, 0, 12)),
            Token(TokenType.LITERAL, "{", generate_context(0, 12, 0, 13)),
            Token(TokenType.TEXT, "end", generate_context(0, 13, 0, 16)),
            Token(TokenType.LITERAL, "}", generate_context(0, 16, 0, 17)),
            Token(TokenType.EOF, "", generate_context(0, 17, 0, 17)),
        ],
    )
