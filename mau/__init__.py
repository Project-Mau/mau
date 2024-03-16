# pylint: disable=unused-import

from mau.lexers.main_lexer import MainLexer
from mau.lexers.text_lexer import TextLexer
from mau.nodes.page import ContainerNode, DocumentNode
from mau.parsers.environment import Environment
from mau.parsers.main_parser import MainParser
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.visitors.base_visitor import BaseVisitor

# from mau.visitors.html_visitor import HTMLVisitor
# from mau.visitors.markua_visitor import MarkuaVisitor
# from mau.visitors.latex_visitor import LatexVisitor


# pylint: disable=import-outside-toplevel
def load_visitors():
    """
    This function loads all the visitors belonging to
    the group "mau.visitors". This code has been isolated
    in a function to allow visitor modules to import the
    Mau package without creating a cycle.
    """

    import sys

    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_plugins = entry_points(group="mau.visitors")

    # Load the available visitors
    visitors = [i.load() for i in discovered_plugins]
    visitors.append(BaseVisitor)

    return visitors


class ConfigurationError(ValueError):
    """Used to signal an error in the configuration"""


class Mau:
    def __init__(
        self,
        input_file_name,
        environment=None,
    ):
        # This is needed to set up the initial context for the lexer
        self.input_file_name = input_file_name

        # This will contain all the variables declared
        # in the text and in the configuration
        self.environment = environment or Environment()

    def run_lexer(self, text):
        context = Context(source=self.input_file_name)
        text_buffer = TextBuffer(text, context)

        lexer = MainLexer(text_buffer)
        lexer.process()

        return lexer

    def run_parser(self, tokens):
        # Parse the source text using the given configuration
        parser = MainParser(tokens, environment=self.environment)
        parser.parse()

        return parser

    def process(self, nodes):
        full_document = self.environment.getvar("mau.full_document", True)
        visitor_class = self.environment.getvar("mau.visitor_class")

        wrapper_node_class = ContainerNode
        if full_document:
            wrapper_node_class = DocumentNode

        # Wrap the whole output
        output = wrapper_node_class(nodes)

        # Initialise the visitor
        # Use the parser variables so that the visitor
        # has both the configuration values and the
        # variables defined inside the text
        visitor = visitor_class(
            environment=self.environment,
        )

        # Visit the document AST
        return visitor.visit(output)
