# Mau 

Mau is a lightweight markup language heavily inspired by [AsciiDoc](https://asciidoctor.org/docs/what-is-asciidoc), [Asciidoctor](https://asciidoctor.org/) and [Markdown](https://daringfireball.net/projects/markdown/).

As I wasn't satisfied by the results I got with those tools I decided to try to write my own language and the tool to render it.

I am currently using Mau to render posts on my blog [The Digital Cat](https://www.thedigitalcatonline.com) and the online version of my book ["Clean Architectures in Python"](https://www.thedigitalcatbooks.com). I also used it to transpile the code of the book to Markua, to be able to publish the book on Leanpub using their toolchain.

## Quick start

To install Mau use `pip`

``` sh
pip install mau
```

To convert Mau sources into HTML just run

``` sh
mau -i source.mau -o destination.html -f html
```

To use Mau in your tool you can run it programmatically

``` python
from mau import Mau

mau = Mau(target_format="html")

mau.process(text)
```

Check out Mau [documentation](https://mau.readthedocs.io/en/latest/) for further information.

## Pelican plugin

There is a Pelican plugin that enables you to use Mau in your blog. Check it at https://github.com/pelican-plugins/mau-reader.

You can see the plugin in action at https://www.thedigitalcatonline.com/blog/2021/02/22/mau-a-lightweight-markup-language/ and on other pages in my blog.

## Incompatibility between Mau 2.x and Mau 1.x

* The macro `[footnote]()` requires now a strict attributes syntax, so you need to put between quotes any text that contains commas. In Mau 1.x footnotes use the text between round brackets directly, so there was no need for quotes. The old behaviour can be still turned on setting the configuration value `v1_backward_compatibility` to `True`. The old syntax is however considered deprecated, so my advice is to change the source as soon as possible. Example `[footnote](A footnote, with a comma)` should become `[footnote]("A footnote, with a comma")`.

## Support

You may report bugs or missing features use the [issues page](https://github.com/Project-Mau/mau/issues).
If you want to ask for help or discuss ideas use the [discussions page](https://github.com/Project-Mau/mau/discussions)

This project has been set up using PyScaffold 3.3.1. For details and usage information on PyScaffold see https://pyscaffold.org/.
