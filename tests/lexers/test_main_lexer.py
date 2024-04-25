from unittest.mock import mock_open, patch

from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.lexers.main_lexer import MainLexer, TokenTypes
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token

from tests.helpers import dedent, init_lexer_factory, lexer_runner_factory

init_lexer = init_lexer_factory(MainLexer)

runner = lexer_runner_factory(MainLexer)


def test_empty_text():
    lex = runner("")

    assert lex.tokens == [
        Token(BLTokenTypes.EOF),
    ]


def test_empty_lines():
    lex = runner("\n")

    assert lex.tokens == [
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_lines_with_only_spaces():
    lex = runner("      \n      ")

    assert lex.tokens == [
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_horizontal_rule():
    lex = runner("---")

    assert lex.tokens == [
        Token(TokenTypes.HORIZONTAL_RULE, "---"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_escape_line():
    lex = runner(r"\[name]")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, r"\[name]"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_escape_line_beginning_with_backslash():
    lex = runner(r"\\[name]")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, r"\\[name]"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_arguments():
    lex = runner("[name]")

    assert lex.tokens == [
        Token(TokenTypes.ARGUMENTS, "["),
        Token(BLTokenTypes.TEXT, "name"),
        Token(BLTokenTypes.LITERAL, "]"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_attributes_no_closing_bracket():
    lex = runner("[name")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "[name"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_attributes_marker_in_text():
    lex = runner("Not [attributes]")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Not [attributes]"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "Not [attributes]"),
        Context(0, 16, None, "Not [attributes]"),
        Context(1, 0, None, ""),
    ]


def test_variable_definition():
    lex = runner(":variable:value123")

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "variable"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "value123"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ":variable:value123"),
        Context(0, 1, None, ":variable:value123"),
        Context(0, 9, None, ":variable:value123"),
        Context(0, 10, None, ":variable:value123"),
        Context(0, 18, None, ":variable:value123"),
        Context(1, 0, None, ""),
    ]


def test_variable_flag_true():
    lex = runner(":+variable:")

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "+variable"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_variable_flag_false():
    lex = runner(":-variable:")

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "-variable"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_variable_marker_in_text():
    lex = runner("Not a :variable:")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Not a :variable:"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_variable_definition_accepted_characters():
    lex = runner(":abcAB.C0123-_:value123")

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "abcAB.C0123-_"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "value123"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_multiple_lines():
    lex = runner(
        dedent(
            """
            This is text
            split into multiple lines

            with an empty line
            """
        )
    )

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "This is text"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "split into multiple lines"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "with an empty line"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "This is text"),
        Context(0, 12, None, "This is text"),
        Context(1, 0, None, "split into multiple lines"),
        Context(1, 25, None, "split into multiple lines"),
        Context(2, 0, None, ""),
        Context(3, 0, None, "with an empty line"),
        Context(3, 18, None, "with an empty line"),
        Context(4, 0, None, ""),
    ]


def test_title():
    lex = runner(".A title")

    assert lex.tokens == [
        Token(TokenTypes.TITLE, "."),
        Token(BLTokenTypes.TEXT, "A title"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ".A title"),
        Context(0, 1, None, ".A title"),
        Context(0, 8, None, ".A title"),
        Context(1, 0, None, ""),
    ]


def test_title_with_space():
    lex = runner(".      A title")

    assert lex.tokens == [
        Token(TokenTypes.TITLE, "."),
        Token(BLTokenTypes.WHITESPACE, "      "),
        Token(BLTokenTypes.TEXT, "A title"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ".      A title"),
        Context(0, 1, None, ".      A title"),
        Context(0, 7, None, ".      A title"),
        Context(0, 14, None, ".      A title"),
        Context(1, 0, None, ""),
    ]


def test_command():
    lex = runner("::command:arg0,arg1")

    assert lex.tokens == [
        Token(TokenTypes.COMMAND, "::"),
        Token(BLTokenTypes.TEXT, "command"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "arg0,arg1"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "::command:arg0,arg1"),
        Context(0, 2, None, "::command:arg0,arg1"),
        Context(0, 9, None, "::command:arg0,arg1"),
        Context(0, 10, None, "::command:arg0,arg1"),
        Context(0, 19, None, "::command:arg0,arg1"),
        Context(1, 0, None, ""),
    ]


def test_command_without_arguments():
    lex = runner("::command:")

    assert lex.tokens == [
        Token(TokenTypes.COMMAND, "::"),
        Token(BLTokenTypes.TEXT, "command"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_comment():
    lex = runner("// Some comment")

    assert lex.tokens == [
        Token(TokenTypes.COMMENT, "// Some comment"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_multiline_comment():
    lex = runner(
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
        Token(TokenTypes.MULTILINE_COMMENT, "////"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "Some comment"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "   another line"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.MULTILINE_COMMENT, "////"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "////"),
        Context(0, 4, None, "////"),
        Context(1, 0, None, "Some comment"),
        Context(1, 12, None, "Some comment"),
        Context(2, 0, None, ""),
        Context(3, 0, None, "   another line"),
        Context(3, 15, None, "   another line"),
        Context(4, 0, None, "////"),
        Context(4, 4, None, "////"),
        Context(5, 0, None, ""),
    ]


def test_include_content():
    lex = runner("<<type:/path/to/it.jpg")

    assert lex.tokens == [
        Token(TokenTypes.CONTENT, "<<"),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "/path/to/it.jpg"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<type:/path/to/it.jpg"),
        Context(0, 2, None, "<<type:/path/to/it.jpg"),
        Context(0, 6, None, "<<type:/path/to/it.jpg"),
        Context(0, 7, None, "<<type:/path/to/it.jpg"),
        Context(0, 22, None, "<<type:/path/to/it.jpg"),
        Context(1, 0, None, ""),
    ]


def test_include_content_with_space():
    lex = runner("<<      type:/path/to/it.jpg")

    assert lex.tokens == [
        Token(TokenTypes.CONTENT, "<<"),
        Token(BLTokenTypes.WHITESPACE, "      "),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "/path/to/it.jpg"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<      type:/path/to/it.jpg"),
        Context(0, 2, None, "<<      type:/path/to/it.jpg"),
        Context(0, 8, None, "<<      type:/path/to/it.jpg"),
        Context(0, 12, None, "<<      type:/path/to/it.jpg"),
        Context(0, 13, None, "<<      type:/path/to/it.jpg"),
        Context(0, 28, None, "<<      type:/path/to/it.jpg"),
        Context(1, 0, None, ""),
    ]


def test_include_content_without_arguments():
    lex = runner("<<type:")

    assert lex.tokens == [
        Token(TokenTypes.CONTENT, "<<"),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<type:"),
        Context(0, 2, None, "<<type:"),
        Context(0, 6, None, "<<type:"),
        Context(0, 7, None, "<<type:"),
        Context(1, 0, None, ""),
    ]


def test_unordered_list():
    lex = runner("* Item")

    assert lex.tokens == [
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "* Item"),
        Context(0, 1, None, "* Item"),
        Context(0, 2, None, "* Item"),
        Context(0, 6, None, "* Item"),
        Context(1, 0, None, ""),
    ]


def test_unordered_list_leading_space():
    text_buffer = TextBuffer("    * Item")
    lex = init_lexer()
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(BLTokenTypes.WHITESPACE, "    "),
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_unordered_list_trailing_space():
    lex = runner("*       Item")

    assert lex.tokens == [
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, "       "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_unordered_list_multiple_stars():
    lex = runner("*** Item")

    assert lex.tokens == [
        Token(TokenTypes.LIST, "***"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_ordered_list():
    lex = runner("# Item")

    assert lex.tokens == [
        Token(TokenTypes.LIST, "#"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_ordered_list_multiple_stars():
    lex = runner("### Item")

    assert lex.tokens == [
        Token(TokenTypes.LIST, "###"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_header():
    lex = runner("=Header")

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "=Header"),
        Context(0, 1, None, "=Header"),
        Context(0, 7, None, "=Header"),
        Context(1, 0, None, ""),
    ]


def test_header_with_space():
    lex = runner("=    Header")

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.WHITESPACE, "    "),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_empty_header():
    lex = runner("=")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "="),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_multiple_header_markers():
    lex = runner("=== Header")

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "==="),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_header_marker_in_header_text():
    lex = runner("= a=b")

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "a=b"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_header_markers_in_text():
    lex = runner("Definitely not a === header")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Definitely not a === header"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


@patch("mau.lexers.main_lexer.MainLexer._run_directive")
def test_directive(mock_run_directive):
    runner("::#name:/path/to/file")

    assert mock_run_directive.called_with("name", "/path/to/file")


@patch("builtins.open", new_callable=mock_open, read_data="just some data")
def test_import_directive(mock_file):  # pylint: disable=unused-argument
    lex = runner("::#include:/path/to/file")

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "just some data"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, "/path/to/file", "just some data"),
        Context(0, 14, "/path/to/file", "just some data"),
        Context(1, 0, None),
    ]


def test_block():
    lex = runner(
        dedent(
            """
            ----
            Some comment

               another line
            ----
            """
        )
    )

    assert lex.tokens == [
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "Some comment"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "   another line"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "----"),
        Context(0, 4, None, "----"),
        Context(1, 0, None, "Some comment"),
        Context(1, 12, None, "Some comment"),
        Context(2, 0, None, ""),
        Context(3, 0, None, "   another line"),
        Context(3, 15, None, "   another line"),
        Context(4, 0, None, "----"),
        Context(4, 4, None, "----"),
        Context(5, 0, None, ""),
    ]


def test_block_four_characters():
    lex = runner(
        dedent(
            """
            ####
            Some comment

               another line
            ####
            """
        )
    )

    assert lex.tokens == [
        Token(TokenTypes.BLOCK, "####"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "Some comment"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "   another line"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.BLOCK, "####"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "####"),
        Context(0, 4, None, "####"),
        Context(1, 0, None, "Some comment"),
        Context(1, 12, None, "Some comment"),
        Context(2, 0, None, ""),
        Context(3, 0, None, "   another line"),
        Context(3, 15, None, "   another line"),
        Context(4, 0, None, "####"),
        Context(4, 4, None, "####"),
        Context(5, 0, None, ""),
    ]


def test_block_with_comment():
    lex = runner(
        dedent(
            """
            ----
            // Comment
            ----
            """
        )
    )

    assert lex.tokens == [
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.COMMENT, "// Comment"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "----"),
        Context(0, 4, None, "----"),
        Context(1, 0, None, "// Comment"),
        Context(1, 10, None, "// Comment"),
        Context(2, 0, None, "----"),
        Context(2, 4, None, "----"),
        Context(3, 0, None, ""),
    ]


def test_block_has_to_begin_with_four_identical_characters():
    lex = runner(
        dedent(
            """
            abcd
            """
        )
    )

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "abcd"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]


def test_conditional():
    lex = runner("@if:somevar:=value")

    assert lex.tokens == [
        Token(TokenTypes.CONTROL, "@"),
        Token(BLTokenTypes.TEXT, "if"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "somevar:=value"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "@if:somevar:=value"),
        Context(0, 1, None, "@if:somevar:=value"),
        Context(0, 3, None, "@if:somevar:=value"),
        Context(0, 4, None, "@if:somevar:=value"),
        Context(0, 18, None, "@if:somevar:=value"),
        Context(1, 0, None, ""),
    ]


def test_conditional_no_value():
    lex = runner("@if:somevar:")

    assert lex.tokens == [
        Token(TokenTypes.CONTROL, "@"),
        Token(BLTokenTypes.TEXT, "if"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "somevar:"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOF),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "@if:somevar:"),
        Context(0, 1, None, "@if:somevar:"),
        Context(0, 3, None, "@if:somevar:"),
        Context(0, 4, None, "@if:somevar:"),
        Context(0, 12, None, "@if:somevar:"),
        Context(1, 0, None, ""),
    ]
