import textwrap

from mau.lexers.base_lexer import Text, Literal, EOL, EOF, WS
from mau.lexers.main_lexer import MainLexer


def dedent(text):
    return textwrap.dedent(text).strip()


def test_empty_text():
    lex = MainLexer()

    lex.process("")

    assert lex.tokens == [EOL, EOF]


def test_empty_lines():
    lex = MainLexer()

    lex.process("\n")

    assert lex.tokens == [EOL, EOL, EOF]


def test_lines_with_only_spaces():
    lex = MainLexer()

    lex.process("      \n      ")

    assert lex.tokens == [EOL, EOL, EOF]


def test_horizontal_rule():
    lex = MainLexer()

    lex.process("---")

    assert lex.tokens == [Literal("---"), EOL, EOF]


def test_attributes():
    lex = MainLexer()

    lex.process("[name]")

    assert lex.tokens == [
        Literal("["),
        Text("name"),
        Literal("]"),
        EOL,
        EOF,
    ]


def test_attributes_marker_in_text():
    lex = MainLexer()

    lex.process("Not [attributes]")

    assert lex.tokens == [
        Text("Not [attributes]"),
        EOL,
        EOF,
    ]


def test_variable_definition():
    lex = MainLexer()

    lex.process(":variable:value123")

    assert lex.tokens == [
        Literal(":"),
        Text("variable"),
        Literal(":"),
        Text("value123"),
        EOL,
        EOF,
    ]


def test_variable_negation():
    lex = MainLexer()

    lex.process(":!variable:")

    assert lex.tokens == [
        Literal(":"),
        Text("!variable"),
        Literal(":"),
        EOL,
        EOF,
    ]


def test_variable_marker_in_text():
    lex = MainLexer()

    lex.process("Not a :variable:")

    assert lex.tokens == [
        Text("Not a :variable:"),
        EOL,
        EOF,
    ]


def test_variable_definition_accepted_characters():
    lex = MainLexer()

    lex.process(":abcAB.C0123-_:value123")

    assert lex.tokens == [
        Literal(":"),
        Text("abcAB.C0123-_"),
        Literal(":"),
        Text("value123"),
        EOL,
        EOF,
    ]


def test_multiple_lines():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            This is text
            split into multiple lines

            with an empty line
            """
        )
    )

    assert lex.tokens == [
        Text("This is text"),
        EOL,
        Text("split into multiple lines"),
        EOL,
        EOL,
        Text("with an empty line"),
        EOL,
        EOF,
    ]


def test_multiple_lines_poistions():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            This is text
            split into multiple lines

            with an empty line
            """
        )
    )

    assert [i.position for i in lex.tokens] == [
        (0, 0),
        (0, 12),
        (1, 0),
        (1, 25),
        (2, 0),
        (3, 0),
        (3, 18),
        (4, 0),
    ]


def test_title():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            .A title
            Some text
            """
        )
    )

    assert lex.tokens == [
        Literal("."),
        Text("A title"),
        EOL,
        Text("Some text"),
        EOL,
        EOF,
    ]


def test_title_with_space():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            . A title
            Some text
            """
        )
    )

    assert lex.tokens == [
        Literal("."),
        WS(" "),
        Text("A title"),
        EOL,
        Text("Some text"),
        EOL,
        EOF,
    ]


def test_title_multiple_spaces_after_mark():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            .     A title with spaces
            Some text
            """
        )
    )

    assert lex.tokens == [
        Literal("."),
        WS("     "),
        Text("A title with spaces"),
        EOL,
        Text("Some text"),
        EOL,
        EOF,
    ]


def test_id():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            #someid
            Some text
            """
        )
    )

    assert lex.tokens == [
        Literal("#"),
        Text("someid"),
        EOL,
        Text("Some text"),
        EOL,
        EOF,
    ]


def test_command():
    lex = MainLexer()

    lex.process("::command:arg0,arg1")

    assert lex.tokens == [
        Literal("::"),
        Text("command"),
        Literal(":"),
        Text("arg0,arg1"),
        EOL,
        EOF,
    ]


def test_command_without_arguments():
    lex = MainLexer()

    lex.process("::command:")

    assert lex.tokens == [
        Literal("::"),
        Text("command"),
        Literal(":"),
        EOL,
        EOF,
    ]


def test_comment():
    lex = MainLexer()

    lex.process("// Some comment")

    assert lex.tokens == [
        Text("// Some comment"),
        EOL,
        EOF,
    ]


def test_multiline_comment():
    lex = MainLexer()

    lex.process(
        dedent(
            """
            ////
            Some comment

               another line
            ////
            """
        )
    )

    assert lex.tokens == [
        Literal("////"),
        EOL,
        Text("Some comment"),
        EOL,
        EOL,
        Text("   another line"),
        EOL,
        Literal("////"),
        EOL,
        EOF,
    ]


def test_include_content():
    lex = MainLexer()

    lex.process("<< type:/path/to/it.jpg")

    assert lex.tokens == [
        Literal("<<"),
        WS(" "),
        Text("type:/path/to/it.jpg"),
        EOL,
        EOF,
    ]


def test_include_content_multiple_spaces_after_mark():
    lex = MainLexer()

    lex.process("<<      type:/path/to/it.jpg")

    assert lex.tokens == [
        Literal("<<"),
        WS("      "),
        Text("type:/path/to/it.jpg"),
        EOL,
        EOF,
    ]


def test_include_content_positions():
    lex = MainLexer()

    lex.process("<< type:/path/to/it.jpg")

    assert [i.position for i in lex.tokens] == [
        (0, 0),
        (0, 2),
        (0, 3),
        (0, 23),
        (1, 0),
    ]


def test_include_content_with_arguments():
    lex = MainLexer()

    lex.process("<< type:/path/to/it.jpg(value1,argument2=value2)")

    assert lex.tokens == [
        Literal("<<"),
        WS(" "),
        Text("type:/path/to/it.jpg"),
        Literal("("),
        Text("value1,argument2=value2"),
        Literal(")"),
        EOL,
        EOF,
    ]


def test_unordered_list():
    lex = MainLexer()

    lex.process("* Item")

    assert lex.tokens == [
        Literal("*"),
        WS(" "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_unordered_list_leading_space():
    lex = MainLexer()

    lex.process("    * Item")

    assert lex.tokens == [
        WS("    "),
        Literal("*"),
        WS(" "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_unordered_list_trailing_space():
    lex = MainLexer()

    lex.process("*       Item")

    assert lex.tokens == [
        Literal("*"),
        WS("       "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_unordered_list_multiple_stars():
    lex = MainLexer()

    lex.process("*** Item")

    assert lex.tokens == [
        Literal("***"),
        WS(" "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_ordered_list():
    lex = MainLexer()

    lex.process("# Item")

    assert lex.tokens == [
        Literal("#"),
        WS(" "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_ordered_list_multiple_stars():
    lex = MainLexer()

    lex.process("### Item")

    assert lex.tokens == [
        Literal("###"),
        WS(" "),
        Text("Item"),
        EOL,
        EOF,
    ]


def test_header():
    lex = MainLexer()

    lex.process("= Header")

    assert lex.tokens == [
        Literal("="),
        WS(" "),
        Text("Header"),
        EOL,
        EOF,
    ]


def test_header_multiple_spaces_after_mark():
    lex = MainLexer()

    lex.process("=    Header")

    assert lex.tokens == [
        Literal("="),
        WS("    "),
        Text("Header"),
        EOL,
        EOF,
    ]


def test_empty_header():
    lex = MainLexer()

    lex.process("=")

    assert lex.tokens == [
        Text("="),
        EOL,
        EOF,
    ]


def test_multiple_header_markers():
    lex = MainLexer()

    lex.process("=== Header")

    assert lex.tokens == [
        Literal("==="),
        WS(" "),
        Text("Header"),
        EOL,
        EOF,
    ]


def test_header_marker_in_header_text():
    lex = MainLexer()

    lex.process("= a=b")

    assert lex.tokens == [
        Literal("="),
        WS(" "),
        Text("a=b"),
        EOL,
        EOF,
    ]


def test_header_markers_in_text():
    lex = MainLexer()

    lex.process("Definitely not a === header")

    assert lex.tokens == [
        Text("Definitely not a === header"),
        EOL,
        EOF,
    ]


def test_unlisted_header():
    lex = MainLexer()

    lex.process("==! Header")

    assert lex.tokens == [
        Literal("==!"),
        WS(" "),
        Text("Header"),
        EOL,
        EOF,
    ]
