from mau.visitors.visitor import Visitor

DEFAULT_TEMPLATES = {
    "admonition.adoc": "[{{ class }}{% if icon %}.{{ icon }}{% endif %}]\n====\n{{ content }}====\n",
    "block.adoc": "--\n{{ content }}\n--",
    "callout.adoc": "<{{ name }}>",
    "class.adoc": """[{{ classes }}]#{{ content }}#""",
    "document.adoc": "{{ content }}",
    "footnote_ref.adoc": "footnote:[{{ content }}]",
    "header.adoc": "{{ header }} {{ value }}\n",
    "horizontal_rule.adoc": "---\n",
    "image.adoc": "{% if asciidoctor_classes %}[{{ asciidoctor_classes }}]\n{% endif %}{% if title %}.{{ title }}\n{% endif %}image::{{ uri }}[{% if alt_text %}{{ alt_text }}{% endif %}]\n",
    "inline_image.adoc": "image::{{ uri }}{%if alt_text %}[{{ alt_text }}]{% endif %}",
    "link.adoc": "{{ target }}{% if text %}[{{ text }}]{% endif %}",
    "list.adoc": "{{ items }}{% if main_node %}\n{% endif %}",
    "list_item.adoc": "{% if not main_node %}\n{% endif %}{% if prefix %}{{ prefix }} {% endif %}{{ content }}",
    "paragraph.adoc": "{{ content }}\n",
    "quote.adoc": '[quote, "{{ attribution }}"]\n____\n{{ content }}____\n',
    "sentence.adoc": "{{ content }}",
    "source.adoc": "{% if title %}.{{ title }}\n{% endif %}[source{% if language %},{{ language }}{% endif %}]\n----\n{{ code }}\n----\n{% if callouts %}{% for callout in callouts %}{{ callout[0] }} {{ callout[1] }}{% endfor %}\n{% endif %}",
    "star.adoc": "*{{ content }}*",
    "text.adoc": "{{ value }}",
    "underscore.adoc": "_{{ content }}_",
    "verbatim.adoc": "`{{ content }}`",
}


class AsciidoctorVisitor(Visitor):
    _template_extension = ".adoc"
    _environment_options = {"keep_trailing_newline": True}

    def __init__(
        self,
        default_templates=DEFAULT_TEMPLATES,
        templates_directory=None,
        config=None,
        toc=None,
        footnotes=None,
    ):
        super().__init__(
            default_templates=default_templates,
            templates_directory=templates_directory,
            config=config,
            toc=toc,
            footnotes=footnotes,
        )

    def _visit_class(self, node):
        classes = " ".join([f".{cls}" for cls in node["classes"]])
        node["classes"] = classes
        node["content"] = self.visit(node["content"])

    def _visit_link(self, node):
        if node["text"] == node["target"]:
            node["text"] = None

    def _visit_header(self, node):
        node["header"] = "=" * int(node["level"])

    def _visit_quote(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

    def _visit_admonition(self, node):
        node["content"] = self.visitlist(node["content"], join_with="")

        if node["class"] in ["note", "tip", "important", "caution", "warning"]:
            node["class"] = node["class"].upper()
        else:
            raise ValueError(f"""Admonition {node["class"]} cannot be converted""")

    def _visit_block(self, node):
        node["content"] = self.visitlist(node["content"], join_with="\n")

    def _visit_source(self, node):
        src = [i["value"] for i in node["code"]]

        # Inject callout markers in the highlighted code
        callout_markers = node["callouts"]["markers"]
        callout_contents = node["callouts"]["contents"]

        for linenum, callout_name in callout_markers.items():
            src[linenum] = "{line} {callout}".format(
                line=src[linenum],
                callout=self._render("callout", name=callout_name),
            )

        src = "\n".join(src)
        callouts_list = [
            (self._render("callout", name=name), text)
            for name, text in callout_contents.items()
        ]

        node["code"] = src
        node["title"] = self.visit(node["title"])
        node["callouts"] = callouts_list

    def _visit_document(self, node):
        node["content"] = self.visitlist(node["content"], join_with="\n")

    def _visit_list_item(self, node, ordered=False):
        mark = "*"
        if ordered:
            mark = "."

        prefix = None
        if node["content"]["type"] != "list":
            prefix = mark * int(node["level"])

        node["content"] = self.visit(node["content"])
        node["prefix"] = prefix

    def _visit_list(self, node, ordered=False):
        node["items"] = "".join(
            [self.visit(i, ordered=node["ordered"]) for i in node["items"]]
        )

    def _visit_footnote_ref(self, node):
        number = node["number"]
        footnote = [i for i in self.footnote_defs if i["number"] == number][0]

        node["node_types"] = (["footnote_ref"],)
        node["content"] = self.visitlist(footnote["content"], join_with="")

    def _visit_content_image(self, node):
        node["node_types"] = ["image"]
        node["title"] = self.visit(node["title"])
        node["asciidoctor_classes"] = node["kwargs"].get("asciidoctor_classes", None)

    def _visit_image(self, node):
        node["node_types"] = ["inline_image"]
