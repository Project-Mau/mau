# Mau v3

Mau is a lightweight markup language heavily inspired by [AsciiDoc](https://asciidoctor.org/docs/what-is-asciidoc), [Asciidoctor](https://asciidoctor.org/) and [Markdown](https://daringfireball.net/projects/markdown/).

As I wasn't satisfied by the results I got with those tools I decided to try to write my own language and the tool to render it.

I am currently using Mau to render posts on my blog [The Digital Cat](https://www.thedigitalcatonline.com) and the online version of my book ["Clean Architectures in Python"](https://www.thedigitalcatbooks.com). I also used it to transpile the code of the book to Markua, to be able to publish the book on Leanpub using their toolchain.

## Quick start

To install Mau use `pip`

``` sh
pip install mau
```

Then install at least one visitor plugin. You probably want to start with `mau-html-visitor`

``` sh
pip install mau-html-visitor
```

To convert Mau sources into HTML just run

``` sh
mau -i source.mau -o destination.html -f html
```

To use Mau in your tool you can run it programmatically

``` python
from mau import Mau, load_visitors

visitor_classes = load_visitors()

visitors = {i.format_code: i for i in visitor_classes}
visitor_class = visitors["html"]

mau = Mau(
    "path/of/the/source",
    visitor_class=visitor_class,
)

lexer = self._mau.run_lexer(text)
parser = self._mau.run_parser(lexer.tokens)
content = self._mau.process(parser.nodes, parser.environment)

if visitor_class.transform:
    content = visitor_class.transform(content)
```

Check out Mau [documentation](https://mau.readthedocs.io/en/latest/) for further information.

## Pelican plugin

There is a Pelican plugin that enables you to use Mau in your blog. Check it at https://github.com/pelican-plugins/mau-reader.

You can see the plugin in action at https://www.thedigitalcatonline.com/blog/2021/02/22/mau-a-lightweight-markup-language/ and on other pages in my blog.

## Support

You may report bugs or missing features use the [issues page](https://github.com/Project-Mau/mau/issues).
If you want to ask for help or discuss ideas use the [discussions page](https://github.com/Project-Mau/mau/discussions)
