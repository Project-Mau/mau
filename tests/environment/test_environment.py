import pytest
from mau.environment.environment import Environment


def test_init():
    environment = Environment()

    assert environment.asdict() == {}


def test_init_with_flat_content():
    environment = Environment({"var1": "value1", "var2": "value2"})

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_init_with_nested_content():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_init_with_flat_content_and_namespace():
    environment = Environment({"var1": "value1", "var2": "value2"}, "test")

    assert environment.asdict() == {"test": {"var1": "value1", "var2": "value2"}}


def test_init_with_nested_content_and_namespace():
    environment = Environment({"var1": {"var2": "value2"}}, "test")

    assert environment.asdict() == {"test": {"var1": {"var2": "value2"}}}


def test_update():
    environment = Environment()

    environment.update({"var1": "value1", "var2": "value2"})

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_update_does_not_replace():
    environment = Environment({"var1": "value1", "var2": "value2"})

    environment.update({"var3": "value3"})

    assert environment.asdict() == {
        "var1": "value1",
        "var2": "value2",
        "var3": "value3",
    }


def test_update_with_namespace():
    environment = Environment()

    environment.update({"var1": "value1", "var2": "value2"}, "test")

    assert environment.asdict() == {"test": {"var1": "value1", "var2": "value2"}}


def test_update_with_namespace_does_not_replace():
    environment = Environment({"test": {"var1": "value1", "var2": "value2"}})

    environment.update({"var3": "value3"}, "test")

    assert environment.asdict() == {
        "test": {"var1": "value1", "var2": "value2", "var3": "value3"}
    }


def test_get_variable_flat():
    environment = Environment({"var1": "value1"})

    assert environment.getvar("var1") == "value1"


def test_get_variable_nested():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.getvar("var1.var2") == "value2"


def test_get_variable_flat_default():
    environment = Environment({"var1": "value1"})

    assert environment.getvar("var2", "def") == "def"


def test_get_variable_nested_default():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.getvar("var1.var3", "def") == "def"


def test_set_variables_flat():
    environment = Environment()

    environment.setvar("var1", "value1")

    assert environment.asdict() == {"var1": "value1"}


def test_set_variables_nested():
    environment = Environment()

    environment.setvar("var1.var2", "value2")

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_asdict():
    environment = Environment()

    environment.setvar("var1.var2", "value2")
    environment.setvar("var3.var4.var5", "value5")

    assert environment.asdict() == {
        "var1": {
            "var2": "value2",
        },
        "var3": {
            "var4": {
                "var5": "value5",
            },
        },
    }


def test_get_variable_flat_no_default():
    environment = Environment()

    with pytest.raises(KeyError):
        environment.getvar_nodefault("var1")


def test_get_variable_nested_no_default():
    environment = Environment()

    with pytest.raises(KeyError):
        environment.getvar_nodefault("var1.var2")


def test_get_namespace():
    environment = Environment(
        {
            "top": {
                "middle": {
                    "var1": "value1",
                    "var2": "value2",
                }
            }
        }
    )

    assert environment.getnamespace("top").asdict() == {
        "middle": {
            "var1": "value1",
            "var2": "value2",
        },
    }

    assert environment.getnamespace("top.middle").asdict() == {
        "var1": "value1",
        "var2": "value2",
    }

    assert environment.getnamespace("notthere").asdict() == {}
