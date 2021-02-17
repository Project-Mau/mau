from mau.lexers.base_lexer import Token, TokenTypes, Text, Literal, EOL, EOF
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer


def test_normal_text():
    lex = PreprocessVariablesLexer()

    lex.process("Some text")

    assert lex.tokens == [
        Text("S"),
        Text("o"),
        Text("m"),
        Text("e"),
        Text(" "),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text("\n"),
    ]


def test_match_only_backticks_and_curly_braces():
    lex = PreprocessVariablesLexer()

    lex.process("Normal text `{curly}` _other_ *text*")

    assert lex.tokens == [
        Text("N"),
        Text("o"),
        Text("r"),
        Text("m"),
        Text("a"),
        Text("l"),
        Text(" "),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text(" "),
        Literal("`"),
        Literal("{"),
        Text("c"),
        Text("u"),
        Text("r"),
        Text("l"),
        Text("y"),
        Literal("}"),
        Literal("`"),
        Text(" "),
        Text("_"),
        Text("o"),
        Text("t"),
        Text("h"),
        Text("e"),
        Text("r"),
        Text("_"),
        Text(" "),
        Text("*"),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text("*"),
        Text("\n"),
    ]


def test_escape_curly_braces():
    lex = PreprocessVariablesLexer()

    lex.process(r"Normal text \{curly\} _other_ *text*")

    assert lex.tokens == [
        Text("N"),
        Text("o"),
        Text("r"),
        Text("m"),
        Text("a"),
        Text("l"),
        Text(" "),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text(" "),
        Literal("\\"),
        Literal("{"),
        Text("c"),
        Text("u"),
        Text("r"),
        Text("l"),
        Text("y"),
        Literal("\\"),
        Literal("}"),
        Text(" "),
        Text("_"),
        Text("o"),
        Text("t"),
        Text("h"),
        Text("e"),
        Text("r"),
        Text("_"),
        Text(" "),
        Text("*"),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text("*"),
        Text("\n"),
    ]


def test_preserve_escapes():
    lex = PreprocessVariablesLexer()

    lex.process(r"Normal \text \_other\_")

    assert lex.tokens == [
        Text("N"),
        Text("o"),
        Text("r"),
        Text("m"),
        Text("a"),
        Text("l"),
        Text(" "),
        Literal("\\"),
        Text("t"),
        Text("e"),
        Text("x"),
        Text("t"),
        Text(" "),
        Literal("\\"),
        Text("_"),
        Text("o"),
        Text("t"),
        Text("h"),
        Text("e"),
        Text("r"),
        Literal("\\"),
        Text("_"),
        Text("\n"),
    ]
