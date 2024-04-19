import logging
from pathlib import Path

import jinja2
from mau.environment.environment import Environment

# from mau.parsers.toc import create_toc
from mau.visitors.base_visitor import BaseVisitor

_logger = logging.getLogger(__name__)

JOIN_CHARACTERS = {
    "block": "\n",
    "footnote": "\n",
    "footnotes_entry": "\n",
    "source": None,
}


# pylint: disable=import-outside-toplevel
def load_template_providers():  # pragma: no cover
    """
    This function loads all the template providers belonging to
    the group "mau.templates".
    """

    import sys

    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_plugins = entry_points(group="mau.templates")

    # Load the available plugins
    return {i.name: i.load() for i in discovered_plugins}


def load_templates_from_path(path, filt=None):  # pragma: no cover
    """
    Loads templates fromt he given path into the dictionary `output`.
    The path is expected to contain files named after the template
    they contain and subdirectories with the same structure.
    """

    result = {}

    for obj in path.iterdir():
        if obj.is_file():
            result[obj.name] = filt(obj.read_text()) if filt else obj.read_text()
        else:
            result[obj.name] = load_templates_from_path(obj, filt=filt)

    return result


def create_templates(prefixes, node_templates, node, extension=None):
    prefixes = [f"{prefix}." for prefix in prefixes]
    prefixes.append("")

    node_templates.append(node.node_type)

    # Build
    # [
    # "parent_type.parent_subtype.position",
    # "parent_type.parent_subtype.",
    # "parent_type.position",
    # "parent_type.",
    # ""
    # ]

    parent_types = [""]
    if node.parent:
        parent_types.append(f"{node.parent.node_type}.")

        if node.parent_position:
            parent_types.append(f"{node.parent.node_type}.{node.parent_position}.")

        if node.parent.subtype:
            parent_types.append(f"{node.parent.node_type}.{node.parent.subtype}.")

            if node.parent_position:
                parent_types.append(
                    f"{node.parent.node_type}.{node.parent.subtype}.{node.parent_position}."
                )
    parent_types = parent_types[::-1]

    # Build [".{node_subtype}", ""]
    node_subtypes = [""]
    if node.subtype:
        node_subtypes.append(f".{node.subtype}")
    node_subtypes = node_subtypes[::-1]

    # Build [".{tag1}", ".{tag2}", ..., ""]
    node_tags = [f".{tag}" for tag in node.tags]
    node_tags.append("")

    templates = [
        f"{prefix}{parent_type}{node_template}{node_subtype}{node_tag}"
        for prefix in prefixes
        for parent_type in parent_types
        for node_template in node_templates
        for node_subtype in node_subtypes
        for node_tag in node_tags
    ]

    # The template full name contains the extension
    # with the type of template, e.g. document.txt
    if extension:
        templates = [f"{template}.{extension}" for template in templates]

    return templates


class TemplateNotFound(ValueError):
    pass


class JinjaVisitor(BaseVisitor):
    format_code = "jinja"
    extension = "j2"
    transform = None
    templates_filter = None

    environment_options = {}
    default_templates = Environment()

    _join_with = JOIN_CHARACTERS
    _join_with_default = ""

    def __init__(
        self,
        environment,
        *args,
        **kwds,
    ):
        super().__init__(environment)

        self.template_prefixes = self.environment.getvar("mau.visitor.prefixes", [])

        # Load templates from the visitor plugin
        self.templates = Environment(self.default_templates)

        # Load templates from template provider plugins
        available_providers = load_template_providers()
        requested_providers = environment.getvar("mau.visitor.template_providers", [])
        for provider in requested_providers:  # pragma: no cover
            if provider not in available_providers:
                print(f"Template provider {provider} is not available")
                continue

            self.templates.update(available_providers[provider].templates)

        # Load custom templates provided as files
        templates_directory = environment.getvar("mau.visitor.templates_directory")
        if templates_directory:  # pragma: no cover
            self.templates.update(
                load_templates_from_path(
                    Path.cwd() / Path(templates_directory),
                    filt=self.templates_filter,
                )
            )

        # Load custom templates provided as a dictionary
        self.templates.update(
            environment.getvar("mau.visitor.custom_templates", Environment())
        )

        # These act as a temporary storage while we are in mau blocks.
        # There, ToC and footnotes have to be isolated, so at the
        # beginning of the block we save the main ToC and footnotes
        self._temp_toc = None
        self._temp_footnotes = None

        # This is the environment that uses the internal dict
        self._dict_env = jinja2.Environment(
            loader=jinja2.DictLoader(self.templates.asflatdict()),
            **self.environment_options,
        )

    def _render(self, template_full_name, **kwargs):
        # This renders a template using the current
        # environment and the given parameters
        try:
            template = self._dict_env.get_template(template_full_name)
        except jinja2.exceptions.TemplateNotFound as exception:
            raise TemplateNotFound(exception) from exception

        return template.render(config=self.environment.asdict(), **kwargs)

    def visit(self, node, *args, **kwargs):
        # The visitor has to define functions for each node type
        # and those shall return a dictionary of keys.
        #
        # The node types are a list made of the key `node_types` and the node type.
        # This allows a function to return one or more types that have to
        # be used instead of the standard type, which also allows to write
        # generic functions. See _visit_style in HTMLVisitor which works for
        # multiple styles.
        #
        # The rest of the returned keys are passed to the _render function
        # as keys and are thus available in the template.

        # Template names are created with this schema

        # [prefix.][parent_type.][parent_subtype.][parent_position.][node_template][.node_subtype][.ext]

        if node is None:
            return {}

        result = super().visit(node, *args, **kwargs)
        node_templates = result.get("templates", [])

        templates = create_templates(
            self.template_prefixes, node_templates, node, self.extension
        )

        # The key "data" contains the values that we want
        # to pass to the template. These are used as arguments
        # when calling the template.
        data = result["data"]

        for template in templates:
            try:
                return self._render(template, **data)
            except TemplateNotFound:
                continue

        self._error(f"Cannot find any of the following templates {templates}", node)

        return None  # pragma: no cover

    def _visit_style(self, node, *args, **kwargs):
        base = super()._visit_style(node)
        base["templates"] = [f"style.{node.value}"]

        return base

    def _visit_macro(self, node, *args, **kwargs):
        base = super()._visit_macro(node)
        base["templates"] = [f"macro.{node.name}"]

        return base

    def _visit_content(self, node, *args, **kwargs):
        base = super()._visit_content(node)
        base["templates"] = [
            f"content.{node.content_type}",
        ]

        return base

    def _visit_block(self, node, *args, **kwargs):
        base = super()._visit_block(node)

        base["templates"] = []
        if node.engine is not None:
            base["templates"].append(f"{node.node_type}.{node.engine}")

        return base

    def _visit_block_group(self, node, *args, **kwargs):
        base = super()._visit_block_group(node)

        base["templates"] = [
            f"block_group.{node.group_name}",
        ]

        return base

    def _visit_source(self, node, *args, **kwargs):
        base = super()._visit_source(node)
        base["templates"] = [
            f"source.{node.language}",
        ]

        return base
