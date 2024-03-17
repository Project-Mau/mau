import pytest
from mau.environment.environment import Environment


def test_init():
    environment = Environment()

    assert environment.asdict() == {}


def test_init_with_content():
    environment = Environment({"var1": "value1", "var2": "value2"})

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_init_with_content_and_environment():
    environment = Environment({"var1": "value1", "var2": "value2"}, "test")

    assert environment.asdict() == {"test": {"var1": "value1", "var2": "value2"}}


def test_flat_environment_default():
    environment = Environment()

    environment.setvar("var1", "value1")

    assert environment.getvar("var2", "defaultvalue") == "defaultvalue"


def test_set_and_get_variables_flat():
    environment = Environment()

    environment.setvar("var1", "value1")
    environment.setvar("var2", "value2")

    assert environment.getvar("var1") == "value1"
    assert environment.getvar("var2") == "value2"
    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_set_and_get_variables_namespace():
    environment = Environment()

    environment.setvar("namespace.var1", "value1")
    environment.setvar("namespace.var2", "value2")

    assert environment.getvar("namespace.var1") == "value1"
    assert environment.getvar("namespace.var2") == "value2"
    assert environment.asdict() == {"namespace": {"var1": "value1", "var2": "value2"}}


def test_set_and_get_variables_nested_namespace():
    environment = Environment()

    environment.setvar("name.space.var1", "value1")
    environment.setvar("name.space.var2", "value2")

    assert environment.getvar("name.space.var1") == "value1"
    assert environment.getvar("name.space.var2") == "value2"
    assert environment.asdict() == {
        "name": {"space": {"var1": "value1", "var2": "value2"}}
    }


def test_set_and_get_variables_no_default():
    environment = Environment()

    with pytest.raises(KeyError):
        environment.getvar_nodefault("name.space.var2")


def test_multiple_namespaces():
    environment = Environment()
    environment.setvar("top.middle.var1", 1)
    environment.setvar("top.middle.var2", 2)

    assert environment.asdict() == {"top": {"middle": {"var1": 1, "var2": 2}}}


def test_get_namespace():
    environment = Environment()
    environment.setvar("top.middle.var1", 1)
    environment.setvar("top.middle.var2", 2)

    assert environment.getnamespace("top") == Environment(
        {"middle": {"var1": 1, "var2": 2}}
    )

    assert environment.getnamespace("top.middle") == Environment({"var1": 1, "var2": 2})


def test_update():
    environment = Environment()

    environment.update({"name1": "value1", "name2": "value2"})

    assert environment.asdict() == {"name1": "value1", "name2": "value2"}


def test_update_with_namespace():
    environment = Environment()

    environment.update({"name1": "value1", "name2": "value2"}, "test")

    assert environment.asdict() == {"test": {"name1": "value1", "name2": "value2"}}
