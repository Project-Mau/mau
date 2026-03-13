from __future__ import annotations

from .helpers import flatten_nested_dict, nest_flattened_dict


class Environment:
    """
    This is a class that hosts a nested configuration.

    An Environment contains a dictionary of
    configuration variables that can be queried using flat
    variable names like `a.b.c`.
    """

    def __init__(self):
        # This is the internal dictionary, which
        # is always kept in its flattened version.
        self._variables: dict = {}

    @classmethod
    def from_dict(cls, other: dict, namespace: str | None = None):
        env = cls()
        env.dupdate(other, namespace)
        return env

    @classmethod
    def from_environment(cls, other: Environment, namespace: str | None = None):
        return cls().from_dict(other.asdict(), namespace)

    def update(self, other: Environment, namespace: str | None = None, overwrite=True):
        # Create an environment, to get all
        # plain variables with the right
        # namespace.
        new_env = Environment.from_dict(other._variables, namespace)

        if overwrite:
            self._variables.update(new_env._variables)
            return

        new_env._variables.update(self._variables)
        self._variables = new_env._variables

    def dupdate(self, other: dict, namespace: str | None = None):
        # If there is a namespace store the
        # new dictionary under it.
        if namespace:
            other = {namespace: other}

        self._variables.update(flatten_nested_dict(other))

    def asdict(self) -> dict[str, str | dict]:
        return nest_flattened_dict(self._variables)

    def asflatdict(self) -> dict[str, str]:
        return self._variables

    def __setitem__(self, key, value):
        # If the value is a dictionary, we need to include
        # it into the Environment namespace.
        # This is why we don't update self._variables directly.
        self.dupdate({key: value})

    def __getitem__(self, key):
        return self._variables[key]

    def get(self, key, default=None):
        try:
            # If the key is present in the flat
            # index we can just return the
            # corresponding value.
            return self._variables[key]
        except KeyError:
            # The key is not there, let's
            # check if it works as a namespace.

            # Add the dot to transform the
            # key into a namespace prefix.
            prefix = f"{key}."

            # Find all the flat keys that
            # start with that prefix.
            keys = [k for k in self._variables if k.startswith(prefix)]

            # If we found matching keys,
            # we need to return the corresponding
            # items as an Environment.
            #
            # For each matching key, we create
            # the key without prefix and store
            # the value under it. Then, we
            # promote to an Environment.
            if len(keys) != 0:
                return self.__class__.from_dict(
                    {
                        k.removeprefix(prefix): v
                        for k, v in self._variables.items()
                        if k.startswith(prefix)
                    }
                )

            # If we can't find matching keys
            # we should return the default value.
            return default
