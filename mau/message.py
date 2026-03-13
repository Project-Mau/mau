from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from logging import ERROR, INFO, Logger

from mau.environment.environment import Environment
from mau.text_buffer import Context, Position, adjust_context, adjust_position


class MauMessageType(Enum):
    ERROR_LEXER = "error-lexer"
    ERROR_PARSER = "error-parser"
    ERROR_VISITOR = "error-visitor"
    DEBUG_VISITOR = "debug-visitor"


@dataclass
class MauMessage:
    type: MauMessageType = field(init=False)
    text: str


@dataclass
class MauLexerErrorMessage(MauMessage):
    type: MauMessageType = field(init=False, default=MauMessageType.ERROR_LEXER)
    source: str
    position: Position | None = None


@dataclass
class MauParserErrorMessage(MauMessage):
    type: MauMessageType = field(init=False, default=MauMessageType.ERROR_PARSER)
    context: Context | None = None
    help_text: str | None = None


@dataclass
class MauVisitorErrorMessage(MauMessage):
    type: MauMessageType = field(init=False, default=MauMessageType.ERROR_VISITOR)
    context: Context | None
    node_type: str | None
    data: dict | None = None
    environment: Environment | None = None
    additional_info: dict[str, str] | None = None
    help_text: str | None = None


@dataclass
class MauVisitorDebugMessage(MauMessage):
    type: MauMessageType = field(init=False, default=MauMessageType.DEBUG_VISITOR)
    context: Context | None
    node_type: str | None
    data: dict | None = None
    environment: Environment | None = None
    additional_info: dict[str, str] | None = None


class MauException(ValueError):
    def __init__(self, message: MauMessage):
        self.message = message


class BaseMessageHandler(ABC):
    type = "base"

    @abstractmethod
    def process_lexer_error(self, message: MauLexerErrorMessage): ...

    @abstractmethod
    def process_parser_error(self, message: MauParserErrorMessage): ...

    @abstractmethod
    def process_visitor_error(self, message: MauVisitorErrorMessage): ...

    @abstractmethod
    def process_visitor_debug(self, message: MauVisitorDebugMessage): ...

    def process(self, message: MauMessage):
        match message.type:
            case MauMessageType.ERROR_LEXER:
                return self.process_lexer_error(message)

            case MauMessageType.ERROR_PARSER:
                return self.process_parser_error(message)

            case MauMessageType.ERROR_VISITOR:
                return self.process_visitor_error(message)

            case MauMessageType.DEBUG_VISITOR:
                return self.process_visitor_debug(message)


class LogMessageHandler(BaseMessageHandler):
    type = "log"

    def __init__(
        self,
        logger: Logger,
        prefix: str | None = None,
        debug_logging_level=INFO,
    ):
        self.logger = logger
        self.prefix = prefix or "[MAU] "
        self.debug_logging_level = debug_logging_level

    def process_lexer_error(self, message: MauLexerErrorMessage):
        self.logger.error(f"Lexer error: {message.text}")
        self.logger.error(f"Source: {message.source}")
        if message.position:
            self.logger.error(f"Position: {adjust_position(message.position)}")

    def process_parser_error(self, message: MauParserErrorMessage):
        self.logger.error(f"Parser error: {message.text}")
        if message.context:
            self.logger.error(f"Context: {adjust_context(message.context)}")
        if message.help_text:
            self.logger.error(message.help_text)

    def _process_visitor_debug_message(
        self,
        message: MauVisitorErrorMessage,
        logging_level,
    ):
        values = {}

        values["Message"] = message.text
        values["Context"] = message.context

        if message.node_type:
            values["Node type"] = message.node_type

        if message.data:
            for k, v in message.data.items():
                values[f"Template data - {k}"] = v

        if message.additional_info:
            values.update(message.additional_info)

        for k, v in values.items():
            self.logger.log(logging_level, f"{self.prefix}{k}: {v}")

    def process_visitor_error(self, message: MauVisitorErrorMessage):
        self.logger.log(ERROR, f"{self.prefix}Visitor error")
        self._process_visitor_debug_message(message, ERROR)

    def process_visitor_debug(self, message: MauVisitorDebugMessage):
        self.logger.log(self.debug_logging_level, f"{self.prefix}Visitor message")
        self._process_visitor_debug_message(message, self.debug_logging_level)
