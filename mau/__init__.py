# pylint: disable=unused-import

from mau.environment.environment import Environment
from mau.lexers.main_lexer import MainLexer
from mau.lexers.text_lexer import TextLexer
from mau.parsers.main_parser import MainParser
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.visitors.base_visitor import BaseVisitor


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

        self.lexer = MainLexer(self.environment)
        self.parser = MainParser(self.environment)

    def run_lexer(self, text):
        context = Context(source=self.input_file_name)
        text_buffer = TextBuffer(text, context)

        self.lexer.process(text_buffer)

    def run_parser(self, tokens):
        self.parser.parse(tokens)
        self.parser.finalise()

    def create_visitor(self):
        visitor_class = self.environment.getvar("mau.visitor.class")

        return visitor_class(
            environment=self.environment,
        )

    def run_visitor(self, node):
        visitor = self.create_visitor()

        # Visit the document AST
        return visitor.visit(node)
