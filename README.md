# Mau v5

Mau is a lightweight markup language heavily inspired by [AsciiDoc](https://asciidoctor.org/docs/what-is-asciidoc), [Asciidoctor](https://asciidoctor.org/) and [Markdown](https://daringfireball.net/projects/markdown/).

It is built on **Jinja** and designed for authors who want the simplicity of Markdown with the expressive power of templating. You can use Mau to create blog posts, books, documentation.

## Why Mau?

Mau combines:
- **Readable plain text** similar to Markdown.
- **Jinja templating** that allows you to easily affect the rendering of Mau syntax.
- **Flexible output** via pluggable visitors (HTML, TeX, YAML, etc.)

## Installation

Mau requires Python 3.10 or later.

``` sh
pip install mau
```

Mau parses the source into an abstract syntax tree and then transforms it into the final output using a visitor. The core package includes a YAML visitor and a Jinja base visitor. To render into a specific format you need an additional visitor plugin.

To render Mau into HTML:

``` sh
pip install mau-html-visitor
```

To render Mau into TeX:

``` sh
pip install mau-tex-visitor
```

## Quick start

1. Create a file `example.mau` with some Mau content:

   ```
   = My first document

   This is a paragraph with *bold text* and _underlined text_.

   * Item one
   * Item two
   * Item three
   ```

2. Render it to YAML (built-in, no extra plugin needed):

   ``` sh
   mau -i example.mau -t core:YamlVisitor -o example.yaml
   ```

3. If you installed `mau-html-visitor`, render it to HTML:

   ``` sh
   mau -i example.mau -t core:HtmlVisitor -o example.html
   ```

## CLI usage

```
mau -i INPUT_FILE -t VISITOR [-o OUTPUT_FILE] [OPTIONS]
```

### Required arguments

| Flag | Description |
|---|---|
| `-i`, `--input-file` | The Mau source file |
| `-t`, `--visitor` | The output format visitor (e.g. `core:YamlVisitor`, `core:HtmlVisitor`) |

### Optional arguments

| Flag | Description |
|---|---|
| `-o`, `--output-file` | Output file path. Use `-` for standard output. Defaults to the input file name with the visitor's extension |
| `-c`, `--config-file` | A YAML configuration file |
| `-e`, `--environment-file` | A YAML file loaded into the environment. Can be repeated. Format: `key=path` or just `path` |
| `--environment-files-namespace` | Namespace for environment files (default: `envfiles`) |
| `-v`, `--environment-variable` | An environment variable as `key=value`. Can be repeated. The key can be dotted to add namespaces |
| `--environment-variables-namespace` | Namespace for environment variables (default: `envvars`) |
| `--verbose` | Set log level to INFO |
| `--debug` | Set log level to DEBUG |
| `--lexer-print-output` | Print the tokens produced by the lexer |
| `--lexer-only` | Stop after the lexing step |
| `--version` | Print the Mau version and exit |

### Examples

``` sh
# Render to YAML and print to stdout
mau -i document.mau -t core:YamlVisitor -o -

# Render to HTML with an environment variable
mau -i document.mau -t core:HtmlVisitor -v title="My Doc"

# Render with a config file and debug output
mau -i document.mau -t core:YamlVisitor -c config.yaml --debug

# Load an environment file
mau -i document.mau -t core:HtmlVisitor -e metadata=data.yaml
```

## Library usage

You can use Mau as a Python library:

```python
import logging

from mau import Mau, load_visitors
from mau.environment.environment import Environment
from mau.message import LogMessageHandler

logger = logging.getLogger(__name__)
message_handler = LogMessageHandler(logger)

# Build the environment from a dictionary.
environment = Environment.from_dict(
    {"some_variable": "some_value"},
)

# Create the Mau processor.
mau = Mau(message_handler=message_handler, environment=environment)

# Load available visitors.
visitors = load_visitors()

# Select a visitor class.
visitor_class = visitors["core:YamlVisitor"]

# Process the text.
text = "= Hello\n\nThis is *bold*."
result = mau.process(visitor_class, text, source_filename="example.mau")

print(result)
```

For finer control, you can run each stage individually:

```python
# Initialise the text buffer.
text_buffer = mau.init_text_buffer(text, "example.mau")

# Run the lexer.
lexer = mau.run_lexer(text_buffer)

# Run the parser.
parser = mau.run_parser(lexer.tokens)

# Run the visitor on the document node.
rendered = mau.run_visitor(visitor_class, parser.output.document)
```

## Backward compatibility

Mau v5 changed some parts of the syntax in a non-backward compatible way. The file [MAJOR_CHANGES.md](MAJOR_CHANGES.md) contains a list of the major changes between v4 and v5.

## Pelican plugin

There is a Pelican plugin to use Mau directly in your blog:

https://github.com/pelican-plugins/mau-reader

Make sure to read the instructions in that repository to configure the plugin correctly.

## Full documentation

The full documentation is available at https://project-mau.github.io/.

## LLM instructions

If you want to quickly teach an LLM to use Mau you can use the file `MAU_SYNTAX_REFERENCE.md`.

## Development

### Setup

1. Clone the repository.
2. Create a virtual environment with Python 3.10+.
3. Install the development and testing dependencies:

   ``` sh
   pip install -e ".[development,testing]"
   ```

### Running tests

``` sh
pytest
```

### Linting

``` sh
ruff check .
mypy .
pylint mau
```

## Support

Bug reports and feature requests: https://github.com/Project-Mau/mau/issues

Discussions and Q&A: https://github.com/Project-Mau/mau/discussions

## License

MIT License.
