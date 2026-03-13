from mau.lexers.text_lexer import TextLexer
from mau.test_helpers import (
    compare_asdict_list,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.token import Token, TokenType

init_lexer = init_lexer_factory(TextLexer)

runner = lexer_runner_factory(TextLexer)


def test_normal_text():
    lex = runner("Normal text")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Normal", generate_context(0, 0, 0, 6)),
            Token(TokenType.TEXT, " ", generate_context(0, 6, 0, 7)),
            Token(TokenType.TEXT, "text", generate_context(0, 7, 0, 11)),
            Token(TokenType.EOF, "", generate_context(0, 11, 0, 11)),
        ],
    )


def test_underscore():
    lex = runner("_underscore_")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "_", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "underscore", generate_context(0, 1, 0, 11)),
            Token(TokenType.LITERAL, "_", generate_context(0, 11, 0, 12)),
            Token(TokenType.EOF, "", generate_context(0, 12, 0, 12)),
        ],
    )


def test_star():
    lex = runner("*star*")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "*", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "star", generate_context(0, 1, 0, 5)),
            Token(TokenType.LITERAL, "*", generate_context(0, 5, 0, 6)),
            Token(TokenType.EOF, "", generate_context(0, 6, 0, 6)),
        ],
    )


def test_caret():
    lex = runner("^caret^")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "^", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "caret", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, "^", generate_context(0, 6, 0, 7)),
            Token(TokenType.EOF, "", generate_context(0, 7, 0, 7)),
        ],
    )


def test_tilde():
    lex = runner("~tilde~")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "~", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "tilde", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, "~", generate_context(0, 6, 0, 7)),
            Token(TokenType.EOF, "", generate_context(0, 7, 0, 7)),
        ],
    )


def test_backtick():
    lex = runner("`backtick`")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "`", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "backtick", generate_context(0, 1, 0, 9)),
            Token(TokenType.LITERAL, "`", generate_context(0, 9, 0, 10)),
            Token(TokenType.EOF, "", generate_context(0, 10, 0, 10)),
        ],
    )


def test_dollar():
    lex = runner("$dollar$")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "$", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "dollar", generate_context(0, 1, 0, 7)),
            Token(TokenType.LITERAL, "$", generate_context(0, 7, 0, 8)),
            Token(TokenType.EOF, "", generate_context(0, 8, 0, 8)),
        ],
    )


def test_percent():
    lex = runner("%percent%")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "%", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "percent", generate_context(0, 1, 0, 8)),
            Token(TokenType.LITERAL, "%", generate_context(0, 8, 0, 9)),
            Token(TokenType.EOF, "", generate_context(0, 9, 0, 9)),
        ],
    )


def test_curly_braces():
    # A text paragraph should be processed by the
    # variable substitution preprocessor first,
    # so any variable-like syntax left behind
    # is just the literal text.
    lex = runner("{curly}")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "{curly}", generate_context(0, 0, 0, 7)),
            Token(TokenType.EOF, "", generate_context(0, 7, 0, 7)),
        ],
    )


def test_round_brackets():
    lex = runner("(round)")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "(", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "round", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, ")", generate_context(0, 6, 0, 7)),
            Token(TokenType.EOF, "", generate_context(0, 7, 0, 7)),
        ],
    )


def test_square_brackets():
    lex = runner("[square]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "[", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "square", generate_context(0, 1, 0, 7)),
            Token(TokenType.LITERAL, "]", generate_context(0, 7, 0, 8)),
            Token(TokenType.EOF, "", generate_context(0, 8, 0, 8)),
        ],
    )


def test_macro():
    lex = runner("[macro](value1,value2)")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "[", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "macro", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, "]", generate_context(0, 6, 0, 7)),
            Token(TokenType.LITERAL, "(", generate_context(0, 7, 0, 8)),
            Token(TokenType.TEXT, "value1,value2", generate_context(0, 8, 0, 21)),
            Token(TokenType.LITERAL, ")", generate_context(0, 21, 0, 22)),
            Token(TokenType.EOF, "", generate_context(0, 22, 0, 22)),
        ],
    )


def test_macro_named_arguments():
    lex = runner("[macro](attr1=value1,attr2=value2)")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "[", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "macro", generate_context(0, 1, 0, 6)),
            Token(TokenType.LITERAL, "]", generate_context(0, 6, 0, 7)),
            Token(TokenType.LITERAL, "(", generate_context(0, 7, 0, 8)),
            Token(
                TokenType.TEXT,
                "attr1=value1,attr2=value2",
                generate_context(0, 8, 0, 33),
            ),
            Token(TokenType.LITERAL, ")", generate_context(0, 33, 0, 34)),
            Token(TokenType.EOF, "", generate_context(0, 34, 0, 34)),
        ],
    )


def test_escaped_underscore():
    lex = runner(r"\_underscore\_")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "_", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "underscore", generate_context(0, 2, 0, 12)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 12, 0, 13)),
            Token(TokenType.LITERAL, "_", generate_context(0, 13, 0, 14)),
            Token(TokenType.EOF, "", generate_context(0, 14, 0, 14)),
        ],
    )


def test_escaped_square_brackets():
    lex = runner(r"\[square\]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "[", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "square", generate_context(0, 2, 0, 8)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 8, 0, 9)),
            Token(TokenType.LITERAL, "]", generate_context(0, 9, 0, 10)),
            Token(TokenType.EOF, "", generate_context(0, 10, 0, 10)),
        ],
    )


def test_escaped_round_brackets():
    lex = runner(r"\(round\)")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "(", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "round", generate_context(0, 2, 0, 7)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 7, 0, 8)),
            Token(TokenType.LITERAL, ")", generate_context(0, 8, 0, 9)),
            Token(TokenType.EOF, "", generate_context(0, 9, 0, 9)),
        ],
    )


def test_escaped_curly_braces():
    lex = runner(r"\{curly\}")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "{curly", generate_context(0, 1, 0, 7)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 7, 0, 8)),
            Token(TokenType.TEXT, "}", generate_context(0, 8, 0, 9)),
            Token(TokenType.EOF, "", generate_context(0, 9, 0, 9)),
        ],
    )


def test_escaped_quotes():
    lex = runner(r"\"quotes\"")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, '"', generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "quotes", generate_context(0, 2, 0, 8)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 8, 0, 9)),
            Token(TokenType.LITERAL, '"', generate_context(0, 9, 0, 10)),
            Token(TokenType.EOF, "", generate_context(0, 10, 0, 10)),
        ],
    )


def test_escaped_backticks():
    lex = runner(r"\`backticks\`")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "`", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "backticks", generate_context(0, 2, 0, 11)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 11, 0, 12)),
            Token(TokenType.LITERAL, "`", generate_context(0, 12, 0, 13)),
            Token(TokenType.EOF, "", generate_context(0, 13, 0, 13)),
        ],
    )


def test_escaped_dollar():
    lex = runner(r"\$dollar\$")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "$", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "dollar", generate_context(0, 2, 0, 8)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 8, 0, 9)),
            Token(TokenType.LITERAL, "$", generate_context(0, 9, 0, 10)),
            Token(TokenType.EOF, "", generate_context(0, 10, 0, 10)),
        ],
    )


def test_escaped_percent():
    lex = runner(r"\%percent\%")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LITERAL, "\\", generate_context(0, 0, 0, 1)),
            Token(TokenType.LITERAL, "%", generate_context(0, 1, 0, 2)),
            Token(TokenType.TEXT, "percent", generate_context(0, 2, 0, 9)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 9, 0, 10)),
            Token(TokenType.LITERAL, "%", generate_context(0, 10, 0, 11)),
            Token(TokenType.EOF, "", generate_context(0, 11, 0, 11)),
        ],
    )
