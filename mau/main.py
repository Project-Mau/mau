import argparse
import logging
import sys
from importlib import metadata

import yaml
from mau import ConfigurationError, Mau, load_visitors
from mau.lexers.base_lexer import LexerError
from mau.parsers.base_parser import ParserError
from mau.visitors.base_visitor import BaseVisitor, VisitorError
from mau.text_buffer.context import print_context
from tabulate import tabulate

__version__ = metadata.version("mau")
_logger = logging.getLogger(__name__)

visitor_classes = load_visitors()
visitors = {i.format_code: i for i in visitor_classes}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        action="store",
        required=True,
        help="Input file",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        action="store",
        required=False,
        help="Optional output file ('-' for standard output)",
    )

    parser.add_argument(
        "-c",
        "--config-file",
        action="store",
        required=False,
        help="Optional YAML config file",
    )

    parser.add_argument(
        "-f",
        "--format",
        action="store",
        required=True,
        choices=visitors.keys(),
        help="Output format",
    )

    parser.add_argument(
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )

    parser.add_argument(
        "--debug",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    parser.add_argument(
        "--lex-only",
        dest="lexonly",
        help="performs only lexing and prints tokens",
        action="store_true",
    )

    parser.add_argument(
        "--parse-only",
        dest="parseonly",
        help="performs only parsing and prints nodes",
        action="store_true",
    )

    parser.add_argument(
        "--version", action="version", version=f"Mau version {__version__}"
    )

    return parser.parse_args()


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def write_output(output, output_file, transform=None):
    if transform:
        output = transform(output)

    # The output file can be "-" which means
    # the standard output
    if output_file == "-":
        print(output)

        return

    # We need to write on an actual file
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(output)
        out.write("\n")


def main():
    # Get arguments and logging set up
    args = parse_args()
    setup_logging(args.loglevel)

    # Read the input file
    with open(args.input_file, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    # Load the YAML configuration file into a dictionary
    config = {}
    if args.config_file:
        with open(args.config_file, "r", encoding="utf-8") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

    # The directory that contains custom templates.
    templates_directory = config.get("templates_directory", None)

    # Select the visitor class according to the target
    # format specified on the command line
    visitor_class = visitors[args.format]

    # This extracts the custom templates defined
    # in the config file
    custom_templates = config.get("custom_templates", None)

    # Find out the name of the output file
    output_file = args.output_file or args.input_file.replace(
        ".mau", visitor_class.extension
    )

    # The Mau object configured with what we figured out above.
    mau = Mau(
        args.input_file,
        visitor_class=visitor_class,
        config=config,
        custom_templates=custom_templates,
        templates_directory=templates_directory,
        full_document=True,
    )

    # Run the lexer on the input data
    try:
        lexer = mau.run_lexer(text)
    except LexerError as exception:
        print_context(exception.context, f"Lexer error - {str(exception)}")
        sys.exit(1)
    except Exception as exception:  # pylint: disable=broad-exception-caught
        print(f"Unhandled exception: {exception}")
        sys.exit(1)

    if args.lexonly:
        write_output(
            tabulate(
                [(t.type, t.value, t.context) for t in lexer.tokens],
                maxcolwidths=[10, 60, 30],
            ),
            output_file,
        )

        sys.exit(1)

    # Run the parser on the tokens
    try:
        parser = mau.run_parser(lexer.tokens)
    except ParserError as exception:
        print_context(exception.token.context, f"Parser error - {str(exception)}")
        sys.exit(1)

    if args.parseonly:
        write_output(parser.nodes, output_file)
        sys.exit(1)

    # Run the visitor on the AST
    try:
        output = mau.process(parser.nodes, parser.environment)
    except ConfigurationError as exception:
        print(f"Configuration error: {exception}")
        sys.exit(1)
    except ParserError as exception:
        print_context(exception.token.context, f"Parser error - {str(exception)}")
        sys.exit(1)
    except VisitorError as exception:
        print(exception)
        sys.exit(1)

    write_output(output, output_file, transform=visitor_class.transform)
