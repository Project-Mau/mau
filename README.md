# Mau 

Mau is a lightweight markup language heavily inspired by [AsciiDoc](https://asciidoctor.org/docs/what-is-asciidoc), [Asciidoctor](https://asciidoctor.org/) and [Markdown](https://daringfireball.net/projects/markdown/).

As I wasn't satisfied by the results I got with those tools I decided to try to write my own language and the tool to render it.

I successfully used it to transpile my book ["Clean Architectures in Python"](https://www.pycabook.com) from Mau to Asciidoctor, as Mau is not ready to be used in my workflow yet (it can't create PDFs, for example).

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

## Support

You may report bugs or missing features use the [issues page](https://github.com/Project-Mau/mau/issues).
If you want to ask for help or discuss ideas use the [discussions page](https://github.com/Project-Mau/mau/discussions)

This project has been set up using PyScaffold 3.3.1. For details and usage information on PyScaffold see https://pyscaffold.org/.
