from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

from mau.visitors.visitor import Visitor, TemplateNotFound

DEFAULT_TEMPLATES = {
    "admonition.html": '<div class="{{ admclass }}"><table><tbody><tr><td class="icon"><i class="fa icon-{{ icon }}" title="{{ label }}"></i></td><td class="content">{{ content|join }}</td></tr></tbody></table></div>',
    "block.html": '<div{% if kwargs["classes"] %} class="{{ kwargs["classes"] }}"{% endif %}>{% if title %}<div class="title">{{ title }}</div>{% endif %}<div class="content">{{ content|join }}</div></div>',
    "quote.html": '<blockquote><div class="content">{{ content|join }}</div></blockquote><div class="attribution">{{ attribution }}</div>',
    "source.html": '<div class="source">{% if title %}<div class="title">{{ title }}</div>{% endif %}<div class="content">{{ code }}</div></div>{% if callouts %}<div class="colist arabic"><table><tbody>{% for callout in callouts %}<tr><td>{{ callout[0] }}</td><td>{{ callout[1] }}</td></tr>{% endfor %}</tbody></table></div>{% endif %}',
    "callout.html": '<i class="conum" data-value="{{ name }}"></i><b>({{ name }})</b>',
    "class.html": """<span class="{{ classes|join(' ') }}">{{ text }}</span>""",
    "document.html": "<html><head></head><body>{{ content|join() }}</body></html>",
    "footnote_def.html": '<div id="{{ defanchor }}"><a href="#{{ refanchor }}">{{ number }}</a> {{ text|join }}</div>',
    "footnote_ref.html": '<sup>[<a id="{{ refanchor }}" href="#{{ defanchor }}">{{ number }}</a>]</sup>',
    "footnotes.html": '<div id="_footnotes">{{ entries|join }}</div>',
    "header.html": '<h{{ level }} id="{{ anchor }}">{% if id %}<a id="{{ id }}"></a>{% endif %}{{ value }}</h{{ level }}>',
    "horizontal_rule.html": "<hr>",
    "image.html": '<div class="imageblock"><div class="content"><img src="{{ uri }}"{% if alt_text %} alt="{{ alt_text }}"{% endif %}>{% if title %}<div class="title">{{ title|join }}</div>{% endif %}</div></div>',
    "inline_image.html": '<span class="image"><img src="{{ uri }}"{%if alt_text %} alt="{{ alt_text }}"{% endif %}></span>',
    "link.html": '<a href="{{ target }}">{{ text }}</a>',
    "list.html": "<{% if ordered %}ol{% else %}ul{% endif %}>{{ items|join }}</{% if ordered %}ol{% else %}ul{% endif %}>",
    "list_item.html": "<li>{{ content }}</li>",
    "paragraph.html": "<p>{{ text }}</p>",
    "raw.html": "{{ content }}",
    "star.html": "<strong>{{ text }}</strong>",
    "toc_entry.html": '<li><a href="#{{ anchor }}">{{ text }}</a>{% if children %}<ul>{{ children|join }}</ul>{% endif %}</li>',
    "toc.html": "<ul>{% if entries%}{{ entries|join }}{% endif %}</ul>",
    "underscore.html": "<em>{{ text }}</em>",
    "verbatim.html": "<code>{{ text }}</code>",
}


class HTMLVisitor(Visitor):
    _template_extension = ".html"

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
        return self._render("class", classes=node["classes"], text=text)

    def _visit_link(self, node):
        return self._render("link", text=node["text"], target=node["target"])

    def _visit_header(self, node):
        return self._render(
            "header",
            level=node["level"],
            value=node["value"],
            anchor=node["anchor"],
        )

    def _visit_quote(self, node):
        return self._render(
            "quote",
            attribution=node["attribution"],
            content=self.visitlist(node["content"]),
        )

    def _visit_raw(self, node):
        return self._render(
            "raw",
            content="\n".join(self.visitlist(node["content"])),
        )

    def _visit_admonition(self, node):
        admclass = node["class"]
        icon = node["icon"]
        label = node["label"]
        content = self.visitlist(node["content"])

        templates = [
            f"admonition_{admclass}",
            "admonition",
        ]

        for t in templates:
            try:
                return self._render(
                    t,
                    admclass=admclass,
                    icon=icon,
                    label=label,
                    content=content,
                )
            except TemplateNotFound:
                continue

        raise ValueError(
            "Cannot find any suitable template among "
            + ", ".join([f"{i}.html" for i in templates])
        )

    def _visit_block(self, node):
        return self._render(
            "block",
            content=self.visitlist(node["content"]),
            title=self.visit(node["title"]),
            kwargs=node["kwargs"],
        )

    def _visit_source(self, node):
        lexer = get_lexer_by_name(node["language"])
        formatter = get_formatter_by_name("html")
        src = "\n".join([i["value"] for i in node["code"]])

        highlighted_src = highlight(src, lexer, formatter)

        highlighted_src_lines = highlighted_src.split("\n")

        callouts = {}
        for linenum, callout in node["callouts"].items():
            callout_name, callout_text = callout
            highlighted_src_lines[linenum] = "{line} {callout}".format(
                line=highlighted_src_lines[linenum],
                callout=self._render("callout", name=callout_name),
            )
            callouts[callout_name] = callout_text

        highlighted_src = "\n".join(highlighted_src_lines)
        callouts_list = [
            (self._render("callout", name=name), text)
            for name, text in callouts.items()
        ]

        return self._render(
            "source",
            code=highlighted_src,
            callouts=callouts_list,
            title=self.visit(node["title"]),
        )

    def _visit_document(self, node):
        return self._render(
            "document", content=[self.visit(item) for item in node["content"]]
        )

    def _visit_list_item(self, node):
        return self._render("list_item", content=self.visit(node["content"]))

    def _visit_list(self, node):
        return self._render(
            "list",
            ordered=node["ordered"],
            items=[self.visit(i) for i in node["items"]],
        )

    def _visit_toc_entry(self, node):
        return self._render(
            "toc_entry",
            anchor=node["anchor"],
            text=node["value"],
            children=[self._visit_toc_entry(i) for i in node["children"]],
        )

    def visit_toc(self, nodes):
        return self._render("toc", entries=[self._visit_toc_entry(i) for i in nodes])

    def _visit_footnote(self, node):
        return self._render(
            "footnote_ref",
            number=node["number"],
            refanchor=node["refanchor"],
            defanchor=node["defanchor"],
        )

    def _visit_footnote_def(self, node):
        return self._render(
            "footnote_def",
            number=node["number"],
            refanchor=node["refanchor"],
            defanchor=node["defanchor"],
            text=[self.visit(i) for i in node["content"]],
        )

    def visit_footnotes(self, nodes):
        entries = [self._visit_footnote_def(i) for i in nodes]

        return self._render("footnotes", entries=entries)

    def _visit_command(self, node):
        if node["name"] == "toc":
            return self.visit_toc(self.toc)

        if node["name"] == "footnotes":
            return self.visit_footnotes(self.footnotes)

    def _visit_content_image(self, node):
        return self._render(
            "image",
            uri=node["uri"],
            title=self.visit(node["title"]),
            alt_text=node["alt_text"],
        )

    def _visit_image(self, node):
        return self._render(
            "inline_image",
            uri=node["uri"],
            alt_text=node["alt_text"],
        )

    def _visit_macro(self, node):
        return ""
