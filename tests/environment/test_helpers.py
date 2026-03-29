from mau.environment.helpers import (
    flatten_nested_dict,
    nest_flattened_dict,
)


def test_flatten_already_flat():
    dictionary = {
        "var1": "value1",
        "var2": "value2",
    }

    assert flatten_nested_dict(dictionary) == dictionary


def test_flatten_nested():
    dictionary = {
        "var1": {
            "var2": "value2",
            "var3": {
                "var4": "value4",
                "var5": "value5",
            },
        },
    }

    assert flatten_nested_dict(dictionary) == {
        "var1.var2": "value2",
        "var1.var3.var4": "value4",
        "var1.var3.var5": "value5",
    }


def test_flatten_alternative_separator():
    dictionary = {
        "var1": {
            "var2": "value2",
            "var3": {
                "var4": "value4",
                "var5": "value5",
            },
        },
    }

    assert flatten_nested_dict(dictionary, separator="_") == {
        "var1_var2": "value2",
        "var1_var3_var4": "value4",
        "var1_var3_var5": "value5",
    }


def test_flatten_parent_key():
    dictionary = {
        "var1": {
            "var2": "value2",
        },
    }

    assert flatten_nested_dict(dictionary, parent_key="parent") == {
        "parent.var1.var2": "value2",
    }


def test_flatten_empty():
    dictionary = {
        "var1": {
            "var2": {},
        },
    }

    assert flatten_nested_dict(dictionary) == {
        "var1.var2": {},
    }


def test_nest_no_hierarchy_flat():
    dictionary = {
        "var1": "value1",
        "var2": "value2",
    }

    assert nest_flattened_dict(dictionary) == dictionary


def test_nest_no_hierarchy_nested():
    dictionary = {"var1": "value1", "var2": {"var3": "value3"}}

    assert nest_flattened_dict(dictionary) == dictionary


def test_nest_hierarchy():
    flat = {
        "var1.var2": "value2",
        "var1.var3": "value3",
    }

    assert nest_flattened_dict(flat) == {
        "var1": {
            "var2": "value2",
            "var3": "value3",
        },
    }


def test_nest_hierarchy_double_nesting():
    flat = {
        "var1.var2.var3": "value3",
        "var1.var2.var4": "value4",
    }

    assert nest_flattened_dict(flat) == {
        "var1": {
            "var2": {
                "var3": "value3",
                "var4": "value4",
            }
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
