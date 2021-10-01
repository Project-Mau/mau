# -*- coding: utf-8 -*-

import argparse
import logging
import sys

import yaml

from mau import __version__, Mau, ConfigurationError

__author__ = "Leonardo Giordani"
__copyright__ = "Leonardo Giordani"
__license__ = "mit"

_logger = logging.getLogger(__name__)

# This is a convenience dictionary that collects the output formats
# that Mau supports and some matadata
FORMATS = {
    "html": {"extension": ".html"},
    "asciidoctor": {"extension": ".adoc"},
    "markua": {"extension": ".md"},
}


def parse_args(args):
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
        help="Optional output file",
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
        required=False,
        choices=FORMATS.keys(),
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
        "--version", action="version", version=f"Mau version {__version__}"
    )

    return parser.parse_args()


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    # Get arguments and logging set up
    args = parse_args(args)
    setup_logging(args.loglevel)

    # Read the input file
    with open(args.input_file, "r") as f:
        text = f.read()

    # Load the YAML configuration file into a dictionary
    config = {}
    if args.config_file:
        with open(args.config_file, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

    # Theming is pretty simple. If the config file contains the variable "theme"
    # that is the directory that shall contain all templates.
    templates_directory = f'{config["theme"]}/templates' if "theme" in config else None

    # If a target format is specified on the command line
    # override the one already set in the config file
    # or set it if it isn't.
    if args.format is not None:
        config["target_format"] = args.format

    # The Mau object configured with what we figured out above.
    mau = Mau(
        config,
        None,
        templates_directory=templates_directory,
        full_document=True,
    )

    try:
        # Process the input text.
        output = mau.process(text)
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Find out the name of the output file
    output_extension = FORMATS[args.format]["extension"]
    output_file = args.output_file or args.input_file.replace(".mau", output_extension)

    # Write the output
    with open(output_file, "w") as f:
        text = f.write(output)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
