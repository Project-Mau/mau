import logging
from pathlib import Path

import jinja2
from mau.environment.environment import Environment

# from mau.parsers.toc import create_toc
from mau.visitors.base_visitor import BaseVisitor

_logger = logging.getLogger(__name__)


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


class TemplateNotFound(ValueError):
    pass


class JinjaVisitor(BaseVisitor):
    format_code = "jinja"
    extension = "j2"
    transform = None
    templates_filter = None

    environment_options = {}
    default_templates = Environment()

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

        self._join_with = {
            "block": "\n",
            "footnotes": "",
            "references": "",
            "toc": "",
            "container": "",
            "document": "",
            "footnote": "\n",
            "footnotes_entry": "\n",
            "list": "",
            "list_item": "",
            "reference": "\n",
            "references_entry": "\n",
            "paragraph": "",
            "sentence": "",
            "style": "",
            "toc_entry": "",
        }

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

        if node is None:
            return {}

        result = super().visit(node, *args, **kwargs)

        # The key "templates" contains a list of all templates
        # used for this node.

        # The node type is appended
        # as the last choice to allow specialised
        # templates to be applied first
        templates = result.get("templates", [])
        templates.append(node.node_type.replace("__", "."))

        # Create subtype templates
        node_subtype = getattr(node, "subtype", None)
        if node_subtype:
            templates = [
                f"{t}{suffix}" for t in templates for suffix in (f".{node_subtype}", "")
            ]

        # Create prefixed templates
        prefixed_templates = []
        for prefix in self.template_prefixes:
            prefixed_templates.extend(
                [f"{prefix}.{template}" for template in templates]
            )

        # Preprend the prefixed templates
        templates = prefixed_templates + templates

        # The template full name contains the extension
        # with the type of template, e.g. document.txt
        template_full_names = [f"{template}.{self.extension}" for template in templates]

        # The key "data" contains the values that we want
        # to pass to the template. These are used as arguments
        # when calling the template.
        data = result["data"]

        for template_full_name in template_full_names:
            try:
                return self._render(template_full_name, **data)
            except TemplateNotFound:
                continue

        self._error(
            f"Cannot find any of the following templates {template_full_names}", node
        )

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

    def _visit_reference(self, node, *args, **kwargs):
        base = super()._visit_reference(node)
        base["templates"] = [
            f"reference.{node.content_type}",
        ]

        return base

    def _visit_references(self, node, *args, **kwargs):
        base = super()._visit_references(node)
        base["templates"] = [
            f"references.{node.content_type}",
        ]

        return base

    def _visit_references_entry(self, node, *args, **kwargs):
        base = super()._visit_references_entry(node)
        base["templates"] = [
            f"references_entry.{node.content_type}",
        ]

        return base
