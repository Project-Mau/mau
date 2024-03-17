from collections.abc import MutableMapping


def flatten_nested_dict(nested, parent_key=None, separator="."):
    flat = {}

    for key, value in nested.items():
        key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, MutableMapping):
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


class Environment:
    def __init__(self, content=None):
        self._variables = {}

        if content is not None:
            self._variables = flatten_nested_dict(content)

    def setvar(self, key, value):
        self._variables[key] = value

    def getvar(self, key, default=None):
        return self._variables.get(key, default)

    def getvar_nodefault(self, key):
        return self._variables[key]

    def getnamespace(self, namespace):
        prefix = f"{namespace}."

        return Environment(
            {
                k.removeprefix(prefix): v
                for k, v in self._variables.items()
                if k.startswith(prefix)
            }
        )

    def update(self, adict, namespace=None):
        if not namespace:
            self._variables.update(flatten_nested_dict(adict))
            return

        self._variables.update(flatten_nested_dict({namespace: adict}))

    def asdict(self):
        return nest_flattened_dict(self._variables)

    def asflatdict(self):
        return self._variables

    def __repr__(self):  # pragma: no cover
        return f"{self.asdict()}"

    def __eq__(self, other):
        return self._variables == other._variables
