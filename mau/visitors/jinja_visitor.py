import copy
import logging

import jinja2

# from mau.parsers.toc import create_toc
from mau.visitors.base_visitor import BaseVisitor

_logger = logging.getLogger(__name__)


class TemplateNotFound(ValueError):
    pass


class JinjaVisitor(BaseVisitor):
    format_code = "jinja"
    extension = "j2"
    transform = None

    environment_options = {}
    default_templates = {}

    def __init__(
        self,
        *args,
        custom_templates=None,
        templates_directory=None,
        config=None,
        **kwds,
    ):
        super().__init__()

        self.templates_directory = templates_directory
        self.config = copy.deepcopy(config) if config else {}

        self.templates = {}
        self.templates.update(self.default_templates)

        if custom_templates:
            self.templates.update(custom_templates)

        self._join_with = {
            "block": "\n",
            "command_footnotes": "",
            "command_references": "",
            "command_toc": "",
            "container": "",
            "document": "",
            "footnote": "\n",
            "footnotes_entry": "\n",
            "list": "",
            "reference": "\n",
            "references_entry": "\n",
            "sentence": "",
            "toc_entry": "",
        }

        # These act as a temporary storage while we are in mau blocks.
        # There, ToC and footnotes have to be isolated, so at the
        # beginning of the block we save the main ToC and footnotes
        self._temp_toc = None
        self._temp_footnotes = None

        # This is the environment that uses the internal dict
        self._dict_env = jinja2.Environment(
            loader=jinja2.DictLoader(self.templates),
            **self.environment_options,
        )

        # This is the environment that uses files
        # If the templates directory is not defined we fall back to the dict environment
        if self.templates_directory:  # pragma: no cover
            self._files_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(searchpath=self.templates_directory),
                **self.environment_options,
            )
        else:
            self._files_env = self._dict_env

    def _render(self, template_full_name, **kwargs):
        # This renders a template using the current config and the given parameters

        try:
            template = self._files_env.get_template(template_full_name)
        except jinja2.exceptions.TemplateNotFound:
            try:
                template = self._dict_env.get_template(template_full_name)
            except jinja2.exceptions.TemplateNotFound as exception:
                raise TemplateNotFound(exception) from exception

        return template.render(config=self.config, **kwargs)

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
        templates.append(node.node_type)

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

    def _visit_style(self, node):
        base = super()._visit_style(node)
        base["templates"] = [node.value]

        return base

    #     def _visit_macro(self, node):
    #         return {
    #             "data": {
    #                 "name": node.name,
    #                 "args": node.args,
    #                 "kwargs": node.kwargs,
    #             },
    #             "templates": [f"macro-{node.name}", "macro"],
    #         }

    #     def _visit_header(self, node):
    #         return {
    #             "data": {
    #                 "value": node.value,
    #                 "level": int(node.level),
    #                 "anchor": node.anchor,
    #                 "args": node.args,
    #                 "kwargs": node.kwargs,
    #                 "tags": node.tags,
    #             },
    #             "templates": [f"header{node.level}", "header"],
    #         }

    def _visit_content(self, node):
        base = super()._visit_content(node)
        base["templates"] = [
            f"content-{node.content_type}",
            "content",
        ]

        return base

    def _visit_block(self, node):
        base = super()._visit_block(node)
        base["templates"] = [
            f"block-{node.engine}-{node.blocktype}",
            f"block-{node.engine}",
            f"block-{node.blocktype}",
            "block",
        ]

        return base

    def _visit_command_toc(self, node):
        base = super()._visit_command_toc(node)
        base["templates"] = ["toc"]

        return base

    def _visit_command_footnotes(self, node):
        base = super()._visit_command_footnotes(node)
        base["templates"] = ["footnotes"]

        return base

    def _visit_source(self, node):
        base = super()._visit_source(node)
        base["templates"] = [
            f"source-{node.blocktype}-{node.language}",
            f"source-{node.language}",
            f"source-{node.blocktype}",
            "source",
        ]

        return base

    def _visit_reference(self, node):
        base = super()._visit_reference(node)
        base["templates"] = [
            f"reference-{node.content_type}-{node.category}",
            f"reference-{node.content_type}",
            "reference",
        ]

        return base

    def _visit_command_references(self, node):
        base = super()._visit_command_references(node)
        base["templates"] = [
            f"references-{node.content_type}",
            "references",
        ]

        return base

    def _visit_references_entry(self, node):
        base = super()._visit_references_entry(node)
        base["templates"] = [
            f"references_entry-{node.content_type}-{node.category}",
            f"references_entry-{node.content_type}",
            "references_entry",
        ]

        return base
