class MauErrorException(ValueError):
    """
    This is a processing error that can occour
    during lexing, parsing, or visiting.
    """

    def __init__(self, error):
        super().__init__(error.message)

        self.error = error


class MauError:
    """
    This is a processing error that can occour
    during lexing, parsing, or visiting.
    """

    source = "global"

    def __init__(self, message, details=None):
        super().__init__()

        self.message = message

        # These are specific values needed by
        # this error, e.g. the context for
        # errors related to tokens
        self.details = details or {}

    def print_details(self):  # pragma: no cover
        print(f"Error: {self.message}")


def print_error(error):  # pragma: no cover
    # This is a function used to print an error occurred
    # during processing.

    len_bar = 80
    title = f" {error.source} error "

    # This takes into account the title and the spaces
    half_bar = "=" * ((len_bar - len(title)) // 2 + 1)
    full_bar = half_bar + "=" * len(title) + half_bar

    print(f"{half_bar}{title}{half_bar}")

    error.print_details()

    print(f"{full_bar}")
