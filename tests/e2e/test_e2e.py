import pathlib
import pytest
import yaml

from mau.environment.environment import Environment
from mau.nodes.page import DocumentNode
from mau.visitors.base_visitor import BaseVisitor
from mau.lexers.main_lexer import MainLexer
from mau.parsers.main_parser import MainParser
from mau.test_helpers import (
    init_parser_factory,
    parser_runner_factory,
    collect_test_files,
)

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)

tests_dir = pathlib.Path(__file__).parent

tst_files = collect_test_files(tests_dir, "source", "mau", "expected", "yaml")


@pytest.mark.parametrize("source,expected", tst_files)
def test_e2e(source, expected):
    with open(source, encoding="utf-8") as source_file:
        source_code = source_file.read()

    with open(expected, encoding="utf-8") as expected_file:
        expected_code = yaml.load(expected_file.read(), Loader=yaml.FullLoader)

    parser = runner(source_code)

    node = DocumentNode(children=parser.nodes)
    visitor = BaseVisitor(Environment())
    result = visitor.visit(node)

    assert result == expected_code
