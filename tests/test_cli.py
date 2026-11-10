import pytest

from mau.cli import default_output_file


@pytest.mark.parametrize(
    "input_file,extension,expected",
    [
        # Extension without the leading dot
        ("test.mau", "yaml", "test.yaml"),
        # Extension with the leading dot
        ("test.mau", ".yaml", "test.yaml"),
        # Paths are preserved.
        ("/path/to/myinput.mau", ".yaml", "/path/to/myinput.yaml"),
        # Paths with dots are preserved.
        ("dir.mau/test.mau", ".yaml", "dir.mau/test.yaml"),
        # Only the final suffix is replaced.
        ("my.file.mau", ".yaml", "my.file.yaml"),
        # Input files without the .mau suffix.
        ("test", ".yaml", "test.yaml"),
        ("test.txt", ".yaml", "test.yaml"),
    ],
)
def test_default_output_file(input_file, extension, expected):
    assert default_output_file(input_file, extension) == expected


def test_default_output_file_never_overwrites_input():
    assert default_output_file("page.yaml", ".yaml") == "page.yaml.yaml"


def test_default_output_file_empty_extension():
    # BaseVisitor defines an empty extension.
    assert default_output_file("test.mau", "") == "test.out"


def test_default_output_file_strip_extension_spaces():
    # BaseVisitor defines an empty extension.
    assert default_output_file("test.mau", "  html  ") == "test.html"


def test_default_output_file_strip_extension_only_spaces():
    # BaseVisitor defines an empty extension.
    assert default_output_file("test.mau", "    ") == "test.out"
