import copy
import logging

import jinja2

_logger = logging.getLogger(__name__)


class TemplateNotFound(ValueError):
    pass


def return_node(node, *args, **kwargs):
    return node


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
        self.toc = toc
        self.footnotes = footnotes

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

    def _reduce(self, node, attributes, *args, **kwargs):
        for attribute in attributes:
            node[attribute] = self.visit(node[attribute], *args, **kwargs)

    def _reducelist(self, node, attributes, join_with=None, *args, **kwargs):
        for attribute in attributes:
            node[attribute] = self.visitlist(
                node[attribute], join_with, *args, **kwargs
            )

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

        if node["type"] == "command":
            method_name = f'_visit_command_{node["name"]}'
        else:
            method_name = f'_visit_{node["type"]}'

        try:
            method = getattr(self, method_name)
        except AttributeError:
            method = return_node

        node = method(node, *args, **kwargs)

        node_types = []
        node_types.extend(node.pop("node_types", []))
        node_types.append(node["type"])

        for i in node_types:
            try:
                return self._render(i, **node)
            except TemplateNotFound:
                continue

        raise ValueError(f"Cannot find any suitable template among {node_types}")

    def visitlist(self, nodes, join_with=None, *args, **kwargs):
        visited_nodes = [self.visit(i, *args, **kwargs) for i in nodes]

        if join_with is not None:
            return join_with.join(visited_nodes)

        return visited_nodes

    def _visit_block(self, node):
        node["node_types"] = [f'block-{node["blocktype"]}']
        self._reducelist(node, ["content"], join_with="")
        self._reduce(node, ["title"])
        return node

    def _visit_class(self, node):
        self._reduce(node, ["content"])
        return node

    def _visit_container_node(self, node):
        node["node_types"] = ["container"]
        node["content"] = "".join(self.visitlist(node["content"]))
        return node

    def _visit_content_image(self, node):
        node["node_types"] = ["image"]
        self._reduce(node, ["title"])
        return node

    def _visit_document(self, node):
        self._reducelist(node, ["content"], join_with="")
        return node

    def _visit_footnote_def(self, node):
        self._reducelist(node, ["content"], join_with="")
        return node

    def _visit_image(self, node):
        node["node_types"] = ["inline_image"]
        return node

    def _visit_list(self, node):
        self._reducelist(node, ["items"], join_with="")
        return node

    def _visit_list_item(self, node):
        self._reduce(node, ["content"])
        return node

    def _visit_paragraph(self, node):
        self._reduce(node, ["content"])
        return node

    def _visit_quote(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")
        return node

    def _visit_raw(self, node):
        node["content"] = self.visitlist(node["content"], join_with="\n")
        return node

    def _visit_sentence(self, node):
        node["content"] = "".join(self.visitlist(node["content"]))
        return node

    def _visit_style(self, node):
        node["node_types"] = [node["value"]]
        self._reduce(node, ["content"])
        return node

    def _visit_toc_entry(self, node):
        self._reducelist(node, ["children"], join_with="")
        return node

    def _visit_verbatim(self, node):
        node["content"] = node["value"]
        return node
