from mau.environment.environment import Environment
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.lexers.base_lexer import TokenTypes
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token


def test_single_unnamed_argument():
    text_buffer = TextBuffer("value1")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_single_named_argument():
    text_buffer = TextBuffer("argument1=value1")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_multiple_unnamed_arguments():
    text_buffer = TextBuffer("value1, value2")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_multiple_named_arguments():
    text_buffer = TextBuffer("argument1=value1, argument2=value2")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "argument2"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_mixed_arguments():
    text_buffer = TextBuffer("value1, value2,argument1=value1, argument2=value2")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "argument2"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_quotes():
    text_buffer = TextBuffer('argument1="value1,value2"')
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.LITERAL, ","),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_spaces():
    text_buffer = TextBuffer("argument1=value1 value2")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "value2"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_quotes():
    text_buffer = TextBuffer(r"Argument \"with\" quotes")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "Argument"),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.TEXT, "with"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.WHITESPACE, " "),
        Token(TokenTypes.TEXT, "quotes"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_context():
    text_buffer = TextBuffer("argument1=value1")
    lex = ArgumentsLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "argument1"),
        Token(TokenTypes.LITERAL, "="),
        Token(TokenTypes.TEXT, "value1"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]

    assert [t.context for t in lex.tokens] == [
        Context(line=0, column=0, source=None, text="argument1=value1"),
        Context(line=0, column=9, source=None, text="argument1=value1"),
        Context(line=0, column=10, source=None, text="argument1=value1"),
        Context(line=0, column=16, source=None, text="argument1=value1"),
        Context(line=1, column=0, source=None),
    ]
