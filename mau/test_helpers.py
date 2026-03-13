import textwrap
from collections.abc import MutableMapping, MutableSequence, Sequence

from mau.environment.environment import Environment
from mau.message import (
    BaseMessageHandler,
    MauLexerErrorMessage,
    MauParserErrorMessage,
    MauVisitorDebugMessage,
    MauVisitorErrorMessage,
)
from mau.nodes.label import LabelNode
from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
)
from mau.text_buffer import Context, TextBuffer
from mau.visitors.base_visitor import BaseVisitor

TEST_CONTEXT_SOURCE = "test.py"


# This function removes the parent info if present. This is done
# to make it possible to write the node sequence without
# having to build each single component in isolation to
# establish the parent-child relationship.
def _remove_parent(data: dict) -> dict:
    data["parent"] = {}

    return data


def dedent(text):
    return textwrap.dedent(text).strip()


def generate_context(line: int, column: int, end_line: int, end_column: int):
    return Context(line, column, end_line, end_column, TEST_CONTEXT_SOURCE)


def compare_asdict_object(obj_left, obj_right):
    assert obj_left.asdict() == obj_right.asdict()


def compare_asdict_list(objs_left: MutableSequence, objs_right: MutableSequence):
    assert [i.asdict() for i in objs_left] == [i.asdict() for i in objs_right]


def check_visit_node(node, expected):
    bv = BaseVisitor(message_handler=NullMessageHandler())

    result = bv.visit(node, add_context=False, add_parent=False)

    assert result == expected


def check_node_with_content(node):
    node.content = [Node(), Node()]

    bv = BaseVisitor(message_handler=NullMessageHandler())

    result = bv.visit(node)

    assert result["content"] == [
        {
            "_type": "none",
            "_context": Context.empty().asdict(),
            "kwargs": {},
            "parent": {},
            "subtype": None,
            "tags": [],
            "internal_tags": [],
            "args": [],
        },
        {
            "_type": "none",
            "_context": Context.empty().asdict(),
            "kwargs": {},
            "parent": {},
            "subtype": None,
            "tags": [],
            "internal_tags": [],
            "args": [],
        },
    ]


def check_node_with_labels(node):
    node.labels = {
        "label1": LabelNode("label1", content=[Node(), Node()]),
        "label2": LabelNode("label2", content=[Node()]),
    }

    bv = BaseVisitor(message_handler=NullMessageHandler())

    result = bv.visit(node)

    node_data = {
        "_type": "none",
        "_context": Context.empty().asdict(),
        "kwargs": {},
        "parent": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    assert result["labels"] == {
        "label1": {
            "_type": "label",
            "_context": Context.empty().asdict(),
            "kwargs": {},
            "parent": {},
            "subtype": None,
            "tags": [],
            "internal_tags": [],
            "args": [],
            "role": "label1",
            "content": [node_data, node_data],
        },
        "label2": {
            "_type": "label",
            "_context": Context.empty().asdict(),
            "kwargs": {},
            "parent": {},
            "subtype": None,
            "tags": [],
            "internal_tags": [],
            "args": [],
            "role": "label2",
            "content": [node_data],
        },
    }


def check_parent(node: Node | None, nodes: Sequence[Node]):
    for i in nodes:
        assert i.parent == node


def compare_nodes(node: Node, expected: Node):
    bv = BaseVisitor(message_handler=NullMessageHandler())

    visit_node = bv.visit(node)
    visit_expected = bv.visit(expected)

    assert visit_node == visit_expected


def compare_nodes_sequence(nodes: Sequence[Node], expected: Sequence[Node]):
    bv = BaseVisitor(message_handler=NullMessageHandler())

    visit_nodes = [bv.visit(node, transformer=_remove_parent) for node in nodes]

    visit_expected = [bv.visit(node, transformer=_remove_parent) for node in expected]

    assert visit_nodes == visit_expected


def compare_nodes_map(
    nodes: MutableMapping[str, Node], expected: MutableMapping[str, Node]
):
    bv = BaseVisitor(message_handler=NullMessageHandler())

    visit_nodes = {
        k: bv.visit(node, transformer=_remove_parent) for k, node in nodes.items()
    }
    visit_expected = {
        k: bv.visit(node, transformer=_remove_parent) for k, node in expected.items()
    }

    assert visit_nodes == visit_expected


def init_lexer_factory(lexer_class):
    """
    A factory that returns a lexer initialiser.
    The returned function initialises the lexer
    and returns it.
    """

    def _init_lexer(text_buffer: TextBuffer, environment: Environment | None = None):
        return lexer_class(text_buffer, NullMessageHandler(), environment)

    return _init_lexer


def lexer_runner_factory(lexer_class, *args, **kwds):
    """
    A factory that returns a lexer runner.
    The returned function initialises and
    runs the lexer on the given source.
    """

    init_lexer = init_lexer_factory(lexer_class)

    def _run(text, environment: Environment | None = None, **kwargs):
        kwds.update(kwargs)

        environment = environment or Environment()

        text_buffer = TextBuffer(
            textwrap.dedent(text),
            source_filename=TEST_CONTEXT_SOURCE,
        )

        lexer = init_lexer(text_buffer, environment, *args, **kwds)
        lexer.process()

        return lexer

    return _run


def init_tokens_manager_factory(lexer_class, tokens_manager_class):
    def _init_tokens_manager(text: str, environment):
        text_buffer = TextBuffer(text, source_filename=TEST_CONTEXT_SOURCE)

        lex = lexer_class(text_buffer, environment)
        lex.process()

        tm = tokens_manager_class(lex.tokens)

        return tm

    return _init_tokens_manager


def init_parser_factory(lexer_class, parser_class):
    """
    A factory that returns a parser initialiser.
    The returned function initialises and runs the lexer,
    initialises the parser and returns it.
    """

    def _init_parser(source: str, environment=None, *args, **kwargs):
        text_buffer = TextBuffer(
            textwrap.dedent(source),
            source_filename=TEST_CONTEXT_SOURCE,
        )

        lex = lexer_class(
            text_buffer,
            NullMessageHandler(),
            environment,
        )
        lex.process()

        par = parser_class(
            lex.tokens,
            NullMessageHandler(),
            environment,
            *args,
            **kwargs,
        )

        return par

    return _init_parser


def parser_runner_factory(lexer_class, parser_class, *args, **kwds):
    """
    A factory that returns a parser runner.
    The returned function runs the parser on the given source.
    """

    init_parser = init_parser_factory(lexer_class, parser_class)

    def _run(source, environment=None, **kwargs):
        kwds.update(kwargs)

        environment = environment or Environment()

        parser = init_parser(source, environment, *args, **kwds)

        parser.parse()

        return parser

    return _run


class ATestNode(Node, NodeLabelsMixin, NodeContentMixin):
    type = "test"

    def __init__(
        self,
        value: str,
        content: list[Node] | None = None,
        labels: dict[str, list[Node]] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        self.value = value

        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)


class NullMessageHandler(BaseMessageHandler):
    type = "null"

    def process_lexer_error(self, message: MauLexerErrorMessage):
        pass

    def process_parser_error(self, message: MauParserErrorMessage):
        pass

    def process_visitor_error(self, message: MauVisitorErrorMessage):
        pass

    def process_visitor_debug(self, message: MauVisitorDebugMessage):
        pass
