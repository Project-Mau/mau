from __future__ import annotations

import logging
import sys
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import jinja2

from mau.environment.environment import Environment
from mau.message import BaseMessageHandler
from mau.nodes.node import Node
from mau.visitors.base_visitor import (
    BaseVisitor,
    create_visitor_exception,
)

logger = logging.getLogger(__name__)


class TemplateNotFound(ValueError):
    pass


@dataclass
class Template:
    # This object represents a template and its claims.
    #
    # For subtpye, parent_type, and parent_subtype, None means
    # that there is no claim, so any value in the node will match.
    # A value means that the node the template is applied to must
    # match that value.
    #
    # For tags, an empty list means no claim, while values in the list
    # mean that the set of node tags must be a superset of the
    # template tags.
    #
    # For prefix, any value included None must be matched
    # when rendering the node.

    type: str
    content: str
    name: str
    subtype: str | None = None
    prefix: str | None = None
    parent_type: str | None = None
    parent_subtype: str | None = None
    parent_custom: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    custom: dict[str, str] = field(default_factory=dict)

    @property
    def specificity(self):
        # A tuple that represents
        # the cardinality of the
        # template claims.
        # This will be used to order
        # templates lexicographically.
        return (
            len(self.custom),
            1 if self.subtype else 0,
            1 if self.prefix else 0,
            1 if self.parent_type else 0,
            len(self.parent_custom),
            1 if self.parent_subtype else 0,
            len(self.tags),
        )

    @classmethod
    def from_name(cls, name: str, content: str) -> Template:
        # Create the class from a given
        # template name in the form
        #
        # TYPE[.SUBTPYE][.tg__TAG][.pt__PARENT][.pf__PREFIX]
        #
        # where the elements between
        # square brackets can be in any order.

        # Split the name into parts
        # separated by dots.
        parts = name.split(".")

        # Get the mandatory first part.
        _type = parts[0]

        # If the node type is not in the
        # name (which means the string is
        # empty) we need to stop the process.
        if not _type:
            raise ValueError

        # Build the template object.
        template = Template(type=_type, content=content, name=name)

        # Loop through all remaining parts
        # and use them to assign values to
        # the template.
        for part in parts[1:]:
            if (v := part.removeprefix("pt_")) != part:
                template.parent_type = v
            elif (v := part.removeprefix("pts_")) != part:
                try:
                    key, value = v.split("__")
                    template.parent_custom[key] = value
                except ValueError:
                    template.parent_subtype = v

            elif (v := part.removeprefix("pf_")) != part:
                template.prefix = v
            elif (v := part.removeprefix("tg_")) != part:
                template.tags.append(v)
            else:
                try:
                    key, value = v.split("__")
                    template.custom[key] = value
                except ValueError:
                    template.subtype = v

        return template

    def match(self, node: Node, prefix: str | None = None) -> bool:
        # Check if the given node matches the
        # template claims.
        if self.type and self.type != node.type:
            return False

        # Check all custom fields claimed
        # by the template.
        for key, value in self.custom.items():
            # If the template has a custom field
            # and the node doesn't we cannot match.
            if key not in node.custom_template_fields:
                return False

            # The node has the custom field,
            # let's check the value.
            node_value = node.custom_template_fields[key]

            if value != node_value:
                return False

        if self.prefix != prefix:
            return False

        if self.subtype and self.subtype != node.arguments.subtype:
            return False

        if self.parent_custom and not node.parent:
            return False

        if self.parent_type and not node.parent:
            return False

        if self.parent_subtype and not node.parent:
            return False

        # Check all parent custom fields claimed
        # by the template.
        for key, value in self.parent_custom.items():
            # If the template has a parent_custom field
            # and the node parent doesn't we cannot match.
            if key not in node.parent.custom_template_fields:
                return False

            # The node has the custom field,
            # let's check the value.
            node_value = node.parent.custom_template_fields[key]

            if value != node_value:
                return False

        if self.parent_type and self.parent_type != node.parent.type:
            return False

        if self.parent_subtype and self.parent_subtype != node.parent.arguments.subtype:
            return False

        if self.tags and not set(self.tags).issubset(set(node.arguments.tags)):
            return False

        return True


def _load_available_template_providers():  # pragma: no cover
    # Load all the template providers belonging
    # to the group "mau.templates".

    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_plugins = entry_points(group="mau.templates")

    # Load the available plugins
    return {i.name: i.load() for i in discovered_plugins}


def load_templates_from_providers(environment: Environment) -> Environment:
    # Find all the template providers that
    # have been configured for this execution.
    requested_providers = environment.get("mau.visitor.templates.providers", [])

    # If we didn't request any template provider we can skip this.
    if not requested_providers:
        return Environment()

    # The environment that collects the loaded templates.
    templates = Environment()

    # Load available template provider plugins.
    available_providers = _load_available_template_providers()

    # Load requested providers.
    for provider in requested_providers:
        # Check if the provider is available.
        if provider not in available_providers:
            raise create_visitor_exception(
                text=f"Template provider '{provider}' is not available."
            )

        templates.dupdate(available_providers[provider].templates)

    return templates


def _load_templates_from_path(
    path_str: str | None,
    extension: str,
    preprocess: Callable[[str], str] | None = None,
) -> dict[str, dict | str]:  # pragma: no cover
    # Recursively loads templates from the given path
    # and all its subpaths.
    # Rejects files that do not end with the
    # given extension.

    # If the path string is empty just stop.
    if not path_str:
        return {}

    # The final dictionary of templates.
    result: dict[str, dict | str] = {}

    # Transform the path string into a Path.
    templates_path = Path(path_str)

    # If the path is not absolute, find the relative
    # version and make it absolute.
    if not templates_path.is_absolute():
        templates_path = (Path.cwd() / templates_path).resolve()

    # Set up the preprocess function.
    # If no preprocess function is given we can
    # use the identity function.
    preprocess = preprocess or (lambda x: x)

    # Scan all directories in the given path.
    for obj in templates_path.iterdir():
        # If the object is a directory,
        # recursively load templates from there.
        if obj.is_dir():
            # Collect all templates recursively.
            templates = _load_templates_from_path(
                obj.as_posix(), extension, preprocess=preprocess
            )

            # If we found templates, add them
            # to the results dictionary.
            if templates:
                result[obj.name] = templates

            continue

        # If we found a file, first check
        # if the extension is the one we want.
        # If not, discard and continue.
        if not obj.name.endswith(extension):
            continue

        # If we found a file with the proper
        # extension, read the content,
        # preprocess and store it.
        result[obj.name] = preprocess(obj.read_text())

    return result


def load_templates_from_filesystem(
    environment: Environment,
    extension: str,
    preprocess: Callable[[str], str] | None = None,
) -> Environment:
    # Scan a configured list of paths
    # for templates.
    # Load every file that ends with the
    # given extension, looking recursively
    # into subdirectories.

    # Get the templates path from
    # the configuration environment.
    templates_path_str_list: list[str] = environment.get(
        "mau.visitor.templates.paths", []
    )

    # If no paths have been specified,
    # return and empty environment.
    if not templates_path_str_list:
        return Environment()

    # The environment that collects
    # the loaded templates.
    templates = Environment()

    # Loop through all paths and try
    # to load templates from there.
    for templates_path_str in templates_path_str_list:
        templates.dupdate(
            _load_templates_from_path(
                templates_path_str,
                extension=extension,
                preprocess=preprocess,
            )
        )

    return templates


class JinjaVisitor(BaseVisitor):
    format_code = "jinja"
    extension = ".j2"
    templates_preprocess: Callable[[str], str] | None = None

    join_with = {
        "document": "\n",
        "raw-content": "\n",
        "source": "\n",
        "paragraph": " ",
    }
    join_with_default = ""

    jinja_environment_options = {}
    default_templates = Environment()

    def __init__(
        self,
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
    ):
        super().__init__(message_handler, environment)

        # Load the template prefixes from the configuration.
        self.template_prefixes = environment.get("mau.visitor.templates.prefixes", [])

        # Load default templates.
        # A custom implementation of this visitor might
        # provide default templates that can be overridden
        # by user-defined ones.
        templates_env = Environment.from_environment(self.default_templates)

        # Load the requested template providers from the configuration.
        templates_env.update(load_templates_from_providers(self.environment))

        # Load user-defined templates from files.
        templates_from_filesystem = load_templates_from_filesystem(
            self.environment,
            extension=self.extension,
            preprocess=self.__class__.templates_preprocess,
        )
        templates_env.update(templates_from_filesystem)

        # Load custom templates provided as a dictionary.
        templates_env.update(
            environment.get(
                "mau.visitor.templates.custom",
                Environment(),
            )
        )

        # Here, the environment as a flat dict
        # contains all the templates we defined.
        # We also took care of the hierarchy
        # between sources, as later sources
        # updated might have overwritten what
        # earlier sources created.

        # Here, we need to filter the templates
        # we found keeping only those with the
        # correct extension, remove the latter
        # (so that it doesn't get interpreted
        # as a component of the template name).
        # Then, for all selected templates, we
        # need to devise what type of node they
        # address, and build the MauTemplate
        # object that will allow us to
        # order them by specificity.
        templates = []
        for name, content in templates_env.asflatdict().items():
            # The extension is not the one we
            # requested, skip the template.
            if not name.endswith(self.extension):
                continue

            # Devise the template name
            # without extension.
            name = name.removesuffix(self.extension)

            # Create a template object and
            # add it to the list of templates.
            templates.append(Template.from_name(name, content))

        # Order templates by specificity
        templates.sort(key=lambda t: t.specificity, reverse=True)

        # This dictionary contains list of templates
        # for each node type. The list is sorted
        # in order of specificity.
        self.templates = defaultdict(list)
        for template in templates:
            self.templates[template.type].append(template)

        # A dictionary in the form {'name': 'source'}
        # that Jinja will use to host templates.
        jinja_templates = {t.name: t.content for t in templates}

        # This is the Jinja environment.
        # We prepare it with all the templates we loaded
        # in the previous section of the function.
        self._dict_env = jinja2.Environment(
            loader=jinja2.DictLoader(jinja_templates),
            **self.jinja_environment_options,
        )

    def _render(
        self, node: Node, environment: Environment, template_full_name, **kwargs
    ) -> str:
        # This renders a template using the current
        # environment and the given parameters.

        # Get the template from the Jinja environment.
        try:
            template = self._dict_env.get_template(template_full_name)
        except jinja2.exceptions.TemplateNotFound as exception:
            raise TemplateNotFound(exception) from exception

        # Render the template using the values
        # retrieved visiting the node.
        try:
            rendered_template = template.render(
                config=self.environment.asdict(), **kwargs
            )
        except jinja2.exceptions.UndefinedError as exception:  # pragma: no cover
            raise create_visitor_exception(
                text=f"Error rendering node with template {template_full_name}: {str(exception)}",
                node=node,
                data=kwargs,
                environment=environment,
            ) from exception

        return rendered_template

    def _debug_additional_info(self, node: Node, result: dict):  # pragma: no cover
        templates = self.templates[node.type]

        # The list of all matching templates.
        matching_templates: list[Template] = []

        # Test all templates to find the matching ones.
        # The test is performed on all given prefixes first.
        for prefix in self.template_prefixes:
            matching_templates.extend(
                [t for t in templates if t.match(node, prefix)],
            )

        # Now let's add the matching templates without prefix.
        matching_templates.extend([t for t in templates if t.match(node)])

        return {
            "Available templates": [t.name for t in templates],
            "Matching templates": [t.name for t in matching_templates],
            "Prefixes": self.template_prefixes,
        }

    def _find_matching_template(self, node: Node, data: dict) -> Template:
        # Find all templates available for
        # this type of node in specificity order.
        templates = self.templates[node.type]

        # The list of all matching templates.
        matching_templates: list[Template] = []

        # Test all templates to find the matching ones.
        # The test is performed on all given prefixes first.
        for prefix in self.template_prefixes:
            matching_templates.extend(
                [t for t in templates if t.match(node, prefix)],
            )

        # Now let's add the matching templates without prefix.
        matching_templates.extend([t for t in templates if t.match(node)])

        # If there are no matching templates
        # we are in trouble. Let's print out
        # a message to help the user to debug.
        if not matching_templates:
            raise create_visitor_exception(
                text="Cannot find a suitable template.",
                node=node,
                data=data,
                environment=self.environment,
                additional_info={
                    "Templates found": templates,
                },
            )

        # Select the first template that matches.
        return matching_templates[0]

    def visit(self, node: Node | None, **kwargs) -> str:
        # Visit the node and extract a dictionary of
        # values. Then, extract all templates that
        # target the node type, find the matching
        # ones, select the first and render the
        # node using it.

        # If the node is None we don't need to process
        # anything. If we did, we would get an empty
        # dictionary as a result, and it would be
        # pointless to process it anyway.
        if node is None:
            return ""

        # Visit the node.
        data = super().visit(node, **kwargs)

        # Find a matching template.
        template = self._find_matching_template(node, data)

        return self._render(node, self.environment, template.name, **data)

    def visitlist(
        self, current_node: Node, nodes_list: Sequence[Node], **kwargs
    ) -> str:
        # Find the string this visitor uses to join
        # children according to the current node type.
        join_with = self.join_with.get(current_node.type, self.join_with_default)

        # Visit all nodes in the list.
        visited_nodes = [self.visit(node, **kwargs) for node in nodes_list]

        # Join the results.
        return join_with.join(visited_nodes)
