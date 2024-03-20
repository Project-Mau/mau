import pytest
from mau.environment.environment import (
    Environment,
    flatten_nested_dict,
    nest_flattened_dict,
)


def test_flatten():
    nested = {
        "var1": {
            "var2": "value2",
            "var3": {
                "var4": "value4",
                "var5": "value5",
            },
        },
    }

    assert flatten_nested_dict(nested) == {
        "var1.var2": "value2",
        "var1.var3.var4": "value4",
        "var1.var3.var5": "value5",
    }


def test_flatten_empty():
    nested = {
        "var1": {
            "var2": {},
        },
    }

    assert flatten_nested_dict(nested) == {
        "var1.var2": {},
    }


def test_nest():
    flat = {
        "var1.var2": "value2",
        "var1.var3.var4": "value4",
        "var1.var3.var5": "value5",
    }

    assert nest_flattened_dict(flat) == {
        "var1": {
            "var2": "value2",
            "var3": {
                "var4": "value4",
                "var5": "value5",
            },
        },
    }


def test_nest_empty():
    flat = {
        "var1.var2": {},
    }

    assert nest_flattened_dict(flat) == {
        "var1": {
            "var2": {},
        },
    }


def test_init():
    environment = Environment()

    assert environment.asdict() == {}


def test_init_with_flat_content():
    environment = Environment({"var1": "value1", "var2": "value2"})

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_init_with_nested_content():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_equality():
    assert Environment(
        {
            "var1": "value1",
            "var2": "value2",
        }
    ) == Environment(
        {
            "var1": "value1",
            "var2": "value2",
        }
    )


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


def test_update_from_other_environment():
    environment = Environment()

    environment.update(Environment({"var1": "value1", "var2": "value2"}))

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_update_with_namespace_from_other_environment():
    environment = Environment()

    environment.update(Environment({"var1": "value1", "var2": "value2"}), "test")

    assert environment.asdict() == {"test": {"var1": "value1", "var2": "value2"}}


def test_update_deep():
    environment = Environment({"mau": {"visitor": {"class": "someclass"}}})

    environment.update(
        {"visitor": {"custom_templates": {"template1": "value1"}}}, "mau"
    )

    assert environment.asdict() == {
        "mau": {
            "visitor": {
                "class": "someclass",
                "custom_templates": {"template1": "value1"},
            },
        },
    }


def test_clone():
    environment = Environment({"var1": "value1", "var2": "value2"})
    clone = environment.clone

    assert not clone is environment
    assert environment.clone().asdict() == {"var1": "value1", "var2": "value2"}


def test_get_variable_flat():
    environment = Environment({"var1": "value1"})

    assert environment.getvar("var1") == "value1"


def test_get_variable_nested():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.getvar("var1.var2") == "value2"


def test_get_variable_nested_empty():
    environment = Environment({"var1": {"var2": {}}})

    assert environment.getvar("var1.var2") == {}


def test_get_variable_flat_default():
    environment = Environment({"var1": "value1"})

    assert environment.getvar("var2", "def") == "def"


def test_get_variable_nested_default():
    environment = Environment({"var1": {"var2": "value2"}})

    assert environment.getvar("var1.var3", "def") == "def"


def test_set_variable_flat():
    environment = Environment()

    environment.setvar("var1", "value1")

    assert environment._variables == {"var1": "value1"}


def test_set_variable_nested():
    environment = Environment()

    environment.setvar("var1.var2", "value2")

    assert environment._variables == {"var1.var2": "value2"}


def test_set_variable_dict():
    environment = Environment()

    environment.setvar("var1", {"var2": "value2"})

    assert environment._variables == {"var1.var2": "value2"}


def test_set_variable_empty_dict():
    environment = Environment()

    environment.setvar("var1", {})
    environment.setvar("var2", {"var3": {}})

    assert environment._variables == {
        "var1": {},
        "var2.var3": {},
    }
    assert environment.getvar("var1") == {}
    assert environment.getvar("var2.var3") == {}


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


def test_get_variable_is_a_namespace():
    environment = Environment(
        {
            "top": {
                "middle": {
                    "var1": "value1",
                    "var2": "value2",
                    "var3": {},
                }
            },
        }
    )

    assert environment.getvar("top")._variables == {
        "middle.var1": "value1",
        "middle.var2": "value2",
        "middle.var3": {},
    }

    assert environment.getvar("top.middle")._variables == {
        "var1": "value1",
        "var2": "value2",
        "var3": {},
    }

    assert environment.getvar("notthere") is None

    assert environment.getvar("top.mid") is None
