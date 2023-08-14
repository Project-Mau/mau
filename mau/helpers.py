import re


def rematch(regexp, text):
    # Compile the regexp and get a match on the current line
    return re.compile(regexp).match(text)
