from __future__ import annotations

from enum import Enum

from mau.environment.environment import Environment
from mau.parsers.base_parser import create_parser_exception
from mau.text_buffer import Context


class ControlComparisons(Enum):
    """The supported control comparisons."""

    EQUAL_EQUAL = "=="
    BANG_EQUAL = "!="


class Control:
    """A control statement that can be run to
    get a boolean result."""

    def __init__(
        self,
        operator: str,
        variable: str,
        comparison: str,
        value: str,
        context: Context | None = None,
    ):
        if operator not in ["if"]:
            raise create_parser_exception(
                f"Control operator '{operator}' is not supported.",
                context,
            )

        self.operator = operator
        self.variable = variable
        self.comparison = ControlComparisons(comparison)
        self.value = value
        self.context = context

    def process(self, environment: Environment) -> bool:
        # Get the variable value and fail
        # if the variable is not available.
        try:
            variable_value = environment[self.variable]
        except KeyError:
            raise create_parser_exception(
                f"Variable '{self.variable}' has not been defined.",
                self.context,
            )

        # Perform the requested comparison.
        match self.comparison:
            case ControlComparisons.EQUAL_EQUAL:
                return variable_value == self.value
            case ControlComparisons.BANG_EQUAL:
                return variable_value != self.value


class ControlBuffer:
    """A buffer that stores a control statement."""

    def __init__(self):
        # This is where the buffer keeps the
        # stored control statement.
        self.control: Control | None = None

    def push(self, control: Control):
        # Store the given control statement.
        self.control = control

    def pop(self):
        # Retrieve the stored control statement
        # and reset the internal slot.
        control = self.control
        self.control = None

        return control
