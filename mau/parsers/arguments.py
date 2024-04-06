def set_names_and_defaults(
    args,
    kwargs,
    positional_names,
    default_values=None,
):
    """
    Gives names to positional arguments and assigns
    default values to the ones that have not been
    initialised.
    """

    if default_values is not None:
        _default_values = default_values.copy()
    else:
        _default_values = {}

    # If a named argument provides the value for a
    # positional name we consider it set
    positional_names = [i for i in positional_names if i not in kwargs]

    # If we pass more positional values than names,
    # some of them won't be converted and become flags
    remaining_args = args[len(positional_names) :]

    positional_arguments = dict(zip(positional_names, args))

    # Named arguments win over the defaults
    _default_values.update(kwargs)

    # Positional arguments with win over all the rest
    _default_values.update(positional_arguments)

    # Positional arguments are mandatory and strict
    # so all the names have to be present in the
    # final dictionary.
    if not set(positional_names).issubset(set(_default_values.keys())):
        raise ValueError(
            f"The following attributes need to be specified: {positional_names}"
        )

    return remaining_args, _default_values
