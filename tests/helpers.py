import textwrap

from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer


def dedent(text):
    return textwrap.dedent(text).strip()


def init_parser_factory(lexer_class, parser_class):
    """
    A factory that returns a parser initialiser.
    The returned function initialises and runs the lexer,
    initialises the parser and returns it.
    """

    def _init_parser(text, *args, **kwargs):
        text_buffer = TextBuffer(text, Context(source="main"))

        lex = lexer_class(text_buffer)
        lex.process()

        par = parser_class(lex.tokens, *args, **kwargs)

        return par

    return _init_parser


def parser_runner_factory(lexer_class, parser_class, *args, **kwds):
    """
    A factory that returns a parser runner.
    The returned function runs the parser on the given source.
    """

    init_parser = init_parser_factory(lexer_class, parser_class)

    def _run(source, **kwargs):
        kwds.update(kwargs)

        parser = init_parser(textwrap.dedent(source), *args, **kwds)
        parser.parse()

        return parser

    return _run
