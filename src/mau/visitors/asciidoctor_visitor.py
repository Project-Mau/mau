import copy

from mau.visitors.visitor import Visitor

DEFAULT_TEMPLATES = {
    "block-admonition.adoc": "[{{ kwargs.class }}{% if kwargs.icon %}.{{ kwargs.icon }}{% endif %}]\n====\n{{ content }}====\n",
    "block.adoc": "--\n{{ content }}\n--",
    "block-source.adoc": "{% if title %}.{{ title }}\n{% endif %}[source{% if kwargs.language %},{{ kwargs.language }}{% endif %}]\n----\n{{ content }}\n----\n{% if kwargs.callouts %}{% for callout in kwargs.callouts %}{{ callout[0] }} {{ callout[1] }}{% endfor %}\n{% endif %}",
    "callout.adoc": "<{{ name }}>",
    "class.adoc": """[{{ classes }}]#{{ content }}#""",
    "command.adoc": "{{ content }}",
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
    "block-quote.adoc": '[quote, "{% if kwargs.attribution %}{{ kwargs.attribution }}{% else %}{{ secondary_content }}{% endif %}"]\n____\n{{ content }}____\n',
    "sentence.adoc": "{{ content }}",
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
        classes = " ".join([f".{cls}" for cls in node["classes"]])
        node["classes"] = classes
        return super()._visit_class(node)

    def _visit_link(self, node):
        if node["text"] == node["target"]:
            node["text"] = None
        return node

    def _visit_header(self, node):
        node["header"] = "=" * int(node["level"])
        return node

    def _visit_block_admonition(self, node):
        if node["kwargs"]["class"] in [
            "note",
            "tip",
            "important",
            "caution",
            "warning",
        ]:
            node["kwargs"]["class"] = node["kwargs"]["class"].upper()
        else:
            raise ValueError(
                f"""Admonition {node["kwargs"]["class"]} cannot be converted"""
            )

        return node

    def _visit_block_engine_source(self, node):
        src = node["content"].split("\n")

        # Inject callout markers in the highlighted code
        callout_markers = node["kwargs"]["callouts"]["markers"]
        callout_contents = node["kwargs"]["callouts"]["contents"]

        for linenum, callout_name in callout_markers.items():
            src[linenum] = "{line} {callout}".format(
                line=src[linenum],
                callout=self._render("callout", name=callout_name),
            )

        callouts_list = [
            (self._render("callout", name=name), text)
            for name, text in callout_contents.items()
        ]

        node["content"] = "\n".join(src)
        node["kwargs"]["callouts"] = callouts_list

        return node

    def _visit_document(self, node):
        self._reducelist(node, ["content"], join_with="\n")
        return node

    def _visit_list_item(self, node, ordered=False):
        mark = "*"
        if ordered:
            mark = "."

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

    def _visit_footnote_ref(self, node):
        node["node_types"] = (["footnote_ref"],)
        self._reducelist(node, ["content"], join_with="")
        return node

    def _visit_content_image(self, node):
        node["node_types"] = ["image"]
        node["asciidoctor_classes"] = node["kwargs"].get("asciidoctor_classes", None)
        self._reduce(node, ["title"])
        return node

    def _visit_image(self, node):
        node["node_types"] = ["inline_image"]
        return node
