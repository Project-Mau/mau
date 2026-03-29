from collections.abc import MutableMapping


def flatten_nested_dict(
    nested: MutableMapping, parent_key: str | None = None, separator: str = "."
) -> dict:
    """
    Flatten a nested dictionary.

    This recursive function takes a nested dictionary and returns a flat
    dictionary with hierarchical keys (e.g. "level1.level2.level3").
    The `separator` used in the key names can be specified, the default
    is a dot.

    The function can optionally prefix every key with `parent_key`.
    """

    # This is the final flattened dictionary.
    flat = {}

    # Process all keys at this level.
    for key, value in nested.items():
        # Prefix the key with the parent key if present.
        key = f"{parent_key}{separator}{key}" if parent_key else key

        # If the value is another non-empty dictionary, call the function
        # recursively, otherwise just store it as it is.
        if isinstance(value, MutableMapping) and len(value) != 0:
            # Update the dictionary with the result of the recursive call.
            # The parent key here is the current hierarchical key.
            flat.update(flatten_nested_dict(value, key, separator=separator))
        else:
            flat[key] = value

    return flat


def nest_flattened_dict(flat: dict, separator: str = ".") -> dict:
    """
    Nest a flat dictionary.

    This function takes a flat dictionary and decomposes
    hierarchical keys, creating a nested dictionary.
    The `separator` used to decompose keys can be specified
    and the default is a dot.
    """

    # Helper function to process a key.
    # If the key doesn't contain the separator it
    # is stored as it is in the output,
    # otherwise the key is split once and
    # the function is called recursively.
    def _split(key, value, separator, output):
        # Split the key once.
        # E.g. 'a.b.c' --> ('a', ['b.c'])
        key, *rest = key.split(separator, 1)

        # If the key still has hierarchical
        # parts, call the function recursively.
        if rest:
            _split(
                rest[0],
                value,
                separator,
                output.setdefault(key, {}),
            )
        else:
            output[key] = value

    result: dict = {}

    for key, value in flat.items():
        _split(key, value, separator, result)

    return result
