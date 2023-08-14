from unittest.mock import mock_open, patch

from mau.lexers.base_lexer import TokenTypes as BLTokenTypes
from mau.lexers.main_lexer import MainLexer, TokenTypes
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token

from tests.helpers import dedent


def test_empty_text():
    text_buffer = TextBuffer("")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == []


def test_empty_lines():
    text_buffer = TextBuffer("\n")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [Token(BLTokenTypes.EOL), Token(BLTokenTypes.EOL)]


def test_lines_with_only_spaces():
    text_buffer = TextBuffer("      \n      ")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [Token(BLTokenTypes.EOL), Token(BLTokenTypes.EOL)]


def test_horizontal_rule():
    text_buffer = TextBuffer("---")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.HORIZONTAL_RULE, "---"),
        Token(BLTokenTypes.EOL),
    ]


def test_escape_line():
    text_buffer = TextBuffer(r"\[name]")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, r"\[name]"),
        Token(BLTokenTypes.EOL),
    ]


def test_escape_line_beginning_with_backslash():
    text_buffer = TextBuffer(r"\\[name]")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, r"\\[name]"),
        Token(BLTokenTypes.EOL),
    ]


def test_arguments():
    text_buffer = TextBuffer("[name]")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.ARGUMENTS, "["),
        Token(BLTokenTypes.TEXT, "name"),
        Token(BLTokenTypes.LITERAL, "]"),
        Token(BLTokenTypes.EOL),
    ]


def test_attributes_no_closing_bracket():
    text_buffer = TextBuffer("[name")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "[name"),
        Token(BLTokenTypes.EOL),
    ]


def test_attributes_marker_in_text():
    text_buffer = TextBuffer("Not [attributes]")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Not [attributes]"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "Not [attributes]"),
        Context(0, 16, None, "Not [attributes]"),
    ]


def test_variable_definition():
    text_buffer = TextBuffer(":variable:value123")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "variable"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "value123"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ":variable:value123"),
        Context(0, 1, None, ":variable:value123"),
        Context(0, 9, None, ":variable:value123"),
        Context(0, 10, None, ":variable:value123"),
        Context(0, 18, None, ":variable:value123"),
    ]


def test_variable_negation():
    text_buffer = TextBuffer(":!variable:")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "!variable"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
    ]


def test_variable_marker_in_text():
    text_buffer = TextBuffer("Not a :variable:")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Not a :variable:"),
        Token(BLTokenTypes.EOL),
    ]


def test_variable_definition_accepted_characters():
    text_buffer = TextBuffer(":abcAB.C0123-_:value123")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.VARIABLE, ":"),
        Token(BLTokenTypes.TEXT, "abcAB.C0123-_"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "value123"),
        Token(BLTokenTypes.EOL),
    ]


def test_multiple_lines():
    text_buffer = TextBuffer(
        dedent(
            """
            This is text
            split into multiple lines

            with an empty line
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "This is text"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "split into multiple lines"),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.EOL),
        Token(BLTokenTypes.TEXT, "with an empty line"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "This is text"),
        Context(0, 12, None, "This is text"),
        Context(1, 0, None, "split into multiple lines"),
        Context(1, 25, None, "split into multiple lines"),
        Context(2, 0, None, ""),
        Context(3, 0, None, "with an empty line"),
        Context(3, 18, None, "with an empty line"),
    ]


def test_title():
    text_buffer = TextBuffer(".A title")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TITLE, "."),
        Token(BLTokenTypes.TEXT, "A title"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ".A title"),
        Context(0, 1, None, ".A title"),
        Context(0, 8, None, ".A title"),
    ]


def test_title_with_space():
    text_buffer = TextBuffer(".      A title")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TITLE, "."),
        Token(BLTokenTypes.WHITESPACE, "      "),
        Token(BLTokenTypes.TEXT, "A title"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, ".      A title"),
        Context(0, 1, None, ".      A title"),
        Context(0, 7, None, ".      A title"),
        Context(0, 14, None, ".      A title"),
    ]


def test_command():
    text_buffer = TextBuffer("::command:arg0,arg1")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.COMMAND, "::"),
        Token(BLTokenTypes.TEXT, "command"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "arg0,arg1"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "::command:arg0,arg1"),
        Context(0, 2, None, "::command:arg0,arg1"),
        Context(0, 9, None, "::command:arg0,arg1"),
        Context(0, 10, None, "::command:arg0,arg1"),
        Context(0, 19, None, "::command:arg0,arg1"),
    ]


def test_command_without_arguments():
    text_buffer = TextBuffer("::command:")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.COMMAND, "::"),
        Token(BLTokenTypes.TEXT, "command"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
    ]


def test_comment():
    text_buffer = TextBuffer("// Some comment")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.COMMENT, "// Some comment"),
        Token(BLTokenTypes.EOL),
    ]


def test_multiline_comment():
    text_buffer = TextBuffer(
        dedent(
            """
            ////
            Some comment

               another line
            ////
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

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
    ]


def test_include_content():
    text_buffer = TextBuffer("<<type:/path/to/it.jpg")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.INCLUDE, "<<"),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "/path/to/it.jpg"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<type:/path/to/it.jpg"),
        Context(0, 2, None, "<<type:/path/to/it.jpg"),
        Context(0, 6, None, "<<type:/path/to/it.jpg"),
        Context(0, 7, None, "<<type:/path/to/it.jpg"),
        Context(0, 22, None, "<<type:/path/to/it.jpg"),
    ]


def test_include_content_with_space():
    text_buffer = TextBuffer("<<      type:/path/to/it.jpg")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.INCLUDE, "<<"),
        Token(BLTokenTypes.WHITESPACE, "      "),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.TEXT, "/path/to/it.jpg"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<      type:/path/to/it.jpg"),
        Context(0, 2, None, "<<      type:/path/to/it.jpg"),
        Context(0, 8, None, "<<      type:/path/to/it.jpg"),
        Context(0, 12, None, "<<      type:/path/to/it.jpg"),
        Context(0, 13, None, "<<      type:/path/to/it.jpg"),
        Context(0, 28, None, "<<      type:/path/to/it.jpg"),
    ]


def test_include_content_without_arguments():
    text_buffer = TextBuffer("<<type:")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.INCLUDE, "<<"),
        Token(BLTokenTypes.TEXT, "type"),
        Token(BLTokenTypes.LITERAL, ":"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "<<type:"),
        Context(0, 2, None, "<<type:"),
        Context(0, 6, None, "<<type:"),
        Context(0, 7, None, "<<type:"),
    ]


def test_unordered_list():
    text_buffer = TextBuffer("* Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "* Item"),
        Context(0, 1, None, "* Item"),
        Context(0, 2, None, "* Item"),
        Context(0, 6, None, "* Item"),
    ]


def test_unordered_list_leading_space():
    text_buffer = TextBuffer("    * Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.WHITESPACE, "    "),
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]


def test_unordered_list_trailing_space():
    text_buffer = TextBuffer("*       Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LIST, "*"),
        Token(BLTokenTypes.WHITESPACE, "       "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]


def test_unordered_list_multiple_stars():
    text_buffer = TextBuffer("*** Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LIST, "***"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]


def test_ordered_list():
    text_buffer = TextBuffer("# Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LIST, "#"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]


def test_ordered_list_multiple_stars():
    text_buffer = TextBuffer("### Item")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LIST, "###"),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Item"),
        Token(BLTokenTypes.EOL),
    ]


def test_header():
    text_buffer = TextBuffer("=Header")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "=Header"),
        Context(0, 1, None, "=Header"),
        Context(0, 7, None, "=Header"),
    ]


def test_header_with_space():
    text_buffer = TextBuffer("=    Header")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.WHITESPACE, "    "),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
    ]


def test_empty_header():
    text_buffer = TextBuffer("=")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "="),
        Token(BLTokenTypes.EOL),
    ]


def test_multiple_header_markers():
    text_buffer = TextBuffer("=== Header")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "==="),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "Header"),
        Token(BLTokenTypes.EOL),
    ]


def test_header_marker_in_header_text():
    text_buffer = TextBuffer("= a=b")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.HEADER, "="),
        Token(BLTokenTypes.WHITESPACE, " "),
        Token(BLTokenTypes.TEXT, "a=b"),
        Token(BLTokenTypes.EOL),
    ]


def test_header_markers_in_text():
    text_buffer = TextBuffer("Definitely not a === header")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "Definitely not a === header"),
        Token(BLTokenTypes.EOL),
    ]


@patch("mau.lexers.main_lexer.MainLexer._run_directive")
def test_directive(mock_run_directive):
    text_buffer = TextBuffer("::#name:/path/to/file")
    lex = MainLexer(text_buffer)
    lex.process()

    assert mock_run_directive.called_with("name", "/path/to/file")


@patch("builtins.open", new_callable=mock_open, read_data="just some data")
def test_import_directive(mock_file):  # pylint: disable=unused-argument
    text_buffer = TextBuffer("::#include:/path/to/file")
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "just some data"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, "/path/to/file", "just some data"),
        Context(0, 14, "/path/to/file", "just some data"),
    ]


def test_block():
    text_buffer = TextBuffer(
        dedent(
            """
            ----
            Some comment

               another line
            ----
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

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
    ]


def test_block_four_characters():
    text_buffer = TextBuffer(
        dedent(
            """
            ####
            Some comment

               another line
            ####
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

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
    ]


def test_block_with_comment():
    text_buffer = TextBuffer(
        dedent(
            """
            ----
            // Comment
            ----
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.COMMENT, "// Comment"),
        Token(BLTokenTypes.EOL),
        Token(TokenTypes.BLOCK, "----"),
        Token(BLTokenTypes.EOL),
    ]

    assert [i.context for i in lex.tokens] == [
        Context(0, 0, None, "----"),
        Context(0, 4, None, "----"),
        Context(1, 0, None, "// Comment"),
        Context(1, 10, None, "// Comment"),
        Context(2, 0, None, "----"),
        Context(2, 4, None, "----"),
    ]


def test_block_has_to_begin_with_four_identical_characters():
    text_buffer = TextBuffer(
        dedent(
            """
            abcd
            """
        )
    )
    lex = MainLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(BLTokenTypes.TEXT, "abcd"),
        Token(BLTokenTypes.EOL),
    ]
