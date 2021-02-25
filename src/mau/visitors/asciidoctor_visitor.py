from mau.visitors.visitor import Visitor

DEFAULT_TEMPLATES = {
    "admonition.adoc": "[{{ admclass }}{% if icon %}.{{ icon }}{% endif %}]\n====\n{{ content|join }}====\n",
    "block.adoc": "--\n{{ content|join('\n') }}\n--",
    "callout.adoc": "<{{ name }}>",
    "class.adoc": """[{{ classes|join(' ') }}]#{{ content }}#""",
    "document.adoc": "{{ content|join('\n') }}",
    "footnote_ref.adoc": "footnote:[{{ text|join }}]",
    "header.adoc": "{{ header }} {{ text }}\n",
    "horizontal_rule.adoc": "---\n",
    "image.adoc": "{% if asciidoctor_classes %}[{{ asciidoctor_classes }}]\n{% endif %}{% if title %}.{{ title }}\n{% endif %}image::{{ uri }}[{% if alt_text %}{{ alt_text }}{% endif %}]\n",
    "inline_image.adoc": "image::{{ uri }}{%if alt_text %}[{{ alt_text }}]{% endif %}",
    "link.adoc": "{{ target }}{% if text %}[{{ text }}]{% endif %}",
    "list.adoc": "{{ items|join }}{% if main_node %}\n{% endif %}",
    "list_item.adoc": "{% if not main_node %}\n{% endif %}{% if prefix %}{{ prefix }} {% endif %}{{ content }}",
    "paragraph.adoc": "{{ content }}\n",
    "quote.adoc": '[quote, "{{ attribution }}"]\n____\n{{ content|join }}____\n',
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

    def _visit_class(self, node):
        classes = [f".{cls}" for cls in node["classes"]]
        return {"classes": classes, "content": self.visit(node["content"])}

    def _visit_link(self, node):
        text = node["text"]
        target = node["target"]

        if text == target:
            text = None

        return {"text": text, "target": node["target"]}

    def _visit_header(self, node):
        return {"header": "=" * int(node["level"]), "text": node["value"]}

    def _visit_quote(self, node):
        return {
            "attribution": node["attribution"],
            "content": self.visitlist(node["content"]),
        }

    def _visit_admonition(self, node):
        admclass = node["class"]
        content = self.visitlist(node["content"])

        if admclass in ["note", "tip", "important", "caution", "warning"]:
            admclass = admclass.upper()
        else:
            raise ValueError(f"Admonition {admclass} cannot be converted")

        return {
            "admclass": admclass,
            "icon": node["icon"],
            "content": content,
        }

    def _visit_block(self, node):
        return {
            "content": self.visitlist(node["content"]),
            "title": self.visit(node["title"]),
            "kwargs": node["kwargs"],
        }

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

        return {
            "code": src,
            "title": self.visit(node["title"]),
            "language": node["language"],
            "callouts": callouts_list,
        }

    def _visit_document(self, node):
        return {"content": [self.visit(item) for item in node["content"]]}

    def _visit_list_item(self, node, ordered=False):
        mark = "*"
        if ordered:
            mark = "."

        prefix = None
        if node["content"]["type"] != "list":
            prefix = mark * int(node["level"])

        return {"content": self.visit(node["content"]), "prefix": prefix}

    def _visit_list(self, node, ordered=False):
        return {
            "items": [self.visit(i, ordered=node["ordered"]) for i in node["items"]],
            "main_node": node["main_node"],
        }

    def _visit_footnote_ref(self, node):
        number = node["number"]
        footnote = [i for i in self.footnotes if i["number"] == number][0]

        return {
            "node_types": ["footnote_ref"],
            "text": [self.visit(i) for i in footnote["content"]],
        }

    def _visit_content_image(self, node):
        return {
            "node_types": ["image"],
            "uri": node["uri"],
            "title": self.visit(node["title"]),
            "asciidoctor_classes": node["kwargs"].get("asciidoctor_classes", None),
            "alt_text": node["alt_text"],
        }

    def _visit_image(self, node):
        return {
            "node_types": ["inline_image"],
            "uri": node["uri"],
            "alt_text": node["alt_text"],
        }
