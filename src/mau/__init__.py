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
from mau.parsers.nodes import DocumentNode
from mau.visitors.html_visitor import HTMLVisitor
from mau.visitors.asciidoctor_visitor import AsciidoctorVisitor


class Mau:
    def __init__(
        self, config, target_format, default_templates=None, templates_directory=None
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

        # A flag that triggers a custom behaviour
        # of the document node
        self.no_document = config.get("no_document", False)

        # This will contain all the variables declared
        # in the text and in the configuration
        self.variables = {}

    def process(self, text):
        # Store the target format
        self.config["target_format"] = self.target_format

        parser = MainParser(variables=self.config)
        parser.load(text)
        parser.parse()

        self.variables = parser.variables

        document = DocumentNode(parser.nodes, self.no_document)

        ast = document.asdict()

        if self.target_format == "html":
            visitor_class = HTMLVisitor
        elif self.target_format == "asciidoctor":
            visitor_class = AsciidoctorVisitor

        visitor = visitor_class(
            default_templates=self.default_templates,
            templates_directory=self.templates_directory,
            config=self.config,
            toc=[i.asdict() for i in parser.toc],
            footnotes=[i.asdict() for i in parser.footnotes],
        )

        return visitor.visit(ast)
