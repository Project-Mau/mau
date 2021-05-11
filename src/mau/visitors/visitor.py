import copy
import logging

import jinja2

_logger = logging.getLogger(__name__)


class TemplateNotFound(ValueError):
    pass


class Visitor:
    _template_extension = ".txt"
    _environment_options = {}

    def __init__(
        self,
        default_templates=None,
        templates_directory=None,
        config=None,
        toc=None,
        footnotes=None,
    ):
        self.default_templates = default_templates or {}
        self.templates_directory = templates_directory
        self.config = copy.deepcopy(config) if config else {}
        self.toc = toc or []
        self.footnotes = footnotes or []

        # This is the fallback environment for templates
        self.default_templates_env = jinja2.Environment(
            loader=jinja2.DictLoader(self.default_templates),
            **self._environment_options,
        )

        # This is the first choice for templates
        if self.templates_directory:
            self.main_templates_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(searchpath=self.templates_directory),
                **self._environment_options,
            )
        else:
            self.main_templates_env = self.default_templates_env

    def _template(self, node_type):  # pragma: no cover
        # This returns a template or raises TemplateNotFound

        template_name = f"{node_type}{self._template_extension}"

        try:
            return self.main_templates_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            _logger.debug(
                f"Template {template_name} not provided, trying the default one"
            )
            try:
                return self.default_templates_env.get_template(template_name)
            except jinja2.exceptions.TemplateNotFound as e:
                raise TemplateNotFound(e)

    def _render(self, node_type, **kwargs):
        # This renders a template passing the visitor configuration

        template = self._template(node_type)

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
            return ""

        keys = getattr(self, f'_visit_{node["type"]}')(node, *args, **kwargs)

        node_types = []
        node_types.extend(keys.pop("node_types", []))
        node_types.append(node["type"])

        for i in node_types:
            try:
                return self._render(i, **keys)
            except TemplateNotFound:
                continue

        raise ValueError(f"Cannot find any suitable template among {node_types}")

    def visitlist(self, nodes):
        return [self.visit(i) for i in nodes]

    def _visit_text(self, node):
        return {"value": node["value"]}

    def _visit_sentence(self, node):
        return {"content": "".join([self.visit(t) for t in node["content"]])}

    def _visit_paragraph(self, node):
        return {"content": self.visit(node["content"])}

    def _visit_horizontal_rule(self, node):
        return {}

    def _visit_style(self, node):
        return {"node_types": [node["value"]], "content": self.visit(node["content"])}

    def _visit_verbatim(self, node):
        return {"content": node["value"]}

    def _visit_container_node(self, node):
        return {
            "node_types": ["container"],
            "content": "".join([self.visit(item) for item in node["content"]]),
        }

    def _visit_macro(self, node):
        return {}
