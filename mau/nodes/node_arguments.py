from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any


def set_names(
    unnamed_args: Sequence[Any],
    named_args: MutableMapping[str, Any],
    positional_names: Sequence[str],
) -> tuple[Sequence[Any], MutableMapping[str, Any]]:
    """
    Give names to positional arguments.

    This function uses the given `positional_names`
    to convert unnamed args to named ones. Each entry
    in `unnamed_args` is assigned a key from
    `positional_names` in order.

    If a positional name is used that is already
    present in `named_args`, the key is ignored
    and the corresponding unnamed entry remains
    unassigned.
    """

    # Filter the given positional names.
    # If a named argument provides the value for a
    # positional name we consider it already set and ignore it.
    positional_names = [i for i in positional_names if i not in named_args]

    # Merge positional names and args into a dictionary.
    # Then create a named argument out of each value.
    # The zip() will ignore arguments that don't have a
    # corresponding value.
    positional_arguments = dict(zip(positional_names, unnamed_args))

    # If we pass more positional values than names,
    # some of them won't be converted and become flags
    unnamed_args = unnamed_args[len(positional_names) :]

    # Update the named dictionary with the
    # positional arguments we just created.
    named_args.update(positional_arguments)

    return unnamed_args, named_args


@dataclass
class NodeArguments:
    unnamed_args: Sequence[str] = field(default_factory=list)
    named_args: MutableMapping[str, str] = field(default_factory=dict)
    tags: Sequence[str] = field(default_factory=list)
    internal_tags: Sequence[str] = field(default_factory=list)
    subtype: str | None = None

    def asdict(self):
        return asdict(self)

    def set_names(self, positional_names: list[str]) -> NodeArguments:
        self.unnamed_args, self.named_args = set_names(
            self.unnamed_args, self.named_args, positional_names
        )

        return self
