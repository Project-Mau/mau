from unittest.mock import patch

import pytest

from mau import ConfigurationError, load_environment_files, load_environment_variables
from mau.environment.environment import Environment


def test_load_environment_files_empty():
    environment = Environment()

    load_environment_files(environment, [], "somespace")

    assert environment.asdict() == {}


@patch("mau.Path.open")
@patch("mau.yaml.safe_load")
def test_load_environment_files(mock_safe_load, mock_path_open):
    # Test that we can load a file with
    #
    # `akey=/path/to/afile.yaml`
    #
    # resulting in its content being stored
    # under the namespace `mau.envfiles.akey`.

    test_content = {
        "key1": "value1",
        "key2": "value2",
    }
    mock_safe_load.return_value = test_content

    environment = Environment()

    load_environment_files(
        environment,
        ["akey=/path/to/afile.yaml"],
    )

    assert environment.asdict() == {
        "mau": {
            "envfiles": {
                "akey": {
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        }
    }


@patch("mau.Path.open")
@patch("mau.yaml.safe_load")
def test_load_environment_files_custom_namespace(mock_safe_load, mock_path_open):
    # Test that we can load a file with
    #
    # `akey=/path/to/afile.yaml`
    #
    # using the custom namespace `somespace`,
    # resulting in its content being stored
    # under the namespace `mau.somespace.akey`.

    test_content = {
        "key1": "value1",
        "key2": "value2",
    }
    mock_safe_load.return_value = test_content

    environment = Environment()

    load_environment_files(
        environment,
        ["akey=/path/to/afile.yaml"],
        "somespace",
    )

    assert environment.asdict() == {
        "mau": {
            "somespace": {
                "akey": {
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        }
    }


@patch("mau.Path.open")
@patch("mau.yaml.safe_load")
def test_load_environment_files_simple_path(mock_safe_load, mock_path_open):
    # Test that we can load a file with
    #
    # `/path/to/afile.yaml`
    #
    # resulting in its content being stored
    # under the namespace `mau.envfiles.afile`.

    test_content = {
        "key1": "value1",
        "key2": "value2",
    }
    mock_safe_load.return_value = test_content

    environment = Environment()

    load_environment_files(
        environment,
        ["/path/to/afile.yaml"],
    )

    assert environment.asdict() == {
        "mau": {
            "envfiles": {
                "afile": {
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        }
    }


@patch("mau.Path.open")
@patch("mau.yaml.safe_load")
def test_load_environment_failed_load(mock_safe_load, mock_path_open):
    mock_safe_load.side_effect = ValueError

    with pytest.raises(ConfigurationError):
        load_environment_files(
            Environment(),
            ["/path/to/afile.yaml"],
        )


def test_load_environment_variables_empty():
    environment = Environment()

    load_environment_variables(environment, [], "somespace")

    assert environment.asdict() == {}


def test_load_environment_variables():
    # Test that we can load a variable
    #
    # `answer=42`
    #
    # resulting in the value 42 being stored
    # under the namespace `mau.envvars.answer`.

    environment = Environment()

    load_environment_variables(
        environment,
        ["answer=42"],
    )

    assert environment.asdict() == {
        "mau": {
            "envvars": {
                "answer": "42",
            }
        }
    }


def test_load_environment_variables_custom_namespace():
    # Test that we can load a variable
    #
    # `answer=42`
    #
    # using the custom namespace `somespace`,
    # resulting in the value 42 being stored
    # under the namespace `mau.somespace.answer`.

    environment = Environment()

    load_environment_variables(environment, ["answer=42"], "somespace")

    assert environment.asdict() == {
        "mau": {
            "somespace": {
                "answer": "42",
            }
        }
    }
