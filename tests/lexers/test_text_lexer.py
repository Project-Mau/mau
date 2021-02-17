from mau.lexers.base_lexer import Text, Literal, EOL, EOF
from mau.lexers.text_lexer import TextLexer


def test_normal_text():
    lex = TextLexer()

    lex.process("Normal text")

    assert lex.tokens == [
        Text("Normal"),
        Text(" "),
        Text("text"),
        EOL,
        EOF,
    ]


def test_underscore():
    lex = TextLexer()

    lex.process("_underscore_")

    assert lex.tokens == [
        Literal("_"),
        Text("underscore"),
        Literal("_"),
        EOL,
        EOF,
    ]


def test_star():
    lex = TextLexer()

    lex.process("*star*")

    assert lex.tokens == [
        Literal("*"),
        Text("star"),
        Literal("*"),
        EOL,
        EOF,
    ]


def test_backtick():
    lex = TextLexer()

    lex.process("`backtick`")

    assert lex.tokens == [
        Literal("`"),
        Text("backtick"),
        Literal("`"),
        EOL,
        EOF,
    ]


def test_curly_braces():
    lex = TextLexer()

    lex.process("{curly}")

    assert lex.tokens == [
        Literal("{"),
        Text("curly"),
        Literal("}"),
        EOL,
        EOF,
    ]


def test_round_brackets():
    lex = TextLexer()

    lex.process("(round)")

    assert lex.tokens == [
        Literal("("),
        Text("round"),
        Literal(")"),
        EOL,
        EOF,
    ]


def test_square_brackets():
    lex = TextLexer()

    lex.process("[square]")

    assert lex.tokens == [
        Literal("["),
        Text("square"),
        Literal("]"),
        EOL,
        EOF,
    ]


def test_single_class():
    lex = TextLexer()

    lex.process("[name]#content#")

    assert lex.tokens == [
        Literal("["),
        Text("name"),
        Literal("]"),
        Literal("#"),
        Text("content"),
        Literal("#"),
        EOL,
        EOF,
    ]


def test_multiple_classes():
    lex = TextLexer()

    lex.process("[name1,name2]#content#")

    assert lex.tokens == [
        Literal("["),
        Text("name1,name2"),
        Literal("]"),
        Literal("#"),
        Text("content"),
        Literal("#"),
        EOL,
        EOF,
    ]


def test_class_content_with_styles():
    lex = TextLexer()

    lex.process("[name]#_content_#")

    assert lex.tokens == [
        Literal("["),
        Text("name"),
        Literal("]"),
        Literal("#"),
        Literal("_"),
        Text("content"),
        Literal("_"),
        Literal("#"),
        EOL,
        EOF,
    ]


def test_macro():
    lex = TextLexer()

    lex.process("[macro](value1,value2)")

    assert lex.tokens == [
        Literal("["),
        Text("macro"),
        Literal("]"),
        Literal("("),
        Text("value1,value2"),
        Literal(")"),
        EOL,
        EOF,
    ]


def test_macro_named_attributes():
    lex = TextLexer()

    lex.process("[macro](attr1=value1,attr2=value2)")

    assert lex.tokens == [
        Literal("["),
        Text("macro"),
        Literal("]"),
        Literal("("),
        Text("attr1=value1,attr2=value2"),
        Literal(")"),
        EOL,
        EOF,
    ]


def test_escaped_underscore():
    lex = TextLexer()

    lex.process(r"\_underscore\_")

    # Escaped characters are TEXT tokens, not LITERAL
    assert lex.tokens == [
        Literal("\\"),
        Literal("_"),
        Text("underscore"),
        Literal("\\"),
        Literal("_"),
        EOL,
        EOF,
    ]


def test_escaped_square_brackets():
    lex = TextLexer()

    lex.process(r"\[square\]")

    # Escaped characters are TEXT tokens, not LITERAL
    assert lex.tokens == [
        Literal("\\"),
        Literal("["),
        Text("square"),
        Literal("\\"),
        Literal("]"),
        EOL,
        EOF,
    ]


def test_escaped_round_brackets():
    lex = TextLexer()

    lex.process(r"\(round\)")

    # Escaped characters are TEXT tokens, not LITERAL
    assert lex.tokens == [
        Literal("\\"),
        Literal("("),
        Text("round"),
        Literal("\\"),
        Literal(")"),
        EOL,
        EOF,
    ]


def test_escaped_curly_braces():
    lex = TextLexer()

    lex.process(r"\{curly\}")

    # Escaped characters are TEXT tokens, not LITERAL
    assert lex.tokens == [
        Literal("\\"),
        Literal("{"),
        Text("curly"),
        Literal("\\"),
        Literal("}"),
        EOL,
        EOF,
    ]


def test_escaped_quotes():
    lex = TextLexer()

    lex.process(r"\"quotes\"")

    assert lex.tokens == [
        Literal("\\"),
        Literal('"'),
        Text("quotes"),
        Literal("\\"),
        Literal('"'),
        EOL,
        EOF,
    ]
