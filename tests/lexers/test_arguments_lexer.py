from mau.lexers.base_lexer import Text, Literal, WS
from mau.lexers.arguments_lexer import ArgumentsLexer


def test_single_unnamed_argument():
    lex = ArgumentsLexer()

    lex.process("value1")

    assert lex.tokens == [
        Text("value1"),
    ]


def test_single_named_argument():
    lex = ArgumentsLexer()

    lex.process("argument1=value1")

    assert lex.tokens == [
        Text("argument1"),
        Literal("="),
        Text("value1"),
    ]


def test_multiple_unnamed_arguments():
    lex = ArgumentsLexer()

    lex.process("value1, value2")

    assert lex.tokens == [
        Text("value1"),
        Literal(","),
        WS(" "),
        Text("value2"),
    ]


def test_multiple_named_arguments():
    lex = ArgumentsLexer()

    lex.process("argument1=value1, argument2=value2")

    assert lex.tokens == [
        Text("argument1"),
        Literal("="),
        Text("value1"),
        Literal(","),
        WS(" "),
        Text("argument2"),
        Literal("="),
        Text("value2"),
    ]


def test_mixed_arguments():
    lex = ArgumentsLexer()

    lex.process("value1, value2,argument1=value1, argument2=value2")

    assert lex.tokens == [
        Text("value1"),
        Literal(","),
        WS(" "),
        Text("value2"),
        Literal(","),
        Text("argument1"),
        Literal("="),
        Text("value1"),
        Literal(","),
        WS(" "),
        Text("argument2"),
        Literal("="),
        Text("value2"),
    ]


def test_quotes():
    lex = ArgumentsLexer()

    lex.process('argument1="value1,value2"')

    assert lex.tokens == [
        Text("argument1"),
        Literal("="),
        Literal('"'),
        Text("value1"),
        Literal(","),
        Text("value2"),
        Literal('"'),
    ]

    assert [t.position for t in lex.tokens] == [
        (0, 0),
        (0, 9),
        (0, 10),
        (0, 11),
        (0, 17),
        (0, 18),
        (0, 24),
    ]


def test_spaces():
    lex = ArgumentsLexer()

    lex.process("argument1=value1 value2")

    assert lex.tokens == [
        Text("argument1"),
        Literal("="),
        Text("value1"),
        WS(" "),
        Text("value2"),
    ]


def test_escaped_quotes():
    lex = ArgumentsLexer()

    lex.process(r"Argument \"with\" quotes")

    assert lex.tokens == [
        Text("Argument"),
        WS(" "),
        Literal("\\"),
        Literal('"'),
        Text("with"),
        Literal("\\"),
        Literal('"'),
        WS(" "),
        Text("quotes"),
    ]
