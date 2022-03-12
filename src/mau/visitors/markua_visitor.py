import copy

from mau.visitors.visitor import Visitor

DEFAULT_TEMPLATES = {
    "block-admonition.md": "{blurb, class: {{ kwargs.class }}}\n**{{ kwargs.label }}**\n\n{{ content }}{/blurb}\n\n",
    "block.md": "{{ content }}",
    "block-source.md": '{% if title %}{caption: "{{ title }}"}\n{% endif %}``` {% if kwargs.language %}{{ kwargs.language }}{% endif %}\n{{ content }}\n```',
    "callout.md": "",
    "class.md": "{{ content }}",
    "command.md": "{{ content }}",
    "document.md": "{{ content }}",
    "footnote_def.md": "[^footnote_{{ refanchor }}_{{ number }}]: {{ content }}\n",
    "footnote_ref.md": "[^footnote_{{ refanchor }}_{{ number }}]",
    "footnotes.md": "{{ entries }}",
    "header.md": "{{ header }} {{ value }}\n",
    "horizontal_rule.md": "* * *",
    "image.md": '{% if alt_text %}{alt: "{{ alt_text }}"}\n{% endif %}![{{ title }}]({{ uri }})\n',
    "inline_image.md": "![{{ alt_text }}]({{ uri }})",
    "link.md": "{% if text %}[{{ text }}]({{ target }}){% else %}<{{ target }}>{% endif %}",
    "list.md": "{{ items }}{% if main_node %}\n{% endif %}",
    "list_item.md": "{% if not main_node %}\n{% endif %}{% if prefix %}{{ prefix }} {% endif %}{{ content }}",
    "paragraph.md": "{{ content }}\n",
    "block-quote.md": "{blurb, icon: quote-right}\n{{ content }}\n{% if kwargs.attribution %}{{ kwargs.attribution }}{% else %}{{ secondary_content }}{% endif %}\n{/blurb}\n\n",
    "sentence.md": "{{ content }}",
    "star.md": "**{{ content }}**",
    "text.md": "{{ value }}",
    "underscore.md": "*{{ content }}*",
    "verbatim.md": "`{{ content }}`",
}


class MarkuaVisitor(Visitor):
    _template_extension = ".md"
    _environment_options = {"keep_trailing_newline": True}

    def __init__(
        self,
        default_templates=None,
        custom_templates=None,
        templates_directory=None,
        config=None,
        toc=None,
        footnotes=None,
    ):
        default_templates = (
            copy.deepcopy(default_templates)
            if default_templates is not None
            else copy.deepcopy(DEFAULT_TEMPLATES)
        )

        super().__init__(
            default_templates=default_templates,
            custom_templates=custom_templates,
            templates_directory=templates_directory,
            config=config,
            toc=toc,
            footnotes=footnotes,
        )

    def _visit_class(self, node):
        classes = [f".{cls}" for cls in node["classes"]]
        node["classes"] = classes
        return super()._visit_class(node)

    def _visit_link(self, node):
        if node["text"] == node["target"]:
            node["text"] = None
        return node

    def _visit_header(self, node):
        node["header"] = "#" * int(node["level"])
        return node

    def _visit_block_admonition(self, node):
        if node["kwargs"]["class"] == "note":
            node["kwargs"]["class"] = "tip"

        if node["kwargs"]["class"] not in [
            "discussion",
            "error",
            "information",
            "tip",
            "warning",
        ]:
            raise ValueError(
                f"""Admonition {node["kwargs"]["class"]} cannot be converted"""
            )

        return node

    def _visit_block_engine_source(self, node):
        node["kwargs"]["callouts"] = []

        return node

    def _visit_document(self, node):
        self._reducelist(node, ["content"], join_with="\n")
        return node

    def _visit_list_item(self, node, ordered=False):
        mark = "*"

        prefix = None
        if node["content"]["type"] != "list":
            prefix = mark * int(node["level"])

        self._reduce(node, ["content"])
        node["prefix"] = prefix
        return node

    def _visit_list(self, node, ordered=False):
        node["items"] = "".join(
            [self.visit(i, ordered=node["ordered"]) for i in node["items"]]
        )
        return node

    def _visit_command_footnotes(self, node):
        footnotes_node = self.footnotes.asdict()
        self._reducelist(footnotes_node, ["entries"], join_with="")

        return footnotes_node
