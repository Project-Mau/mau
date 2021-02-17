from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

from mau.visitors.visitor import Visitor, TemplateNotFound

DEFAULT_TEMPLATES = {
    "admonition.adoc": "[{{ admclass }}{% if icon %}.{{ icon }}{% endif %}]\n====\n{{ content|join }}====\n",
    "block.adoc": "--\n{{ content|join('\n') }}\n--",
    "callout.adoc": "<{{ name }}>",
    "class.adoc": """[{{ classes|join(' ') }}]#{{ text }}#""",
    "document.adoc": "{{ content|join('\n') }}",
    "footnote_ref.adoc": "footnote:[{{ text|join }}]",
    "header.adoc": "{{ header }} {{ text }}\n",
    "horizontal_rule.adoc": "---\n",
    "image.adoc": "{% if asciidoctor_classes %}[{{ asciidoctor_classes }}]\n{% endif %}{% if title %}.{{ title }}\n{% endif %}image::{{ uri }}[{% if alt_text %}{{ alt_text }}{% endif %}]\n",
    "inline_image.adoc": "image::{{ uri }}{%if alt_text %}[{{ alt_text }}]{% endif %}",
    "link.adoc": "{{ target }}{% if text %}[{{ text }}]{% endif %}",
    "list.adoc": "{{ items|join('\n') }}{% if main_node %}\n{% endif %}",
    "list_item.adoc": "{{ prefix }} {{ content }}",
    "paragraph.adoc": "{{ text }}\n",
    "quote.adoc": '[quote, "{{ attribution }}"]\n____\n{{ content|join }}____\n',
    "source.adoc": "{% if title %}.{{ title }}\n{% endif %}[source{% if language %},{{ language }}{% endif %}]\n----\n{{ code }}\n----\n{% if callouts %}{% for callout in callouts %}{{ callout[0] }} {{ callout[1] }}{% endfor %}\n{% endif %}",
    "star.adoc": "*{{ text }}*",
    "underscore.adoc": "_{{ text }}_",
    "verbatim.adoc": "`{{ text }}`",
}


class AsciidoctorVisitor(Visitor):
    _template_extension = ".adoc"
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

    def _visit_text(self, node):
        return node["value"]

    def _visit_sentence(self, node):
        return "".join([self.visit(t) for t in node["content"]])

    def _visit_paragraph(self, node):
        return self._render("paragraph", text=self.visit(node["content"]))

    def _visit_horizontal_rule(self, node):
        return self._render("horizontal_rule")

    def _visit_style(self, node):
        content = self.visit(node["content"])
        return self._render(node["value"], text=content)

    def _visit_verbatim(self, node):
        return self._render("verbatim", text=node["value"])

    def _visit_class(self, node):
        text = self.visit(node["content"])
        classes = [f".{cls}" for cls in node["classes"]]
        return self._render("class", classes=classes, text=text)

    def _visit_link(self, node):
        text = node["text"]
        target = node["target"]

        if text == target:
            text = None

        return self._render("link", text=text, target=target)

    def _visit_header(self, node):
        return self._render(
            "header", header="=" * int(node["level"]), text=node["value"]
        )

    def _visit_quote(self, node):
        return self._render(
            "quote",
            attribution=node["attribution"],
            content=self.visitlist(node["content"]),
        )

    def _visit_admonition(self, node):
        admclass = node["class"]
        content = self.visitlist(node["content"])

        if admclass in ["note", "tip", "important", "caution", "warning"]:
            admclass = admclass.upper()
        else:
            raise ValueError(f"Admonition {admclass} cannot be converted")

        return self._render(
            "admonition",
            admclass=admclass,
            icon=node["icon"],
            content=content,
        )

    def _visit_block(self, node):
        return self._render(
            "block",
            content=self.visitlist(node["content"]),
            title=self.visit(node["title"]),
            kwargs=node["kwargs"],
        )

    def _visit_source(self, node):
        src = [i["value"] for i in node["code"]]

        callouts = {}
        for linenum, callout in node["callouts"].items():
            callout_name, callout_text = callout
            src[linenum] = "{line} {callout}".format(
                line=src[linenum],
                callout=self._render("callout", name=callout_name),
            )
            callouts[callout_name] = callout_text

        src = "\n".join(src)
        callouts_list = [
            (self._render("callout", name=name), text)
            for name, text in callouts.items()
        ]

        return self._render(
            "source",
            code=src,
            title=self.visit(node["title"]),
            language=node["language"],
            callouts=callouts_list,
        )

    def _visit_document(self, node):
        return self._render(
            "document", content=[self.visit(item) for item in node["content"]]
        )

    def _visit_list_item(self, node, ordered=False):
        mark = "*"
        if ordered:
            mark = "."

        prefix = mark * int(node["level"])
        return self._render(
            "list_item", content=self.visit(node["content"]), prefix=prefix
        )

    def _visit_list(self, node, ordered=False):
        return self._render(
            "list",
            items=[self.visit(i, ordered=node["ordered"]) for i in node["items"]],
            main_node=node["main_node"],
        )

    def _visit_footnote(self, node):
        number = node["number"]
        footnote = [i for i in self.footnotes if i["number"] == number][0]
        return self._render(
            "footnote_ref", text=[self.visit(i) for i in footnote["content"]]
        )

    def _visit_content_image(self, node):
        return self._render(
            "image",
            uri=node["uri"],
            title=self.visit(node["title"]),
            asciidoctor_classes=node["kwargs"].get("asciidoctor_classes", None),
            alt_text=node["alt_text"],
        )

    def _visit_image(self, node):
        return self._render(
            "inline_image",
            uri=node["uri"],
            alt_text=node["alt_text"],
        )
