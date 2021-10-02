from mau.visitors.visitor import Visitor

DEFAULT_TEMPLATES = {
    "admonition.md": "{blurb, class: {{ class }}}\n**{{ label }}**\n\n{{ content }}{/blurb}\n\n",
    "block.md": "{{ content }}",
    "callout.md": "",
    "class.md": "{{ content }}",
    "command.md": "{{ content }}",
    "document.md": "{{ content }}",
    "footnote_def.md": "[^footnote{{ number }}]: {{ content }}",
    "footnote_ref.md": "[^footnote{{ number }}]",
    "footnotes.md": "{{ entries }}",
    "header.md": "{{ header }} {{ value }}\n",
    "horizontal_rule.md": "* * *",
    "image.md": '{% if alt_text %}{alt: "{{ alt_text }}"}\n{% endif %}![{{ title }}]({{ uri }})\n',
    "inline_image.md": "![{{ alt_text }}]({{ uri }})",
    "link.md": "{% if text %}[{{ text }}]({{ target }}){% else %}<{{ target }}>{% endif %}",
    "list.md": "{{ items }}{% if main_node %}\n{% endif %}",
    "list_item.md": "{% if not main_node %}\n{% endif %}{% if prefix %}{{ prefix }} {% endif %}{{ content }}",
    "paragraph.md": "{{ content }}\n",
    "quote.md": "{blurb, icon: quote-right}\n{{ content }}\n{{ attribution }}\n{/blurb}\n\n",
    "sentence.md": "{{ content }}",
    "source.md": '{% if title %}{caption: "{{ title }}"}\n{% endif %}``` {% if language %}{{ language }}{% endif %}\n{{ code }}\n```',
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
        templates_directory=None,
        config=None,
        toc=None,
        footnotes=None,
    ):
        super().__init__(
            default_templates=DEFAULT_TEMPLATES,
            templates_directory=templates_directory,
            config=config,
            toc=toc,
            footnotes=footnotes,
        )

    def _visit_sentence(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

    def _visit_paragraph(self, node):
        node["content"] = self.visit(node["content"])

    def _visit_class(self, node):
        classes = [f".{cls}" for cls in node["classes"]]
        node["classes"] = classes
        node["content"] = self.visit(node["content"])

    def _visit_link(self, node):
        if node["text"] == node["target"]:
            node["text"] = None

    def _visit_header(self, node):
        node["header"] = "#" * int(node["level"])

    def _visit_quote(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

    def _visit_admonition(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

        if node["class"] == "note":
            node["class"] = "tip"

        if node["class"] not in [
            "discussion",
            "error",
            "information",
            "tip",
            "warning",
        ]:
            raise ValueError(f"""Admonition {node["class"]} cannot be converted""")

    def _visit_block(self, node):
        node["content"] = self.visitlist(node["content"], join_with="\n")
        node["title"] = self.visit(node["title"])

    def _visit_source(self, node):
        src = [i["value"] for i in node["code"]]

        src = "\n".join(src)
        callouts_list = []

        node["code"] = src
        node["title"] = self.visit(node["title"])
        node["callouts"] = callouts_list

    def _visit_document(self, node):
        node["content"] = self.visitlist(node["content"], join_with="\n")

    def _visit_list_item(self, node, ordered=False):
        mark = "*"

        prefix = None
        if node["content"]["type"] != "list":
            prefix = mark * int(node["level"])

        node["content"] = self.visit(node["content"])
        node["prefix"] = prefix

    def _visit_list(self, node, ordered=False):
        node["items"] = "".join(
            [self.visit(i, ordered=node["ordered"]) for i in node["items"]]
        )

    def _visit_footnote_def(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

    def _visit_content_image(self, node):
        node["node_types"] = ["image"]
        node["title"] = self.visit(node["title"])

    def _visit_image(self, node):
        node["node_types"] = ["inline_image"]

    def _visit_command(self, node):
        if node["name"] == "footnotes":
            node["content"] = "".join(
                self._render(
                    "footnotes",
                    entries=self.visitlist(self.footnote_defs, join_with=""),
                )
            )
