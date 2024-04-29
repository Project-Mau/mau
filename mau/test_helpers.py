import pytest
import pathlib


import textwrap

from mau.environment.environment import Environment
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer


def dedent(text):
    return textwrap.dedent(text).strip()


def init_lexer_factory(lexer_class):
    """
    A factory that returns a lexer initialiser.
    The returned function initialises the lexer
    and returns it.
    """

    def _init_lexer(environment=None):
        return lexer_class(environment)

    return _init_lexer


def lexer_runner_factory(lexer_class, *args, **kwds):
    """
    A factory that returns a lexer runner.
    The returned function initialises and
    runs the lexer on the given source.
    """

    init_lexer = init_lexer_factory(lexer_class)

    def _run(source, environment=None, **kwargs):
        kwds.update(kwargs)

        environment = environment or Environment()

        text_buffer = TextBuffer(textwrap.dedent(source), Context())

        lexer = init_lexer(environment, *args, **kwds)
        lexer.process(text_buffer)

        return lexer

    return _run


def init_parser_factory(lexer_class, parser_class):
    """
    A factory that returns a parser initialiser.
    The returned function initialises and runs the lexer,
    initialises the parser and returns it.
    """

    def _init_parser(text, environment=None, *args, **kwargs):
        text_buffer = TextBuffer(text, Context(source="main"))

        lex = lexer_class(environment)
        lex.process(text_buffer)

        par = parser_class(environment, *args, **kwargs)
        par.tokens = lex.tokens

        return par

    return _init_parser


def parser_runner_factory(lexer_class, parser_class, *args, **kwds):
    """
    A factory that returns a parser runner.
    The returned function runs the parser on the given source.
    """

    init_parser = init_parser_factory(lexer_class, parser_class)

    def _run(source, environment=None, **kwargs):
        kwds.update(kwargs)

        environment = environment or Environment()

        parser = init_parser(textwrap.dedent(source), environment, *args, **kwds)
        parser.parse(parser.tokens)
        parser.finalise()

        return parser

    return _run


def load_files(source_dir, source_ext, expected_dir, expected_ext):
    source_files = pathlib.Path(source_dir).rglob(f"*.{source_ext}")

    files = [
        (i, expected_dir / i.with_suffix(f".{expected_ext}").relative_to(source_dir))
        for i in source_files
    ]

    return files


def collect_test_files(
    tests_dir, source_dir_name, source_ext, expected_dir_name, expected_ext
):
    source_dir = tests_dir / source_dir_name
    expected_dir = tests_dir / expected_dir_name

    return [
        pytest.param(i, j, id=str(i.relative_to(tests_dir)))
        for i, j in load_files(source_dir, source_ext, expected_dir, expected_ext)
    ]
