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

from mau.parsers.main_parser import MainParser
from mau.parsers.nodes import DocumentNode, ContainerNode
from mau.visitors.html_visitor import HTMLVisitor
from mau.visitors.asciidoctor_visitor import AsciidoctorVisitor
from mau.visitors.markua_visitor import MarkuaVisitor


class Mau:
    def __init__(
        self,
        config,
        target_format,
        default_templates=None,
        templates_directory=None,
        full_document=False,
    ):
        # This is an external configuration file that
        # will be used here and also injected into the variables
        self.config = config

        # The target format that corresponds to a specific visitor
        self.target_format = target_format

        # A dictionary with the default templates.
        self.default_templates = default_templates

        # A directory that contains the custom templates as files
        self.templates_directory = templates_directory

        # If this flag is True the output is wrapped in a DocumentNode,
        # otherwise Mau will use a ContainerNode
        self.full_document = full_document

        # This will contain all the variables declared
        # in the text and in the configuration
        self.variables = {}

    def process(self, text):
        # Update the config with the target format
        self.config["target_format"] = self.target_format

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
        if self.target_format == "html":
            visitor_class = HTMLVisitor
        elif self.target_format == "asciidoctor":
            visitor_class = AsciidoctorVisitor
        elif self.target_format == "markua":
            visitor_class = MarkuaVisitor

        # Retrieve the TOC
        toc = [i.asdict() for i in parser.toc]

        # Retrieve the footnotes
        footnotes = [i.asdict() for i in parser.footnotes]

        # Initialise the visitor
        # Use the parser variables so that the visitor
        # has both the configuration values and the
        # variables defined inside the text
        visitor = visitor_class(
            default_templates=self.default_templates,
            templates_directory=self.templates_directory,
            config=parser.variables,
            toc=toc,
            footnotes=footnotes,
        )

        # Replace variables with the ones processed by the parser
        self.variables = parser.variables

        # Visit the document AST
        return visitor.visit(output.asdict())
