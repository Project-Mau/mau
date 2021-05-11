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

Check out Mau [documentation](https://mau.readthedocs.io/en/latest/) for further information.

## Syntax

Since GitHub doesn't support Mau syntax you can see all these examples rendered at https://www.thedigitalcatonline.com/blog/2021/02/22/mau-a-lightweight-markup-language/

### Paragraphs

```
Paragraphs don't require special markup in Mau.
A paragraph is defined by one or more consecutive lines of text.
Newlines within a paragraph are not displayed.
   
Leave at least one blank line to begin a new paragraph.
```

### Comments
    
You can comment a single line with `//`

```
// This is a comment
```

or you can comment a block of lines enclosing them between two markers `////`

```
////
This is
a multiline
comment
////
```

### Thematic break

You can insert an horizontal line using three dashes

```
---
```

### Text formatting

Mau supports three inline styles triggered by `_`, `*`, and ```.

```
Stars identify *strong* text.

Underscores for _emphasized_ text

Backticks are used for `verbatim` text.
```

You can use them together, but pay attention that verbatim is very strong in Mau.

```
You can have _*strong and empashized*_ text.

You can also apply styles to _*`verbatim`*_.

But verbatim will `_*preserve*_` them.
```

Styles can be applied to only part of a word

```
*S*trategic *H*azard *I*ntervention *E*spionage *L*ogistics *D*irectorate

It is completely _counter_intuitive.

There are too many `if`s in this function.
```

Using a single style marker doesn't trigger any effect. If you need to use two of them in the sentence, though, you have to escape at least one

```
You can use _single *markers.

But you \_need\_ to escape pairs.

Even though you can escape \_only one_ of the two.

If you have \_more than two\_ it's better to just \_escape\_ all of them.

Oh, this is valid for `verbatim as well.
```

You can use inline classes to transform the text. Mau has no embedded classes, they have to be implemented in the theme.

```
The following word is underlined: [underline]#really!#

Now let's create a label like [label]#this#

You can use multiple classes separating them with commas: [label,success]#yeah!#
```

### Links

Links beginning with `http://` or `https://` are automatically parsed. If you want to use a specific text for the link you need to use the macro `link` and specify target and text.

```
https://projectmau.org - automatic!

[link](https://projectmau.org,"Project Mau")
```

The text part in this macro is optional. So, if you need you can just specify the target

```
[link](https://projectmau.org)
```

You can include spaces and other special characters in the URL::

```
[link]("https://example.org/?q=[a b]","URL with special characters")

[link]("https://example.org/?q=%5Ba%20b%5D","URL with special characters")
```

### Headers

Headers are created using the character `=`. The number of equal signs represents the level of the header
  
```
= Header 1

== Header 2

=== Header 3

==== Header 4

===== Header 5

====== Header 6
```

When you render Mau in HTML the maximum level is 6, but Mau doesn't have any constraints.

Headers are automatically collected and included in the Table of Contents, but if you want to avoid it for a specific section you can exclude the header using an exclamation mark

```
===! This header is not in the TOC
```

### Variables

You can define variables and use them in paragraphs

```
:answer:42

The answer is {answer}
```

You can avoid variable replacement escaping curly braces

```
:answer:42

The answer is \{answer\} (this won't be replaced)
```

Curly braces are used a lot in programming languages, so verbatim text automatically escapes them

```
:answer:42

The answer is `{answer}` (this won't be replaced)
```

Variables are replaced before parsing paragraphs, so they can contain any inline item such as styles or links

```
:styled:_this is text with style_
:homepage:https://projectmau.org

For example {styled}. Read the docs at {homepage}
```

Variables without a value will automatically become booleans

```
:flag:

The flag is {flag}. (rendered as "The flag is True")
```

You can set a flag to false negating it

```
:!flag:

The flag is {flag}. (rendered as "The flag is False")
```

### Blocks

Mau has the concept of blocks, which are parts of the text delimited by fences

```
----
This is a block
----
```

you can use any sequence of 4 identical characters to delimit a block, provided this doesn't clash with other syntax like headers

```
++++
This is a block
++++
	
%%%%
This is another block
%%%%
```

Should you need to insert 4 identical characters on a line for some reasons, you need to escape one of them

```
\++++
```

Blocks have the concept of secondary content, which is any paragraph that is adjacent to the closing fence. This paragraph is included in the block metadata and used according to the type of block (for example callouts by `source` blocks). The default block simply discards that content

```
----
Content of the block
----
Secondary content that won't be in the output

This is not part of the block
```

#### Block titles

Blocks can have titles

```
. The title
----
This is a block
----
```

#### Block attributes

Blocks can have attributes, specified before the opening fence between square brackets

```
[classes="callout"]
----
This is a block with the class `callout`
----
```

Attributes can be unnamed or named, and the first unnamed attribute is the type of the block. Mau provides some special block types like `source`, `admonition`, and `quote` (see the documentation below), and each one of them has a specific set of required or optional attributes.

You can combine title and attribute in any order

```
. Title of the block
[classes="callout"]
----
This is a block with the class `callout` and a title
----

[classes="callout"]
. Title of the block
----
This is a block with the class `callout` and a title
----
```

Title and attributes are consumed by the next block, so they don't need to be adjacent, should you want to separate them for some reasons

```
[classes="callout"]
	
----
This is a block with the class `callout`
----
```

### Quotes

The simplest block type the Mau provides is called `quote`. The second attribute is the attribution, and the content of the block is the quote itself.

```
[quote,"Star Wars, 1977"]
----
Learn about the Force, Luke.
----
```

### Admonitions

Mau supports admonitions, special blocks that are meant to be rendered with an icon and a title like warnings, tips, or similar things. To create an admonition you need to use the type `admonition` and specify a `class`, and `icon`, and a `label`

```
[admonition,someclass,someicon,somelabel]
----
This is my admonition
----
```

### Conditional blocks

You can wrap Mau content in a conditional block, which displays it only when the condition is met

```
:render:yes
	
[if,render,yes]
----
This will be rendered
----
	
[if,render,no]
----
This will not be rendered
----
```

You can use booleans directly without specifying the value

```
:render:
	
[if,render]
----
This will be rendered
----
	
:!render:
     
[if,render]
----
This will not be rendered
----
```

You can reverse the condition using `ifnot`

```
:render:
	
[ifnot,render]
----
This will not be rendered
----
```

### Source code

Literal paragraphs and Source code can be printed using block type `source`

```
[source]
----
This is all literal.
	
= This is not a header
	
[These are not attributes]
----
```

You can specify the language for the highlighting

```
[source,python]
----
def header_anchor(text, level):
	return "h{}-{}-{}".format(
		level, quote(text.lower())[:20], str(id(text))[:8]
    )  # pragma: no cover
----
```

#### Callouts

Source code supports callouts, where you add notes to specific lines of code. Callouts are listed in the code using a delimiter and their text is added to the secondary content of the block

```
[source,python,callouts=":"]
----
def header_anchor(text, level)::1:
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]:2:
    )  # pragma: no cover
----
1: The name of the function
2: Some memory-related wizardry
```

Callouts use a delimiter that can be any character, and are automatically removed from the source code. The default delimiter is `:`, so if that clashes with the syntax of your language you can pick a different one with the attribute `callouts`

```
[source,python,callouts="|"]
----
def header_anchor(text, level):|1|
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]|2|
    )  # pragma: no cover
----
1: The name of the function
2: Some memory-related wizardry
```

Callouts names are not manipulated by Mau, so you can use them our of order

```
[source,python,callouts=":"]
----
def header_anchor(text, level)::1:
    return "h{}-{}-{}".format(:3:
        level, quote(text.lower())[:20], str(id(text))[:8]:2:
    )  # pragma: no cover
----
1: The name of the function
2: Some memory-related wizardry
3: This is the return value
```

Callouts are not limited to digits, you can use non-numeric labels

```
[source,python,callouts=":"]
----
def header_anchor(text, level)::step1:
    return "h{}-{}-{}".format(:step3:
        level, quote(text.lower())[:20], str(id(text))[:8]:step2:
    )  # pragma: no cover
----
step1: The name of the function
step2: Some memory-related wizardry
step3: This is the return value
```

Callouts don't need to have a definition. You can use them as markers

```
[source,python]
----
def header_anchor(text, level)::1:
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]:2:
    )  # pragma: no cover
----
```
And then reference them in the text, for example with a class

```
The function [callout]#1# accepts two arguments.
```

#### Highlight lines

You can highlight lines using a callout with the special name `@`

```
[source,python]
----
def header_anchor(text, level)::@:
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]:@:
    )  # pragma: no cover
----
```

Should you prefer to list the lines you want to highlight you can use Pygments directly

```
[source,python,pygments.hl_lines="1,3"]
----
def header_anchor(text, level):
    return "h{}-{}-{}".format(
        level, quote(text.lower())[:20], str(id(text))[:8]
    )  # pragma: no cover
----
```

### Lists

You can create unordered lists using the character `*`

```
* List item
** Nested list item
*** Nested list item
* List item
** Another nested list item (indented)
* List item
```

and ordered lists with the character `#`

```
# Step 1
# Step 2
## Step 2a
## Step 2b
# Step 3
```

Mixed lists are possible

```
* List item
** Nested list item
### Ordered item 1
### Ordered item 2
### Ordered item 3
* List item
```

### Footnotes

You can insert a footnote in a paragraph using the macro `footnote`

```
This is a paragraph that ends with a note[footnote](extra information here)
```

The definitions can then be inserted with the command `::footnotes:` and are then rendered according to the template.

### Table of contents

The table of contents (TOC) can be inserted with the command `::toc:` and is rendered according to the template.

### Images

Images can be included with

```
<< image:/path/to/it.jpg
```

You can add a caption using a title

```
. This is the caption
<< image:/path/to/it.jpg
```

and specify the alternate text with `alt_text`

```
[alt_text="Description of the image"]
<< image:/does/not/exist.jpg
```

Images can be added inline with the macro `image`

```
This is a paragraph with an image [image](/path/to/it.jpg,alt_text="A nice cat",width=120,height=120)
```

## Configuration

The optional configuration file is a YAML file that can contain the following keys:

* `theme`: if you specify this Mau will try to load the templates from the directory `{theme}/templates`

## Calling Mau programmatically

You can initialise and call a `Mau` object

``` python
mau = Mau(config, output_format, default_templates=None, templates_directory=None, full_document=False)
```

where `config` is the Python dictionary equivalent of the configuration YAML file and `output_format` is a string. You can provide your custom templates with `default_templates` which will overwrite the internal templates that Mau uses for the visitor that you selected with `output_format`. Last, `full_document` will wrap the output in a full-fledged document. This flag is automatically turned on when you call Mau from the command line. When you call Mau programmatically, for example in a static site generator, you might provide the document markup externally, so it is false by default.

If you want to customise only some of the templates you can import the ones defined by Mau and change them

``` python
from mau.visitors.html_visitor import DEFAULT_TEMPLATES as mau_default_templates

mau_default_templates["container.html"] = "<div>{{ content }}</div>"}

mau = Mau(config, output_format)
```

If you specify `templates_directory` Mau will first search templates there (as files) and then fallback to the default templates dictionary.

## HTML visitor and templates

This is the list of templates that the HTML visitor uses and the parameters they get. Jinja templates can access those parameters directly, so if a node receives the parameter `value` the Jinja template can use it as `{{ value }}`. Templates also receive Mau's configuration as a dictionary called `config`, so you can access the configuration key `key1` as `{{ config.key1 }}`.

Templates need to have the `.html` extension. This is true both if you create template files on the disk and if you pass a Python dictionary of templates (see the example in the previous section). You can see al the default templates in `visitors/html_visitor.html`.

* `text.html`: plain text without any specific role.
  * `value`: the text.
* `sentence.html`: a recursive container node. This node represents the content of a paragraph, but it is recursive,
    while `paragraph` is not. It can contain other `sentence` nodes, or other types of nodes like `text`, `style` or `macro`.
  * `content`: the content of the sentence, rendered and joined without spaces.
* `paragraph.html`: a non-recursive wrapper around a single `sentence`.
  * `content`: the contained sentence.
* `horizontal_rule.html`: a horizontal divider.
* `star.html`: the "star" style.
  * `content`: the rendered content.
* `underscore.html`: the "underscore" style.
  * `content`: the rendered content.
* `verbatim.html`: verbatim text, used in particular for inline code.
  * `content`: the rendered content.
* `class.html`: this is text inside a sentence that has been given one or more specific classes.
  * `classes`: a space separated list of classes.
  * `content`: the rendered content.
* `link.html`: a hyperlink.
  * `text`: the text of the link.
  * `target`: the target of the link.
* `header.html`: a text header.
  * `level`: the level of this header (1-6).
  * `value`: the text of the header.
  * `anchor`: a unique identifier that can be used as an ID. The TOC can contain a link to this ID.
* `quote.html`: a quoted sentence.
  * `attribution`: the attribution of the quote.
  * `content`: the content of the quote.
* `raw.html`: raw text that Mau should include unprocessed, useful to include custom HTML.
  * `content`: the raw content.
* `admonition.html`: a block of text separated from the normal flow used to discuss specific topics.
  * `class`: the class of the admonition (can be used to differentiate colour or style).
  * `icon`: a icon that will be included in the admonition.
  * `label`: a title for this admonition.
  * `content`: the rendered content of the admonition.
* `block.html`: a generic block that contains part of the text that we want to render in a custom way.
  * `type`: the type of the block.
  * `content`: the rendered content of the block.
  * `title`: the title of the block.
  * `kwargs`: a list of all other arguments passed to the block.
* `source.html`: highlighted source code.
  * `code`: the highlighted code with callouts added (rendered with `callout.html`).
  * `language`: the name of the programming language.
  * `callouts`: a list of tuples. The first element is the rendered callout (using `callout.html`) and the second is the text of the callout.
  * `title`: a title for the code block.
* `callout.html`: a single callout attached to a souce code line.
  * `name`: the name of the callout.
* `list.html`: an ordered or unordered  list.
  * `ordered`: a flag that says if the list is ordered or unordered.
  * `items`: the rendered items (this is not a Python list). Each item is rendered using `list_item.html`.
* `list_item.html`: a single item of a list.
  * `content`: the rendered content of the item.
* `toc.html`: the table of contents.
  * `entries`: the rendered content of the TOC (this is not a Python list). Each entry is rendered using `toc_entry.html`.
* `toc_entry.html`: a single entry of the TOC.
  * `anchor`: a unique identifier associated to the TOC entry.
  * `text`: the text associated with this TOC entry.
  * `children`: the rendered children (rendered with `toc_entry.html` itself.
* `footnote_ref.html`: the reference to a footnote inside the text. This is just the number that appears in the main text.
  * `number`: the number of the footnote.
  * `refanchor`: an anchor for this reference.
  * `defanchor`: the anchor of the definition.
* `footnote_def.html`: the definition of a footnote. This is the full text of the footnote.
  * `number`: the number of the footnote.
  * `refanchor`: an anchor of the reference.
  * `defanchor`: the anchor for this definition.
  * `text`: the text of the footnote.
* `footnotes.html`: the footnotes.
  * `entries`: the rendered footnotes (this is not a Python list). Each item is rendered using `footnote_def.html`.
* `image.html`: an image as block element.
  * `uri`: the URI of the image.
  * `title`: the caption of the image.
  * `alt_text`: the alternate text for this image.
* `inline_image.html`: an inline image.
  * `uri`: the URI of the image.
  * `alt_text`: the alternate text for this image.

### Example

Let's say you don't like the way text like `*important*` is rendered by Mau (the default template is `"<strong>{{ content }}</strong>"`). You know that `star.html` receives `content` which is the rendered content of the style, so you can write something like

```
from mau.visitors.html_visitor import DEFAULT_TEMPLATES as mau_default_templates

mau_default_templates["star.html"] = "<span class="strong">{{ content }}</span>"}
```

## Templates and visitors

When should you modify the templates and when do you need to write a new visitor?

Templates are used to quickly customise the way a specific visitor renders some part of Mau's syntax, and while they are powerful thanks to the rich syntax of the Jinja engine, it might be complicated or impossible to implement some logic. When the logic is too complicated to be included in a template you need to write a specific visitor, which is a collection of Python methods where you do not have limits to what you can implement.

Let's consider for example how the `HTMLVisitor` renders quotes. A Mau node of type `quote` is rendered by

``` python
    def _visit_quote(self, node):
        return {
            "attribution": node["attribution"],
            "content": "".join(self.visitlist(node["content"])),
        }
```

and eventually processed by the template

``` python
    "quote.html": (
        "<blockquote>" "{{ content }}" "<cite>{{ attribution }}</cite>" "</blockquote>"
    ),
```

Now, it would be pretty easy to move the `"".join()` into the template (even though it might make it a bit too difficult to read). On the other hand, if you have a look at `HTMLVisitor._visit_source` you will quickly realise that the logic implemented there cannot be packed into a template.

## Pelican plugin

There is a Pelican plugin that enables you to use Mau in your blog. Check it at https://github.com/pelican-plugins/mau-reader.

You can see the plugin in action at https://www.thedigitalcatonline.com/blog/2021/02/22/mau-a-lightweight-markup-language/ and on other pages in my blog.

## Support

You may report bugs or missing features use the [issues page](https://github.com/Project-Mau/mau/issues).
If you want to ask for help or discuss ideas use the [discussions page](https://github.com/Project-Mau/mau/discussions)

This project has been set up using PyScaffold 3.3.1. For details and usage information on PyScaffold see https://pyscaffold.org/.
