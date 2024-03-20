from abc import ABC
from collections.abc import MutableMapping


class EnvironmentABC(ABC):
    pass


def flatten_nested_dict(nested, parent_key=None, separator="."):
    flat = {}

    for key, value in nested.items():
        key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, MutableMapping) and len(value) != 0:
            flat.update(flatten_nested_dict(value, key, separator=separator))
        else:
            flat[key] = value

    return flat


def nest_flattened_dict(flat, separator="."):
    def _split(key, value, separator, output):
        key, *rest = key.split(separator, 1)

        if rest:
            _split(
                rest[0],
                value,
                separator,
                output.setdefault(key, {}),
            )
        else:
            output[key] = value

    result = {}

    for key, value in flat.items():
        _split(key, value, separator, result)

    return result


class Environment(EnvironmentABC):
    def __init__(self, other=None):
        self._variables = {}

        if other is not None:
            self.update(other)

    def clone(self):
        return self.__class__(self._variables)

    def setvar(self, key, value):
        self.update({key: value})
        # self._variables[key] = value

    def getvar(self, key, default=None):
        try:
            return self._variables[key]
        except KeyError:
            prefix = f"{key}."

            keys = [k for k in self._variables if k.startswith(prefix)]

            if len(keys) != 0:
                return Environment(
                    {
                        k.removeprefix(prefix): v
                        for k, v in self._variables.items()
                        if k.startswith(prefix)
                    }
                )

            return default

    def getvar_nodefault(self, key):
        return self._variables[key]

    def update(self, other, namespace=None):
        if isinstance(other, EnvironmentABC):
            if not namespace:
                self._variables.update(other._variables)
                return

            self._variables.update(flatten_nested_dict({namespace: other._variables}))
        else:
            if not namespace:
                self._variables.update(flatten_nested_dict(other))
                return

            self._variables.update(flatten_nested_dict({namespace: other}))

    def asdict(self):
        return nest_flattened_dict(self._variables)

    def asflatdict(self):
        return self._variables

    def __repr__(self):  # pragma: no cover
        return f"{self.asdict()}"

    def __eq__(self, other):
        return self._variables == other._variables
