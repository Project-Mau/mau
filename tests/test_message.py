import logging

from mau.message import (
    BaseMessageHandler,
    LogMessageHandler,
    MauLexerErrorMessage,
    MauParserErrorMessage,
    MauVisitorDebugMessage,
    MauVisitorErrorMessage,
)
from mau.text_buffer import Context


class RecordingMessageHandler(BaseMessageHandler):
    def __init__(self):
        self.calls = []

    def process_lexer_error(self, message: MauLexerErrorMessage):
        self.calls.append(("lexer", message))
        return "lexer"

    def process_parser_error(self, message: MauParserErrorMessage):
        self.calls.append(("parser", message))
        return "parser"

    def process_visitor_error(self, message: MauVisitorErrorMessage):
        self.calls.append(("visitor_error", message))
        return "visitor_error"

    def process_visitor_debug(self, message: MauVisitorDebugMessage):
        self.calls.append(("visitor_debug", message))
        return "visitor_debug"


def test_base_message_handler_process_routes():
    handler = RecordingMessageHandler()

    lexer_message = MauLexerErrorMessage(
        text="Lexer error", source="somesource", position=(0, 0)
    )
    parser_message = MauParserErrorMessage(text="Parser error", context=Context.empty())

    visitor_error_message = MauVisitorErrorMessage(
        text="Visitor error",
        context=Context.empty(),
        node_type="paragraph",
        data=None,
        environment=None,
        additional_info=None,
    )
    visitor_debug_message = MauVisitorDebugMessage(
        text="Visitor debug",
        context=Context.empty(),
        node_type="paragraph",
        data=None,
        environment=None,
        additional_info=None,
    )

    assert handler.process(lexer_message) == "lexer"
    assert handler.process(parser_message) == "parser"
    assert handler.process(visitor_error_message) == "visitor_error"
    assert handler.process(visitor_debug_message) == "visitor_debug"

    assert [call[0] for call in handler.calls] == [
        "lexer",
        "parser",
        "visitor_error",
        "visitor_debug",
    ]


def test_log_message_handler_lexer_error_logs_source_and_position(caplog):
    logger = logging.getLogger("tests.message.lexer")
    handler = LogMessageHandler(logger)

    with caplog.at_level(logging.ERROR, logger=logger.name):
        handler.process_lexer_error(
            MauLexerErrorMessage(text="nope", source="somesource", position=(0, 1))
        )

    assert "Lexer error: nope" in caplog.text
    assert "Source: somesource" in caplog.text
    assert "Position: (1, 1)" in caplog.text


def test_log_message_handler_parser_error_logs_context(caplog):
    logger = logging.getLogger("tests.message.parser")
    handler = LogMessageHandler(logger)
    context = Context(0, 0, 1, 1, source="doc.mau")

    with caplog.at_level(logging.ERROR, logger=logger.name):
        handler.process_parser_error(
            MauParserErrorMessage(text="nope", context=context)
        )

    assert "Parser error: nope" in caplog.text
    assert "Context: doc.mau:1,0-2,1" in caplog.text


def test_log_message_handler_visitor_error_logs_details(caplog):
    logger = logging.getLogger("tests.message.visitor")
    handler = LogMessageHandler(logger, prefix="[TEST] ")
    message = MauVisitorErrorMessage(
        text="nope",
        context=Context(0, 0, 0, 0),
        node_type="paragraph",
        data={"foo": "bar"},
        environment=None,
        additional_info={"Extra": "value"},
    )

    with caplog.at_level(logging.ERROR, logger=logger.name):
        handler.process_visitor_error(message)

    assert "[TEST] Visitor error" in caplog.text
    assert "[TEST] Message: nope" in caplog.text
    assert "[TEST] Context: 0,0-0,0" in caplog.text
    assert "[TEST] Node type: paragraph" in caplog.text
    assert "[TEST] Template data - foo: bar" in caplog.text
    assert "[TEST] Extra: value" in caplog.text


def test_log_message_handler_visitor_debug_logs_details(caplog):
    logger = logging.getLogger("tests.message.visitor_debug")
    handler = LogMessageHandler(logger, prefix="[TEST] ")
    message = MauVisitorDebugMessage(
        text="debug info",
        context=Context(0, 0, 0, 0),
        node_type="paragraph",
        data={"foo": "bar"},
        environment=None,
        additional_info={"Extra": "value"},
    )

    with caplog.at_level(logging.INFO, logger=logger.name):
        handler.process_visitor_debug(message)

    assert "[TEST] Visitor message" in caplog.text
    assert "[TEST] Message: debug info" in caplog.text
    assert "[TEST] Context: 0,0-0,0" in caplog.text
    assert "[TEST] Node type: paragraph" in caplog.text
    assert "[TEST] Template data - foo: bar" in caplog.text
    assert "[TEST] Extra: value" in caplog.text
