import copy
import html

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

from mau.parsers import nodes
from mau.visitors.visitor import Visitor


DEFAULT_TEMPLATES = {
    "block-admonition.html": (
        '<div class="admonition {{ kwargs.class }}">'
        '<i class="{{ kwargs.icon }}"></i>'
        '<div class="content">'
        '<div class="title">{{ kwargs.label }}</div>'
        "<div>{{ content }}</div>"
        "</div></div>"
    ),
    "block.html": (
        '<div class="{{ blocktype }}{% if classes %} {{ classes }}{% endif %}">'
        '{% if title %}<div class="title">{{ title }}</div>{% endif %}'
        '<div class="content">{{ content }}</div>'
        "</div>"
    ),
    "block-source.html": (
        '<div{% if blocktype %} class="{{ blocktype }}"{% endif %}>'
        '{% if title %}<div class="title">{{ title }}</div>{% endif %}'
        '<div class="content">{{ content }}</div>'
        '{% if kwargs.callouts %}<div class="callouts">'
        "<table><tbody>"
        "{% for callout in kwargs.callouts %}<tr>"
        "<td>{{ callout[0] }}</td>"
        "<td>{{ callout[1] }}</td>"
        "</tr>{% endfor %}"
        "</tbody></table>"
        "</div>{% endif %}"
        "</div>"
    ),
    "callout.html": '<span class="callout">{{ name }}</span>',
    "class.html": '<span class="{{ classes }}">{{ content }}</span>',
    "command.html": "{{ content }}",
    "container.html": "{{ content }}",
    "document.html": "<html><head></head><body>{{ content }}</body></html>",
    "footnote_def.html": (
        '<div id="{{ defanchor }}">'
        '<a href="#{{ refanchor }}">{{ number }}</a> {{ content }}</div>'
    ),
    "footnote_ref.html": (
        "<sup>"
        '[<a id="{{ refanchor }}" href="#{{ defanchor }}">{{ number }}</a>]'
        "</sup>"
    ),
    "footnotes.html": '<div id="_footnotes">{{ entries }}</div>',
    "header.html": '<h{{ level }} id="{{ anchor }}">{{ value }}</h{{ level }}>',
    "horizontal_rule.html": "<hr>",
    "image.html": (
        '<div class="imageblock">'
        '<div class="content">'
        '<img src="{{ uri }}"{% if alt_text %} alt="{{ alt_text }}"{% endif %} />'
        '{% if title %}<div class="title">{{ title }}</div>{% endif %}'
        "</div></div>"
    ),
    "inline_image.html": (
        '<span class="image">'
        '<img src="{{ uri }}"{%if alt_text %} alt="{{ alt_text }}"{% endif %}>'
        "</span>"
    ),
    "link.html": '<a href="{{ target }}">{{ text }}</a>',
    "list.html": (
        "<{% if ordered %}ol{% else %}ul{% endif %}>"
        "{{ items }}"
        "</{% if ordered %}ol{% else %}ul{% endif %}>"
    ),
    "list_item.html": "<li>{{ content }}</li>",
    "macro.html": "",
    "paragraph.html": "<p>{{ content }}</p>",
    "block-quote.html": (
        "<blockquote>"
        "{{ content }}"
        "<cite>{% if kwargs.attribution %}{{ kwargs.attribution }}{% else %}{{ secondary_content }}{% endif %}</cite>"
        "</blockquote>"
    ),
    "raw.html": "{{ content }}",
    "sentence.html": "{{ content }}",
    "star.html": "<strong>{{ content }}</strong>",
    "text.html": "{{ value }}",
    "toc.html": "<div>{% if entries%}<ul>{{ entries }}</ul>{% endif %}</div>",
    "toc_entry.html": (
        "<li>"
        '<a href="#{{ header.anchor }}">{{ header.value }}</a>'
        "{% if children %}<ul>{{ children }}</ul>{% endif %}"
        "</li>"
    ),
    "underscore.html": "<em>{{ content }}</em>",
    "verbatim.html": "<code>{{ content }}</code>",
}


class HTMLVisitor(Visitor):
    _template_extension = ".html"

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

    def _visit_link(self, node):
        node["target"] = html.escape(node["target"])
        node["text"] = html.escape(node["text"])
        return node

    def _visit_class(self, node):
        node["classes"] = " ".join(node["classes"])
        return super()._visit_class(node)

    def _visit_admonition(self, node):
        node["node_types"] = [f'admonition_{node["class"]}']
        self._reducelist(node, ["content"], join_with="")
        return node

    def _visit_block_engine_source(self, node):
        # The Pygments lexer for the given language
        lexer = get_lexer_by_name(node["kwargs"]["language"])

        # Fetch global configuration for Pygments and for the HtmlFormatter
        pygments_config = self.config.get("pygments", {})
        formatter_config = pygments_config.get("html", {})

        # Get all the attributes of this specific block
        # that start with `pygments.`
        node_pygments_config = dict(
            (k.replace("pygments.", ""), v)
            for k, v in node["kwargs"].items()
            if k.startswith("pygments.")
        )

        # Converting from text to Python might be tricky,
        # so for now I just update the formatter config with
        # 'hl_lines' which is a list of comma-separated integers
        hl_lines = node_pygments_config.get("hl_lines", "")
        hl_lines = hl_lines.split(",")

        # Add all lines that have been highlighted with Mau's custom callouts
        hl_lines = [i for i in hl_lines if i != ""]

        # Pygments starts counting form 1, Mau from 0
        highlight_markers = [i + 1 for i in node["kwargs"]["highlights"]]

        # Merge the two
        hl_lines = list(set(hl_lines) | set(highlight_markers))

        # Tell Pygments which lines we want to highlight
        formatter_config["hl_lines"] = hl_lines

        # Create the formatter and pass the config
        formatter = get_formatter_by_name("html", **formatter_config)

        # Get the raw source from the node
        src = node["content"]

        # Highlight the source with Pygments
        highlighted_src = highlight(src, lexer, formatter)

        # Split it again into lines to work out callouts
        highlighted_src_lines = highlighted_src.split("\n")

        # Inject callout markers in the highlighted code
        callout_markers = node["kwargs"]["callouts"]["markers"]
        callout_contents = node["kwargs"]["callouts"]["contents"]

        for linenum, callout_name in callout_markers.items():
            highlighted_src_lines[linenum] = "{line} {callout}".format(
                line=highlighted_src_lines[linenum],
                callout=self._render("callout", name=callout_name),
            )

        # Rebuild the source code part and the list of callouts
        highlighted_src = "\n".join(highlighted_src_lines)
        callouts_list = [
            (self._render("callout", name=name), text)
            for name, text in callout_contents.items()
        ]

        node["content"] = highlighted_src
        node["kwargs"]["callouts"] = callouts_list

        return node

    def _visit_toc_entry(self, node, exclude_tags=None):
        exclude_tags = exclude_tags or []

        tags_excluded = [i for i in node["header"]["tags"] if i in exclude_tags]

        if len(tags_excluded) > 0:
            # Return an empty text node
            return nodes.TextNode(value="").asdict()

        self._reducelist(node, ["children"], join_with="", exclude_tags=exclude_tags)
        return node

    def _visit_command_toc(self, node):
        exclude_tags = node["kwargs"].get("exclude_tags", [])
        toc_node = self.toc.asdict()

        self._reducelist(toc_node, ["entries"], join_with="", exclude_tags=exclude_tags)

        return toc_node

    def _visit_command_footnotes(self, node):
        footnotes_node = self.footnotes.asdict()
        self._reducelist(footnotes_node, ["entries"], join_with="")

        return footnotes_node

    def _visit_verbatim(self, node):
        node["content"] = html.escape(node["value"])
        return node
