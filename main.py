import argparse
import logging
import sys
from typing import Type

import yaml
from rich.traceback import install

from mau import (
    BASE_NAMESPACE,
    Mau,
    __version__,
    load_environment_files,
    load_environment_variables,
    load_visitors,
)
from mau.environment.environment import Environment
from mau.lexers.base_lexer import print_tokens
from mau.message import LogMessageHandler, MauException
from mau.visitors.base_visitor import BaseVisitor

install(show_locals=True)

logger = logging.getLogger(__name__)

# Load a dictionary of all visitors,
# indexed by the output format.
visitors: dict[str, Type[BaseVisitor]] = load_visitors()


def write_output(output, output_file, postprocess=None):
    if postprocess:
        output = postprocess(output)

    # The output file can be "-" which means
    # the standard output
    if output_file == "-":
        print(output)

        return

    # We need to write on an actual file
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(output)
        out.write("\n")


def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-c",
        "--config-file",
        action="store",
        required=False,
        help="Optional YAML config file",
    )

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
        "-e",
        "--environment-file",
        action="append",
        required=False,
        help=(
            "Optional text/YAML file in the form key=path (can be specified "
            "multiple times). The key can be dotted to add namespaces."
        ),
    )

    parser.add_argument(
        "--environment-files-namespace",
        action="store",
        default="envfiles",
        required=False,
        help="Optional namespace for environment files",
    )

    parser.add_argument(
        "-v",
        "--environment-variable",
        action="append",
        required=False,
        help=(
            "Optional environment variable in the form key=value (can be specified "
            "multiple times). The key can be dotted to add namespaces."
        ),
    )

    parser.add_argument(
        "--environment-variables-namespace",
        action="store",
        default="envvars",
        required=False,
        help="Optional namespace for environment variables",
    )

    parser.add_argument(
        "-t",
        "--visitor",
        action="store",
        dest="output_format",
        choices=visitors.keys(),
        help="Output format",
    )

    parser.add_argument(
        "--lexer-print-output",
        dest="lexer_print_output",
        help="print the output of the lexer",
        action="store_true",
    )

    parser.add_argument(
        "--lexer-only",
        dest="lexer_only",
        help="stop after lexing",
        action="store_true",
    )

    parser.add_argument(
        "--version", action="version", version=f"Mau version {__version__}"
    )

    return parser


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    ###############################################
    # INITIAL SETUP
    ###############################################

    # Create the parser.
    argparser = create_parser()

    # Get arguments and logging set up.
    args = argparser.parse_args()
    setup_logging(args.loglevel)

    # Initialise the message handler.
    message_handler = LogMessageHandler(logger)

    ###############################################
    # CONFIGURATION
    ###############################################

    # Load the YAML configuration file into a dictionary.
    # All values in the configuration file are loaded
    # under the hard coded Mau base namespace.
    config = {}
    if args.config_file:
        with open(args.config_file, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

    # Build the initial environment.
    environment = Environment.from_dict(config, BASE_NAMESPACE)

    # The list of environment files passed on the command line.
    environment_files = args.environment_file or []

    # Load the files inside the environment.
    load_environment_files(
        environment,
        environment_files,
        namespace=args.environment_files_namespace,
    )

    # The list of environment variables passed on the command line.
    environment_variables = args.environment_variable or []

    # Load the variables inside the environment.
    load_environment_variables(
        environment,
        environment_variables,
        namespace=args.environment_variables_namespace,
    )

    # Read the input file
    with open(args.input_file, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    # Create the Mau object, passing the environment that
    # we built in the previous section.
    mau = Mau(
        message_handler=message_handler,
        environment=environment,
    )

    # Initialise the Text Buffer.
    text_buffer = mau.init_text_buffer(text, args.input_file)

    ###############################################
    # LEXER
    ###############################################

    # Run the lexer.
    try:
        lexer = mau.run_lexer(text_buffer)
    except MauException:
        sys.exit(1)

    # The user wants us print the resulting tokens.
    if args.lexer_print_output:
        # Print the tokens collected by the lexer.
        print_tokens(lexer.tokens)

    # The user wants us to run the lexer only.
    if args.lexer_only:
        print("Mau stopped after the lexing step as requested")
        sys.exit(0)

    ###############################################
    # PARSER
    ###############################################

    # Run the parser.
    try:
        parser = mau.run_parser(lexer.tokens)
    except MauException:
        sys.exit(1)

    ###############################################
    # VISITOR
    ###############################################

    if not args.output_format:
        argparser.print_help()
        sys.exit(1)

    # Run the visitor.

    # Select the visitor according
    # to the required output format.
    visitor_class = visitors[args.output_format]

    # Get the main output node
    # from the parser.
    document = parser.output.document

    try:
        # Process the node.
        rendered = mau.run_visitor(visitor_class, document)
    except MauException:
        sys.exit(1)

    # Find out the name of the output file
    output_file = args.output_file or args.input_file.replace(
        ".mau", f".{visitor_class.extension}"
    )

    # Write the rendered text to
    # the selected output file.
    write_output(rendered, output_file)


if __name__ == "__main__":
    main()
