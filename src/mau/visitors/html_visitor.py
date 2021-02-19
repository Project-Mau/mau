from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

from mau.visitors.visitor import Visitor, TemplateNotFound

DEFAULT_TEMPLATES = {
    "admonition.html": '<div class="{{ admclass }}"><table><tbody><tr><td class="icon"><i class="fa icon-{{ icon }}" title="{{ label }}"></i></td><td class="content">{{ content|join }}</td></tr></tbody></table></div>',
    "block.html": '<div{% if kwargs["classes"] %} class="{{ kwargs["classes"] }}"{% endif %}>{% if title %}<div class="title">{{ title }}</div>{% endif %}<div class="content">{{ content|join }}</div></div>',
    "callout.html": '<i class="conum" data-value="{{ name }}"></i><b>({{ name }})</b>',
    "class.html": """<span class="{{ classes|join(' ') }}">{{ content }}</span>""",
    "command.html": "{{ content }}",
    "document.html": "<html><head></head><body>{{ content|join() }}</body></html>",
    "footnote_def.html": '<div id="{{ defanchor }}"><a href="#{{ refanchor }}">{{ number }}</a> {{ text }}</div>',
    "footnote_ref.html": '<sup>[<a id="{{ refanchor }}" href="#{{ defanchor }}">{{ number }}</a>]</sup>',
    "footnotes.html": '<div id="_footnotes">{{ entries|join }}</div>',
    "header.html": '<h{{ level }} id="{{ anchor }}">{% if id %}<a id="{{ id }}"></a>{% endif %}{{ value }}</h{{ level }}>',
    "horizontal_rule.html": "<hr>",
    "image.html": '<div class="imageblock"><div class="content"><img src="{{ uri }}"{% if alt_text %} alt="{{ alt_text }}"{% endif %}>{% if title %}<div class="title">{{ title|join }}</div>{% endif %}</div></div>',
    "inline_image.html": '<span class="image"><img src="{{ uri }}"{%if alt_text %} alt="{{ alt_text }}"{% endif %}></span>',
    "link.html": '<a href="{{ target }}">{{ text }}</a>',
    "list.html": "<{% if ordered %}ol{% else %}ul{% endif %}>{{ items|join }}</{% if ordered %}ol{% else %}ul{% endif %}>",
    "list_item.html": "<li>{{ content }}</li>",
    "macro.html": "",
    "paragraph.html": "<p>{{ content }}</p>",
    "quote.html": '<blockquote><div class="content">{{ content|join }}</div></blockquote><div class="attribution">{{ attribution }}</div>',
    "raw.html": "{{ content }}",
    "sentence.html": "{{ content }}",
    "source.html": '<div class="source">{% if title %}<div class="title">{{ title }}</div>{% endif %}<div class="content">{{ code }}</div></div>{% if callouts %}<div class="colist arabic"><table><tbody>{% for callout in callouts %}<tr><td>{{ callout[0] }}</td><td>{{ callout[1] }}</td></tr>{% endfor %}</tbody></table></div>{% endif %}',
    "star.html": "<strong>{{ content }}</strong>",
    "text.html": "{{ value }}",
    "toc.html": "<ul>{% if entries%}{{ entries|join }}{% endif %}</ul>",
    "toc_entry.html": '<li><a href="#{{ anchor }}">{{ text }}</a>{% if children %}<ul>{{ children|join }}</ul>{% endif %}</li>',
    "underscore.html": "<em>{{ content }}</em>",
    "verbatim.html": "<code>{{ content }}</code>",
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
        return {"classes": node["classes"], "content": self.visit(node["content"])}

    def _visit_link(self, node):
        return {"text": node["text"], "target": node["target"]}

    def _visit_header(self, node):
        return {
            "level": node["level"],
            "value": node["value"],
            "anchor": node["anchor"],
        }

    def _visit_quote(self, node):
        return {
            "attribution": node["attribution"],
            "content": self.visitlist(node["content"]),
        }

    def _visit_raw(self, node):
        return {"content": "\n".join(self.visitlist(node["content"]))}

    def _visit_admonition(self, node):
        return {
            "node_types": [
                f'admonition_{node["class"]}',
                "admonition",
            ],
            "admclass": node["class"],
            "icon": node["icon"],
            "label": node["label"],
            "content": self.visitlist(node["content"]),
        }

    def _visit_block(self, node):
        return {
            "content": self.visitlist(node["content"]),
            "title": self.visit(node["title"]),
            "kwargs": node["kwargs"],
        }

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

        return {
            "code": highlighted_src,
            "callouts": callouts_list,
            "title": self.visit(node["title"]),
        }

    def _visit_document(self, node):
        return {"content": [self.visit(item) for item in node["content"]]}

    def _visit_list_item(self, node):
        return {"content": self.visit(node["content"])}

    def _visit_list(self, node):
        return {
            "ordered": node["ordered"],
            "items": [self.visit(i) for i in node["items"]],
        }

    def _visit_toc_entry(self, node):
        return {
            "anchor": node["anchor"],
            "text": node["text"],
            "children": [self.visit(i) for i in node["children"]],
        }

    def visit_toc(self, nodes):
        keys = {"entries": [self.visit(i) for i in nodes]}
        return self._render("toc", **keys)

    def _visit_footnote_ref(self, node):
        return {
            "node_types": ["footnote_ref"],
            "number": node["number"],
            "refanchor": node["refanchor"],
            "defanchor": node["defanchor"],
        }

    def _visit_footnote_def(self, node):
        return {
            "number": node["number"],
            "refanchor": node["refanchor"],
            "defanchor": node["defanchor"],
            "text": "".join([self.visit(i) for i in node["content"]]),
        }

    def visit_footnotes(self, nodes):
        keys = {"entries": [self.visit(i) for i in nodes]}
        return self._render("footnotes", **keys)

    def _visit_command(self, node):
        if node["name"] == "toc":
            return {"content": "".join(self.visit_toc(self.toc))}

        if node["name"] == "footnotes":
            return {"content": "".join(self.visit_footnotes(self.footnotes))}

    def _visit_content_image(self, node):
        return {
            "node_types": ["image"],
            "uri": node["uri"],
            "title": self.visit(node["title"]),
            "alt_text": node["alt_text"],
        }

    def _visit_image(self, node):
        return {
            "node_types": ["inline_image"],
            "uri": node["uri"],
            "alt_text": node["alt_text"],
        }

    def _visit_macro(self, node):
        return {}
