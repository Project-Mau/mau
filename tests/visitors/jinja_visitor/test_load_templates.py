from unittest.mock import Mock, patch

import pytest

from mau.environment.environment import Environment
from mau.message import MauException, MauMessageType
from mau.visitors.jinja_visitor import (
    load_templates_from_filesystem,
    load_templates_from_providers,
)


@patch("mau.visitors.jinja_visitor._load_available_template_providers")
def test_load_templates_from_providers_defined_empty(
    mock_load_available_template_providers,
):
    env = Environment.from_dict({"mau.visitor.templates.providers": []})

    assert load_templates_from_providers(env).asdict() == {}

    mock_load_available_template_providers.assert_not_called()


@patch("mau.visitors.jinja_visitor._load_available_template_providers")
def test_load_templates_from_providers_undefined(
    mock_load_available_template_providers,
):
    env = Environment()

    assert load_templates_from_providers(env).asdict() == {}

    mock_load_available_template_providers.assert_not_called()


@patch("mau.visitors.jinja_visitor._load_available_template_providers")
def test_load_templates_from_providers_provider_available(
    mock_load_available_template_providers,
):
    provider1 = Mock()
    provider2 = Mock()

    mock_templates = {"template1": "text1"}
    provider1.templates = mock_templates

    mock_load_available_template_providers.return_value = {
        "provider1": provider1,
        "provider2": provider2,
    }

    env = Environment.from_dict({"mau.visitor.templates.providers": ["provider1"]})

    assert load_templates_from_providers(env).asdict() == mock_templates

    mock_load_available_template_providers.assert_called_once()


@patch("mau.visitors.jinja_visitor._load_available_template_providers")
def test_load_templates_from_providers_provider_unavailable(
    mock_load_available_template_providers,
):
    provider1 = Mock()

    provider1.templates = {}

    mock_load_available_template_providers.return_value = {
        "provider1": provider1,
    }

    env = Environment.from_dict({"mau.visitor.templates.providers": ["provider2"]})

    with pytest.raises(MauException) as exc:
        assert load_templates_from_providers(env)

    assert exc.value.message.type == MauMessageType.ERROR_VISITOR
    assert exc.value.message.text == "Template provider 'provider2' is not available."
    mock_load_available_template_providers.assert_called_once()


@patch("mau.visitors.jinja_visitor._load_templates_from_path")
def test_load_templates_from_filesystem_empty(mockload_templates_from_path):
    env = Environment.from_dict({"mau.visitor.templates.paths": []})

    assert load_templates_from_filesystem(env, ".ext").asdict() == {}

    mockload_templates_from_path.assert_not_called()


@patch("mau.visitors.jinja_visitor._load_templates_from_path")
def test_load_templates_from_filesystem_undefined(mockload_templates_from_path):
    env = Environment()

    assert load_templates_from_filesystem(env, ".ext").asdict() == {}

    mockload_templates_from_path.assert_not_called()


@patch("mau.visitors.jinja_visitor._load_templates_from_path")
def test_load_templates_from_filesystem(mockload_templates_from_path):
    test_ext = ".ext"

    mock_templates = {"template1": "text1"}
    mockload_templates_from_path.return_value = mock_templates

    env = Environment.from_dict({"mau.visitor.templates.paths": ["template_path"]})

    assert load_templates_from_filesystem(env, test_ext).asdict() == mock_templates

    mockload_templates_from_path.assert_called_with(
        "template_path",
        extension=test_ext,
        preprocess=None,
    )
