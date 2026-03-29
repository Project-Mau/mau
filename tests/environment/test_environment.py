import pytest

from mau.environment.environment import Environment


def test_init():
    environment = Environment()

    assert environment.asdict() == {}


def test_init_with_flat_content():
    # Test that the Environment can be created
    # with a flat dictionary.

    environment = Environment.from_dict({"var1": "value1", "var2": "value2"})

    assert environment.asdict() == {"var1": "value1", "var2": "value2"}


def test_init_with_flat_content_and_namespace():
    # Test that the Environment can be created
    # with a flat dictionary and a given namespace.

    environment = Environment.from_dict(
        {"var1": "value1", "var2": "value2"}, namespace="parent"
    )

    assert environment.asdict() == {"parent": {"var1": "value1", "var2": "value2"}}


def test_as_flat_dict():
    # Test that the Environment can be rendered
    # as a flat dictionary with dotted keys

    environment = Environment.from_dict(
        {"var1": "value1", "var2": "value2"}, namespace="parent"
    )

    assert environment.asflatdict() == {
        "parent.var1": "value1",
        "parent.var2": "value2",
    }


def test_init_with_nested_content():
    # Test that the Environment can be created
    # with a nested dictionary.

    environment = Environment.from_dict({"var1": {"var2": "value2"}})

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_init_with_nested_content_and_namespace():
    # Test that the Environment can be created
    # with a nested dictionary and a given namespace.

    environment = Environment.from_dict(
        {"var1": {"var2": "value2"}}, namespace="parent"
    )

    assert environment.asdict() == {"parent": {"var1": {"var2": "value2"}}}


def test_init_with_flat_hierarchical_content():
    # Test that the Environment can be created
    # with a flat dictionary with dotted keys.

    environment = Environment.from_dict({"var1.var3": "value3", "var2": "value2"})

    assert environment.asdict() == {"var1": {"var3": "value3"}, "var2": "value2"}


def test_create_from_other_environment():
    # Test that an Environment can be
    # created from another environment.

    environment_src = Environment.from_dict({"var1": "value1"})
    environment_dst = Environment.from_environment(environment_src)

    assert environment_dst.asdict() == {
        "var1": "value1",
    }


def test_create_from_other_environment_with_namespace():
    # Test that an Environment can be
    # created from another environment
    # using a namespace.

    environment_src = Environment.from_dict({"var1": "value1"})
    environment_dst = Environment.from_environment(environment_src, namespace="test")

    assert environment_dst.asdict() == {
        "test": {
            "var1": "value1",
        },
    }


def test_update_with_flat_content():
    # Test that an existing Environment can be
    # updated using a flat dictionary.

    environment = Environment.from_dict({"var1": "value1"})

    environment.dupdate({"var2": "value2", "var3": "value3"})

    assert environment.asdict() == {
        "var1": "value1",
        "var2": "value2",
        "var3": "value3",
    }


def test_update_with_flat_content_and_namespace():
    # Test that an existing Environment can be
    # updated using a flat dictionary and a given namespace.

    environment = Environment.from_dict({"var1": "value1"})

    environment.dupdate({"var2": "value2", "var3": "value3"}, namespace="test")

    assert environment.asdict() == {
        "var1": "value1",
        "test": {"var2": "value2", "var3": "value3"},
    }


def test_update_with_nested_content():
    # Test that an existing Environment can be
    # updated using a nested dictionary.

    environment = Environment.from_dict({"var1": "value1"})

    environment.dupdate({"var2": {"var3": "value3"}})

    assert environment.asdict() == {"var1": "value1", "var2": {"var3": "value3"}}


def test_update_with_nested_content_and_namespace():
    # Test that an existing Environment can be
    # updated using a nested dictionary and a given namespace.

    environment = Environment.from_dict({"var1": "value1"})

    environment.dupdate({"var2": {"var3": "value3"}}, namespace="test")

    assert environment.asdict() == {
        "var1": "value1",
        "test": {"var2": {"var3": "value3"}},
    }


def test_update_deep():
    # Check that the update operation can add
    # keys deep into the hierarchy.

    environment = Environment.from_dict({"mau": {"visitor": {"class": "someclass"}}})

    environment.dupdate(
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


def test_set_value_flat():
    # Check that values can be written with a
    # dictionary-like syntax.

    environment = Environment()

    environment["var1"] = "value1"

    assert environment.asdict() == {"var1": "value1"}


def test_set_value_hierarchical():
    # Check that writing a value with a dotted key
    # results in a hierarchical dictionary.

    environment = Environment()

    environment["var1.var2"] = "value2"

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_set_value_nested():
    # Check that writing a hierarchical
    # value results in a hierarchical dictionary.

    environment = Environment()

    environment["var1"] = {"var2": "value2"}

    assert environment.asdict() == {"var1": {"var2": "value2"}}


def test_set_value_empty_dict():
    # Check that a key can be given
    # an empty dictionary as value.

    environment = Environment()

    environment["var1.var2"] = {}

    assert environment.asdict() == {"var1": {"var2": {}}}


def test_get_value_flat():
    # Check that values can be read with a
    # dictionary-like syntax.

    environment = Environment.from_dict({"var1": "value1"})

    assert environment["var1"] == "value1"


def test_get_value_nested():
    # Check that values can be read
    # using dotted keys.

    environment = Environment.from_dict({"var1": {"var2": "value2"}})

    assert environment["var1.var2"] == "value2"


def test_get_value_nested_empty():
    # Check that empty dictionaries are
    # supported values.

    environment = Environment.from_dict({"var1": {"var2": {}}})

    assert environment["var1.var2"] == {}


def test_get_value_flat_no_key():
    # Check that the Environment raises an
    # exception if a flat key doesn't exist.

    environment = Environment()

    with pytest.raises(KeyError):
        environment["var1"]


def test_get_value_nested_no_key():
    # Check that the Environment raises an
    # exception if a nested key doesn't exist.

    environment = Environment()

    with pytest.raises(KeyError):
        environment["var1.var2"]


def test_get_value_method_flat():
    # Check that the method get returns
    # the correct value with a flat key.

    environment = Environment.from_dict({"var1": "value1"})

    assert environment.get("var1") == "value1"


def test_get_value_method_nested():
    # Check that the method get returns
    # the correct value with a nested key.

    environment = Environment.from_dict({"var1": {"var2": "value2"}})

    assert environment.get("var1.var2") == "value2"


def test_get_value_method_accepts_default_flat():
    # Check that the method get accepts
    # and returns a default value.

    environment = Environment.from_dict({"var1": "value1"})

    assert environment.get("var2", "def") == "def"


def test_get_value_method_accepts_default_nested():
    # Check that the method get accepts
    # and returns a default value.

    environment = Environment.from_dict({"var1": {"var2": "value2"}})

    assert environment.get("var1.var3", "def") == "def"


def test_get_value_key_is_a_namespace_prefix():
    environment = Environment.from_dict(
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

    assert environment.get("top").asdict() == {
        "middle": {
            "var1": "value1",
            "var2": "value2",
            "var3": {},
        }
    }

    assert environment.get("top.middle").asdict() == {
        "var1": "value1",
        "var2": "value2",
        "var3": {},
    }

    assert environment.get("notthere") is None
    assert environment.get("top.mid") is None


def test_update_without_namespace():
    environment = Environment()
    other = Environment.from_dict({"var1": "value1", "var2": "value2"})

    environment.update(other)

    assert environment.asdict() == other.asdict()


def test_update_with_namespace():
    source_dict = {"var1": "value1", "var2": "value2"}
    namespace = "somespace"

    environment = Environment()
    other = Environment.from_dict(source_dict)

    environment.update(other, namespace)

    assert environment.asdict() == {"somespace": source_dict}


def test_update_no_overwrite_without_namespace():
    environment = Environment.from_dict({"var1": "valueX"})
    other = Environment.from_dict({"var1": "value1", "var2": "value2"})

    environment.update(other, overwrite=False)

    assert environment.asdict() == {"var1": "valueX", "var2": "value2"}


def test_update_no_overwrite_with_namespace():
    source_dict = {"var1": "value1", "var2": "value2"}
    namespace = "somespace"

    environment = Environment.from_dict({"somespace": {"var1": "valueX"}})
    other = Environment.from_dict(source_dict)

    environment.update(other, namespace, overwrite=False)

    assert environment.asdict() == {"somespace": {"var1": "valueX", "var2": "value2"}}
