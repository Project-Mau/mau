from importlib import metadata
from pathlib import Path
from typing import Type

import yaml

__version__ = metadata.version("mau")

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import BaseMessageHandler, MauException
from mau.nodes.node import Node
from mau.parsers.document_parser import DocumentParser
from mau.text_buffer import TextBuffer
from mau.token import Token
from mau.visitors.base_visitor import BaseVisitor
from mau.visitors.jinja_visitor import JinjaVisitor
from mau.visitors.yaml_visitor import YamlVisitor

# This is the base namespace used by
# the configuration, by variables defined
# on the command line, and by variables
# loaded from YAML files.
BASE_NAMESPACE = "mau"

# All YAML environment files are
# loaded by default into this
# secondary namespace (in addition
# to the base namespace).
DEFAULT_ENVIRONMENT_FILES_NAMESPACE = "envfiles"

# All variables defined on the command
# line are loaded into this
# secondary namespace (in addition
# to the base namespace).
DEFAULT_ENVIRONMENT_VARIABLES_NAMESPACE = "envvars"


class ConfigurationError(ValueError):
    """Used to signal an error in the configuration"""


def load_visitors():  # pragma: no cover
    """
    This function loads all the visitors belonging to
    the group "mau.visitors". This code has been isolated
    in a function to allow visitor modules to import the
    Mau package without running into circular imports.
    """

    import sys

    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    # Load all packages that register
    # themselves under the group
    # `mau.visitors`.
    discovered_plugins = entry_points(group="mau.visitors")

    # Load the available visitors.
    visitors = {i.value: i.load() for i in discovered_plugins}

    # Add the visitors defined
    # in this codebase.
    visitors["core:YamlVisitor"] = YamlVisitor
    visitors["core:JinjaVisitor"] = JinjaVisitor

    return visitors


def load_environment_files(
    environment: Environment,
    files: list[str],
    namespace: str | None = None,
):
    """Load YAML files into dictionaries and
    convert them into an environment."""

    # Set the namespace or use the default one.
    namespace = namespace or DEFAULT_ENVIRONMENT_FILES_NAMESPACE

    # Add the base namespace as a prefix.
    namespace = f"{BASE_NAMESPACE}.{namespace}"

    # Create a flat dictionary that will
    # contain all the environment files.
    flat_environment_files: dict[str, str] = {}

    for filename in files:
        # Files can be specified as `PATH` or as `KEY=PATH`.
        # If the key is specified the file content is stored under
        #
        # ENVIRONMENT_FILES_NAMESPACE.KEY
        #
        # If it's just path, the file content is stored under
        #
        # ENVIRONMENT_FILES_NAMESPACE.FILENAME
        #
        # where `FILENAME` is just the name of the file
        # extracted from the full path.

        try:
            # Assume the filename is in the form "key=path".
            key, value = filename.split("=")

            # Create a Path from the file path.
            filepath = Path(value)
        except ValueError:
            # Create a Path from the file path.
            filepath = Path(filename)

            # The key is the name of the
            # file without extension.
            key = filepath.stem

        try:
            # Assume this is YAML.
            with filepath.open("r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                flat_environment_files[key] = content
        except Exception as exc:
            raise ConfigurationError(f"Error processing {filename}") from exc

    if flat_environment_files:
        environment.dupdate(flat_environment_files, namespace)


def load_environment_variables(
    environment: Environment,
    variables: list[str],
    namespace: str | None = None,
):
    """Load each environment variable into the environment."""

    # Set the namespace.
    namespace = namespace or DEFAULT_ENVIRONMENT_VARIABLES_NAMESPACE

    # Add the base namespace as a prefix.
    namespace = f"{BASE_NAMESPACE}.{namespace}"

    # Build a flat dictionary with all the environment variables.
    flat_environment_variables: dict[str, str] = {}

    for variable in variables:
        # Variables must be specified as KEY=VALUE.
        # The VALUE is stored under
        #
        # ENVIRONMENT_VARIABLES_NAMESPACE.KEY

        # Parse the environment variable syntax.
        key, value = variable.split("=")

        # Store the value.
        flat_environment_variables[key] = value

    if flat_environment_variables:
        environment.dupdate(flat_environment_variables, namespace)


class Mau:  # pragma: no cover
    def __init__(
        self,
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
    ):
        # This is the message handler that
        # can process any message created
        # inside Mau.
        self.message_handler = message_handler

        # This will contain all the variables declared
        # in the text and in the configuration.
        self.environment = environment or Environment()

        # This will contain the lexer tokens.
        self.tokens: list[Token] = []

    def init_text_buffer(self, text: str, source_filename: str) -> TextBuffer:
        # The text buffer that manages the input file.
        return TextBuffer(text, source_filename=source_filename)

    def run_lexer(self, text_buffer: TextBuffer) -> DocumentLexer:
        try:
            lexer = DocumentLexer(text_buffer, self.message_handler, self.environment)
            lexer.process()
        except MauException as exc:
            self.message_handler.process(exc.message)
            raise

        return lexer

    def run_parser(self, tokens: list[Token]) -> DocumentParser:
        try:
            parser = DocumentParser(tokens, self.message_handler, self.environment)
            parser.parse()
        except MauException as exc:
            self.message_handler.process(exc.message)
            raise

        return parser

    def run_visitor(self, visitor_class: Type, node: Node | None) -> dict:
        # Initialise the visitor with the
        # current environment.
        try:
            visitor = visitor_class(self.message_handler, self.environment)

            # Visit the given node and all its children.
            return visitor.process(node)
        except MauException as exc:
            self.message_handler.process(exc.message)
            raise

    def process(
        self,
        visitor_class: Type[BaseVisitor],
        text: str,
        source_filename: str,
    ):
        # The text buffer that manages the input file.
        text_buffer = self.init_text_buffer(text, source_filename)

        # Run the lexer on the text buffer.
        lexer = self.run_lexer(text_buffer)

        # Parse the lexer tokens.
        parser = self.run_parser(lexer.tokens)

        # Get the main node from the parser.
        document = parser.output.document

        # Run the selected visitor.
        rendered = self.run_visitor(visitor_class, document)

        return rendered
