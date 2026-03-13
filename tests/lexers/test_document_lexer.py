import pytest

from mau.lexers.base_lexer import TokenType
from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.test_helpers import (
    TEST_CONTEXT_SOURCE,
    compare_asdict_list,
    dedent,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.text_buffer import TextBuffer
from mau.token import Token

init_lexer = init_lexer_factory(DocumentLexer)

runner = lexer_runner_factory(DocumentLexer)


def test_horizontal_rule():
    lex = runner("---")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HORIZONTAL_RULE, "---", generate_context(0, 0, 0, 3)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_arguments():
    lex = runner("[name]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.ARGUMENTS, "[", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "name", generate_context(0, 1, 0, 5)),
            Token(TokenType.LITERAL, "]", generate_context(0, 5, 0, 6)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_arguments_no_closing_bracket():
    lex = runner("[name")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "[name", generate_context(0, 0, 0, 5)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_square_brackets_in_text():
    lex = runner("Not [arguments]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Not [arguments]", generate_context(0, 0, 0, 15)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_square_brackets_at_the_beginning():
    lex = runner("[not] arguments")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "[not] arguments", generate_context(0, 0, 0, 15)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_escape_line():
    lex = runner(r"\[name]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, r"\[name]", generate_context(0, 0, 0, 7)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_escape_line_beginning_with_backslash():
    lex = runner(r"\\[name]")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, r"\\[name]", generate_context(0, 0, 0, 8)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_definition():
    lex = runner(":variable:value123")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.VARIABLE, ":", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "variable", generate_context(0, 1, 0, 9)),
            Token(TokenType.LITERAL, ":", generate_context(0, 9, 0, 10)),
            Token(TokenType.TEXT, "value123", generate_context(0, 10, 0, 18)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_definition_without_arguments():
    lex = runner(":variable")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.VARIABLE, ":", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "variable", generate_context(0, 1, 0, 9)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_flag_true():
    lex = runner(":+variable")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.VARIABLE, ":", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "+variable", generate_context(0, 1, 0, 10)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_flag_false():
    lex = runner(":-variable")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.VARIABLE, ":", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "-variable", generate_context(0, 1, 0, 10)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_marker_in_text():
    lex = runner("Not a :variable:")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Not a :variable:", generate_context(0, 0, 0, 16)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_marker_with_space():
    lex = runner(": not a variable:")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, ": not a variable:", generate_context(0, 0, 0, 17)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_variable_definition_accepted_characters():
    lex = runner(":abcAB.C0123-_:value123")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.VARIABLE, ":", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "abcAB.C0123-_", generate_context(0, 1, 0, 14)),
            Token(TokenType.LITERAL, ":", generate_context(0, 14, 0, 15)),
            Token(TokenType.TEXT, "value123", generate_context(0, 15, 0, 23)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


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

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "This is text", generate_context(0, 0, 0, 12)),
            Token(
                TokenType.TEXT,
                "split into multiple lines",
                generate_context(1, 0, 1, 25),
            ),
            Token(TokenType.EOL, "", generate_context(2, 0, 2, 0)),
            Token(TokenType.TEXT, "with an empty line", generate_context(3, 0, 3, 18)),
            Token(TokenType.EOF, "", generate_context(4, 0, 4, 0)),
        ],
    )


def test_title():
    lex = runner(". A title")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LABEL, ".", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "A title", generate_context(0, 2, 0, 9)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_title_with_space():
    lex = runner(".  A title")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LABEL, ".", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "A title", generate_context(0, 3, 0, 10)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_label_with_role():
    lex = runner(".some-role A title")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LABEL, ".some-role", generate_context(0, 0, 0, 10)),
            Token(TokenType.TEXT, "A title", generate_context(0, 11, 0, 18)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_comment():
    lex = runner("// Some comment")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


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

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.EOF, "", generate_context(5, 0, 5, 0)),
        ],
    )


def test_multiline_comment_unclosed():
    with pytest.raises(MauException) as exc:
        runner("////")

    assert exc.value.message.type == MauMessageType.ERROR_LEXER
    assert exc.value.message.text == "Unclosed multiline comment."


def test_include_content():
    lex = runner("<<type:/path/to/it.jpg")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.INCLUDE, "<<", generate_context(0, 0, 0, 2)),
            Token(TokenType.TEXT, "type", generate_context(0, 2, 0, 6)),
            Token(TokenType.LITERAL, ":", generate_context(0, 6, 0, 7)),
            Token(TokenType.TEXT, "/path/to/it.jpg", generate_context(0, 7, 0, 22)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_include_content_without_arguments():
    lex = runner("<<type")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.INCLUDE, "<<", generate_context(0, 0, 0, 2)),
            Token(TokenType.TEXT, "type", generate_context(0, 2, 0, 6)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_include_content_with_space():
    lex = runner("<<  type:/path/to/it.jpg")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.INCLUDE, "<<", generate_context(0, 0, 0, 2)),
            Token(TokenType.TEXT, "type", generate_context(0, 4, 0, 8)),
            Token(TokenType.LITERAL, ":", generate_context(0, 8, 0, 9)),
            Token(TokenType.TEXT, "/path/to/it.jpg", generate_context(0, 9, 0, 24)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_include_content_type_can_contain_special_characters():
    lex = runner("<< some.ty_pe#123")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.INCLUDE, "<<", generate_context(0, 0, 0, 2)),
            Token(TokenType.TEXT, "some.ty_pe#123", generate_context(0, 3, 0, 17)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_unordered_list():
    lex = runner("* Item")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "*", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Item", generate_context(0, 2, 0, 6)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_unordered_list_leading_space():
    # This is done to skip the dedent() in the default runner.
    text_buffer = TextBuffer("  * Item", source_filename=TEST_CONTEXT_SOURCE)
    lex = init_lexer(text_buffer)
    lex.process()

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "*", generate_context(0, 2, 0, 3)),
            Token(TokenType.TEXT, "Item", generate_context(0, 4, 0, 8)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_unordered_list_trailing_space():
    lex = runner("*  Item")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "*", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Item", generate_context(0, 3, 0, 7)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_unordered_list_multiple_stars():
    lex = runner("*** Item")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "***", generate_context(0, 0, 0, 3)),
            Token(TokenType.TEXT, "Item", generate_context(0, 4, 0, 8)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_ordered_list():
    lex = runner("# Item")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "#", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Item", generate_context(0, 2, 0, 6)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_ordered_list_multiple_stars():
    lex = runner("### Item")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.LIST, "###", generate_context(0, 0, 0, 3)),
            Token(TokenType.TEXT, "Item", generate_context(0, 4, 0, 8)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_header():
    lex = runner("=Header")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HEADER, "=", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Header", generate_context(0, 1, 0, 7)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_header_with_space():
    lex = runner("=  Header")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HEADER, "=", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Header", generate_context(0, 3, 0, 9)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_empty_header():
    lex = runner("=")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "=", generate_context(0, 0, 0, 1)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_multiple_header_markers():
    lex = runner("=== Header")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HEADER, "===", generate_context(0, 0, 0, 3)),
            Token(TokenType.TEXT, "Header", generate_context(0, 4, 0, 10)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_header_marker_in_header_text():
    lex = runner("= a=b")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HEADER, "=", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "a=b", generate_context(0, 2, 0, 5)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_header_markers_in_text():
    lex = runner("Definitely not a === header")

    compare_asdict_list(
        lex.tokens,
        [
            Token(
                TokenType.TEXT,
                "Definitely not a === header",
                generate_context(0, 0, 0, 27),
            ),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


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

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.BLOCK, "----", generate_context(0, 0, 0, 4)),
            Token(
                TokenType.TEXT,
                "Some comment\n\n   another line",
                generate_context(1, 0, 3, 15),
            ),
            Token(TokenType.BLOCK, "----", generate_context(4, 0, 4, 4)),
            Token(TokenType.EOF, "", generate_context(5, 0, 5, 0)),
        ],
    )


def test_block_inside_block():
    lex = runner(
        dedent(
            """
            ----
            ++++
            ++++
            ----
            """
        )
    )

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.BLOCK, "----", generate_context(0, 0, 0, 4)),
            Token(
                TokenType.TEXT,
                "++++\n++++",
                generate_context(1, 0, 2, 4),
            ),
            Token(TokenType.BLOCK, "----", generate_context(3, 0, 3, 4)),
            Token(TokenType.EOF, "", generate_context(4, 0, 4, 0)),
        ],
    )


def test_block_unclosed():
    with pytest.raises(MauException) as exc:
        runner("----")

    assert exc.value.message.type == MauMessageType.ERROR_LEXER
    assert exc.value.message.text == "Unclosed block."


def test_block_with_header():
    lex = runner(
        dedent(
            """
            = Global header

            [*subtype1]
            ----
            = Block header
            ----
            """
        )
    )

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.HEADER, "=", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "Global header", generate_context(0, 2, 0, 15)),
            Token(TokenType.EOL, "", generate_context(1, 0, 1, 0)),
            Token(TokenType.ARGUMENTS, "[", generate_context(2, 0, 2, 1)),
            Token(TokenType.TEXT, "*subtype1", generate_context(2, 1, 2, 10)),
            Token(TokenType.LITERAL, "]", generate_context(2, 10, 2, 11)),
            Token(TokenType.BLOCK, "----", generate_context(3, 0, 3, 4)),
            Token(TokenType.TEXT, "= Block header", generate_context(4, 0, 4, 14)),
            Token(TokenType.BLOCK, "----", generate_context(5, 0, 5, 4)),
            Token(TokenType.EOF, "", generate_context(6, 0, 6, 0)),
        ],
    )


def test_block_four_characters():
    lex = runner(
        dedent(
            """
            ####
            Some text
            ####
            """
        )
    )

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.BLOCK, "####", generate_context(0, 0, 0, 4)),
            Token(TokenType.TEXT, "Some text", generate_context(1, 0, 1, 9)),
            Token(TokenType.BLOCK, "####", generate_context(2, 0, 2, 4)),
            Token(TokenType.EOF, "", generate_context(3, 0, 3, 0)),
        ],
    )


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

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.BLOCK, "----", generate_context(0, 0, 0, 4)),
            Token(TokenType.TEXT, "// Comment", generate_context(1, 0, 1, 10)),
            Token(TokenType.BLOCK, "----", generate_context(2, 0, 2, 4)),
            Token(TokenType.EOF, "", generate_context(3, 0, 3, 0)),
        ],
    )


def test_block_has_to_begin_with_four_identical_characters():
    lex = runner(
        dedent(
            """
            abcd
            """
        )
    )

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "abcd", generate_context(0, 0, 0, 4)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_control():
    lex = runner("@if somevar==value")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.CONTROL, "@", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "if", generate_context(0, 1, 0, 3)),
            Token(TokenType.TEXT, "somevar==value", generate_context(0, 4, 0, 18)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_control_with_space():
    lex = runner("@if   somevar  !=   value")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.CONTROL, "@", generate_context(0, 0, 0, 1)),
            Token(TokenType.TEXT, "if", generate_context(0, 1, 0, 3)),
            Token(TokenType.TEXT, "somevar  !=   value", generate_context(0, 6, 0, 25)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )
