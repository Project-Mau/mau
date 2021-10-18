# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

# This is not used here but exported to __init__.py
from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser
from mau.parsers.nodes import DocumentNode, ContainerNode
from mau.visitors.html_visitor import HTMLVisitor
from mau.visitors.asciidoctor_visitor import AsciidoctorVisitor
from mau.visitors.markua_visitor import MarkuaVisitor


class ConfigurationError(ValueError):
    """ Used to signal an error in the configuration """


class Mau:
    def __init__(
        self,
        config,
        target_format,
        default_templates=None,
        custom_templates=None,
        templates_directory=None,
        full_document=False,
    ):
        # This is an external configuration file that
        # will be used here and also injected into the variables
        self.config = config

        # A dictionary with the default templates.
        self.default_templates = default_templates

        # A dictionary with the custom templates.
        self.custom_templates = custom_templates

        # A directory that contains the custom templates as files
        self.templates_directory = templates_directory

        # If this flag is True the output is wrapped in a DocumentNode,
        # otherwise Mau will use a ContainerNode
        self.full_document = full_document

        # This will contain all the variables declared
        # in the text and in the configuration
        self.variables = {}

    def process(self, text):
        # Store the config under the Mau namespace
        self.variables["mau"] = self.config

        # Parse the source text using the given configuration
        parser = MainParser(variables=self.variables)
        parser.load(text)
        parser.parse()

        wrapper_node_class = ContainerNode
        if self.full_document:
            wrapper_node_class = DocumentNode

        # Wrap the whole output
        output = wrapper_node_class(parser.nodes)

        # Select the visitor class
        target_format = self.config.get("target_format", "html")

        if target_format == "html":
            visitor_class = HTMLVisitor
        elif target_format == "asciidoctor":
            visitor_class = AsciidoctorVisitor
        elif target_format == "markua":
            visitor_class = MarkuaVisitor
        else:
            raise ConfigurationError(f"Target format {target_format} is not available")

        # Initialise the visitor
        # Use the parser variables so that the visitor
        # has both the configuration values and the
        # variables defined inside the text
        visitor = visitor_class(
            default_templates=self.default_templates,
            custom_templates=self.custom_templates,
            templates_directory=self.templates_directory,
            config=parser.variables,
            toc=parser.toc,
            footnotes=parser.footnotes,
        )

        # Replace variables with the ones processed by the parser
        self.variables = parser.variables

        # Visit the document AST
        return visitor.visit(output.asdict())
