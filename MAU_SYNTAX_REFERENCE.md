# Mau Markup Language — Syntax Reference (v5)

This is a machine-readable reference for generating valid Mau markup. Mau is a lightweight markup language that compiles to an AST and renders through Jinja templates to HTML, LaTeX, or other formats.

## 1. Document structure

A Mau document is a sequence of **document nodes** separated by blank lines. Blank lines delimit paragraphs and separate structural elements.

```
This is a paragraph.

This is another paragraph.
```

Adjacent non-blank lines are merged into a single paragraph (joined with a space in output).

A line that matches a document-level syntax (header, label, arguments, variable, control, include, horizontal rule, list item, block delimiter) ends the current paragraph, even without a blank line before it. A `//` comment inside a paragraph is skipped and the paragraph continues.

## 2. Comments

```
// Single-line comment (not rendered)

////
Multi-line comment.
Not rendered.
////
```

## 3. Inline text formatting (styles)

Styles wrap text between matching delimiter pairs. They **cannot span multiple lines**.

| Syntax | Style name | HTML default |
|--------|-----------|--------------|
| `*text*` | star | `<strong>` |
| `_text_` | underscore | `<em>` |
| `~text~` | tilde | `<sub>` |
| `^text^` | caret | `<sup>` |
| `` `text` `` | verbatim | `<code>` (no inner parsing, no variable substitution) |

Styles can be mixed: `_*bold and italic*_`. Styles can apply to parts of words: `*S*trategic`.

### Escaping

- Backslash: `\_not italic\_`
- Dollar/percent wrappers: `$not_styled$` or `%not_styled%` (escape styles and macros inside, including each other). Variables `{name}` inside them are still replaced. They cannot span multiple lines.
- Verbatim (backticks): suppresses all parsing and variable substitution. A backtick inside verbatim can be escaped with `` \` ``.

## 4. Macros

Inline commands with syntax `[name](arguments)`. Arguments are comma-separated, unnamed before named. Arguments that contain commas, `=`, or `)` must be quoted (e.g. a URL with a query string: `[link]("https://example.com/?a=b")`). Spaces don't require quotes.

A value that starts with `*`, `#`, or `@` is read as a subtype, tag, or alias (see "Arguments"), even when quoted.

| Macro | Syntax | Purpose |
|-------|--------|---------|
| link | `[link](URL, "text")` | Hyperlink. Text optional (defaults to URL). |
| mailto | `[mailto](email, "text")` | Email link. Text optional. |
| image | `[image](URI, alt_text, width, height)` | Inline image. Only the URI is mandatory. |
| class | `[class]("text", cls1, cls2)` | Wraps text with CSS classes. |
| header | `[header](name, "text")` | Internal link to a named header. Text optional (defaults to header text). |
| footnote | `[footnote](name)` | Reference to a footnote. |
| raw | `[raw]("content")` | Insert content without escaping. |
| unicode | `[unicode](hex_codepoint)` | Unicode character, e.g. `[unicode](1F30B)`. |
| if | `[if:VAR==VAL]("true text", "false text")` | Conditional inline text. False case optional. |
| ifeval | `[ifeval:VAR==VAL](true_var, false_var)` | Like `if` but looks up variable values. Lazy evaluation. |

Quoting rules: `("argument with space", "argument, with comma")`. Escape inner quotes with `\"`.

Conditional macros (`if`, `ifeval`):

- The condition supports `==` and `!=` and must not contain spaces: `[if:x == 1]` is not recognised as a macro.
- The selected text (or the value of the selected variable, for `ifeval`) is parsed as Mau, so it can contain styles and macros.
- If the false case is omitted and the condition is false, `if` produces no text, while `ifeval` raises an error.

Any other name produces a generic macro node (`[mymacro](arg1, key=value)`) with its name and arguments, which can be rendered by a custom template.

## 5. Variables

```
:name:value           // Declare variable (value is always a string)
:namespace.name:value // Namespaced variable
:+flag:               // Boolean shortcut: sets value to "true"
:-flag:               // Boolean shortcut: sets value to "false"
```

Use with `{name}` or `{namespace.name}`. Escape: `{{name}}` outputs literal `{name}`, or `\{name\}`.

Verbatim (backticks) suppresses variable substitution.

- Names can contain letters, digits, `_`, `.`, `+`, and `-`.
- A value can contain variables defined earlier, which are replaced when the variable is defined.
- Defining a variable again overwrites the previous value.
- `:name:` without a value is an error. With `:+flag:` and `:-flag:` any value is ignored.
- Using an undefined variable is an error.
- The value of a variable is parsed as Mau where it is used, so `:x:*bold*` followed by `{x}` produces bold text.
- Variables are also replaced in arguments (`[...]`) and in control conditions (`@if x=={y}`).
- Variables defined in the configuration file or on the command line are under the namespace `mau` (e.g. `{mau.envvars.title}`, see the README).

## 6. Labels

Labels attach metadata to the next document node. Syntax: `.ROLE text content`

```
.title My Title
. Also a title (default role is "title")
.cite Author Name
.details Some details
```

- The role can contain only lowercase letters, digits, `-`, and `_`. `.Title here` is a label with the default role `title` and text `Title here`.
- Every line that starts with `.` is a label, also inside a paragraph (where it ends the paragraph). Escape the dot (`\...and then`) to start a line of text with a dot.
- Multiple labels with different roles can precede a node.
- Same role twice: second overwrites first.
- Blank lines between labels and node are allowed.
- Labels can contain inline Mau syntax (styles, macros).
- Labels are available in templates as `{{ labels.ROLE }}`.

## 7. Arguments

Arguments attach parameters to the next document node. Syntax: `[ARGUMENTS]`

```
[arg1, arg2, key1=value1]
```

Rules:
- Unnamed args before named args.
- `#tag` — stored as a tag (separate from args).
- `*subtype` — sets the node subtype (one per node).
- `@alias` — expands to predefined args/subtype (one per node). E.g. `@source` expands to `engine=source` and names the first positional arg `language`.
- Multiple `[...]` lines: last one wins.

Special named arguments used by specific nodes:
- `id=VALUE` — sets a custom ID on the node.
- `name=VALUE` — on headers, sets a name for `[header]` macro references.
- `internal_id=VALUE` — on headers, sets the ID used as anchor for ToC and `[header]` links (by default it is generated from the header text).
- `engine=VALUE` — on blocks, selects the processing engine.
- `language=VALUE` — on source blocks, sets the highlight language.
- `start=N` or `start=auto` — on ordered lists, sets starting number.
- `group=NAME, position=POS` — on blocks, assigns block to a block group.
- `footnote=NAME` — on blocks, turns block into a footnote body.
- `isolate=false` — on blocks and `<< mau` includes, makes inner headers, footnotes, and header links part of the outer document.

## 8. Control conditions

Conditionally include/exclude the next document node.

```
@if variable==value
The next node (paragraph, block, header, etc.)

@if variable!=value
This node is excluded if variable equals value.
```

Spaces around `==`/`!=` are optional. The condition is evaluated at parse time.

- `@if` is the only control operator.
- The variable must be defined, otherwise Mau raises an error.
- The value is compared as a plain string: quotes are not removed (`@if x=="1"` compares with `"1"` including the quotes), and trailing spaces are part of the value.
- Only one condition applies to a node: with multiple `@if` lines the last one wins.

Labels and arguments are consumed by the controlled node even if it's excluded.

## 9. Headers

```
= Level 1
== Level 2
=== Level 3
==== Level 4
===== Level 5
====== Level 6
```

Any number of `=` is valid. Headers support inline styles. HTML maps levels > 6 to `<h6>`. A line made of exactly four identical characters (e.g. `====`) is a block delimiter, not a header.

```
[name=myheader]
== My Section

See [header](myheader) for a link back to this header.
```

## 10. Lists

```
* Unordered item
** Nested unordered
*** Deeper nested

# Ordered item
## Nested ordered
```

Ordered and unordered can be mixed at different levels. Leading spaces are ignored. At least one space is required between the marker and the text (`*text` is not a list item). A list must be followed by a blank line or by the end of the document.

```
[start=10]
# Starts at 10
# Item 11

[start=auto]
# Continues from previous list
```

The default start is 1. `start=auto` continues the numbering of the previous list.

## 11. Horizontal rule

```
---
```

Exactly three dashes on a line by themselves, without trailing spaces. Horizontal rules accept labels, arguments, and control conditions.

## 12. Blocks

Blocks are fenced regions delimited by lines of exactly 4 identical characters (e.g. `----`, `####`, `====`), except `////` which is a comment. The closing line must be identical to the opening one. A line of 5 or more characters is not a delimiter.

```
----
Block content parsed as Mau (default engine).
----

####
Another block with different delimiters.
####
```

Blocks can nest (use different delimiter characters for each level).

### Block engines

```
[engine=raw]
----
Content preserved verbatim, no Mau parsing.
----

[engine=source, language=python]
----
def hello():
    print("world")
----
```

- `default` — parses content as Mau (this is the default).
- `raw` — preserves content verbatim.
- `source` — syntax highlighting with markers.

### Source blocks (shorthand)

```
[@source, python]
----
def hello():
    print("world")
----
```

`@source` is an alias for `engine=source`. First positional arg maps to `language` (default `text`).

### Source markers and highlighting

```
[@source, python]
----
def hello():
    print("world"):1:
    return True:@add:
    return False:@-:
----
```

In the example, the second line has the marker `1`, the third line is highlighted with the style `add`, the fourth with the style `remove` (through the alias `-`).

Marker syntax: `:LABEL:` at the very end of the line (nothing can follow it). Highlight: `:@STYLE:`.

Highlight aliases: `@` = default, `@+` = add, `@-` = remove, `@!` = important, `@x` = error. More aliases can be defined in the configuration under `mau.parser.source_highlight_style_aliases`.

Customize: `marker_delimiter="|"` changes `:` to `|`. `highlight_marker="#"` changes `@` to `#`. Both must be a single character. `highlight_default_style=NAME` changes the style used by `:@:` (default `default`).

### Block isolation

Blocks are isolated by default: headers, footnotes, and header names inside a block are not part of the document. They are not added to the ToC or to the footnotes list, and footnote and `[header]` references inside the block can only point to targets inside the block.

Use `[isolate=false]` to make the block part of the document:

- its headers appear in the ToC;
- its footnotes are numbered together with the others;
- footnote and `[header]` references work across the block boundary in both directions;
- a header `name` cannot be used both inside and outside the block.

## 13. Include

Include external content with `<< TYPE`.

```
<< image:"path/to/image.png"
<< image:uri="path.png", alt_text="desc", classes="c1,c2"
<< mau:path/to/file.mau
<< raw:path/to/file.txt
<< toc
<< footnotes
<< blockgroup:groupname
<< customtype:key1=val1, key2=val2
```

Do not put a space after the colon: arguments are not stripped, so `<< customtype: key1=val1` gives the unnamed argument ` key1=val1`. For the same reason write `classes="c1,c2"` without spaces.

Any other type (lowercase letters, digits, `_`, `#`, `.`) produces a generic include node with the type and the arguments, which can be rendered by a custom template.

### Inline vs boxed arguments

```
// Inline arguments (after the colon)
<< image:"path.png", alt_text="A photo"

// Boxed arguments (on preceding line, no colon after type)
[uri="path.png", alt_text="A photo"]
<< image
```

You CANNOT mix inline and boxed arguments.

### Include Mau files

```
<< mau:other_file.mau
<< mau:other_file.mau, call:answer=42              // Pass variables
<< mau:other_file.mau, pass_environment=false      // Don't inherit env
<< mau:other_file.mau, isolate=false               // Part of the document
<< mau:other_file.mau, preprocess=jinja            // Render with Jinja first
<< mau:other_file.mau, preprocess=jinja, data=mau.changelog
```

The included file is parsed as Mau and its content is added to the document.

- Relative paths are resolved according to the configuration (see "Include paths" below). By default they are relative to the directory where Mau runs.
- Included files receive a copy of the current environment, so variables defined inside them do not affect the including file.
- `call:NAME=VALUE` adds variables to the environment of the included file. Values are strings.
- `pass_environment=false` gives the included file an empty environment, containing only the `call:` variables. The configuration values (`mau.*`) are not available either, including custom aliases and source highlight style aliases. Only the include paths strategy and the Jinja options are kept (see below). Any value other than `true` disables the environment.
- Mau detects and prevents include loops, even when the same file is written with different paths (e.g. `a.mau` and `./a.mau`). A file cannot include itself or any of the files that included it, directly or indirectly. The same file can be included multiple times in a document, for example twice in a row or by two sibling included files.

#### Include paths

Relative paths in `<< mau` and `<< raw` are resolved according to the configuration value `parser.include_paths_strategy` (the environment key `mau.parser.include_paths_strategy`):

- `cwd` (default): relative to the directory where Mau runs.
- `file`: relative to the directory of the file that contains the include. Includes inside an included file are relative to that file, so the sources don't depend on where Mau runs.

```yaml
parser:
  include_paths_strategy: file
```

- Absolute paths are used as they are.
- If the text doesn't come from a file (e.g. when Mau is used as a library without a source file name), relative paths are relative to the directory where Mau runs.
- The setting applies to the whole document, including files included with `pass_environment=false`.
- The include keeps the path as written, while error messages show the path Mau tried to open.
- Images (`<< image`) are not affected: Mau doesn't open them, and their URI is passed to the output as it is.

#### Isolation

Included files are isolated by default, like blocks (see "Block isolation"). Their headers are not added to the ToC, their footnotes are not added to the footnotes list, and footnote and `[header]` references cannot cross the file boundary.

Use `isolate=false` to make the included file part of the document. It behaves like a block with `[isolate=false]`. With nested includes, every include along the way must use `isolate=false`: content stops at the first isolated include.

Block groups are not shared across the boundary, not even with `isolate=false`: blocks assigned to a group inside an included file or block can only be rendered with `<< blockgroup` in the same file or block.

#### Jinja preprocessing

With `preprocess=jinja`, the included file is rendered as a Jinja template before it is parsed, and the result is parsed as Mau. This allows generating Mau source from structured data, e.g. lists in the configuration file.

Configuration file `mau.yaml`, loaded with `mau -c mau.yaml`:

```yaml
changelog:
  latest: 1.0.1
  versions:
    - id: 1.0.0
      date: 2026-11-04
      changes:
        - First change.
        - Second change.
    - id: 1.0.1
      date: 2026-11-05
      changes:
        - Third change.
```

Main file:

```
*Current version*: {mau.changelog.latest}

<< mau:changelog.mau, preprocess=jinja, isolate=false
```

Included file `changelog.mau`:

```
{% for version in mau.changelog.versions %}
[nobreak]
== Version {{ version.id }} ({{ version.date }})

{% for change in version.changes %}
* {{ change }}
{% endfor %}

{% endfor %}
```

Mau source produced by Jinja and then parsed:

```
[nobreak]
== Version 1.0.0 (2026-11-04)

* First change.
* Second change.

[nobreak]
== Version 1.0.1 (2026-11-05)

* Third change.
```

Template data:

- By default the template receives the environment of the included file as nested data (after `pass_environment` and `call:` are applied). Values from the configuration file are under `mau`, e.g. `mau.changelog.versions`.
- `data=KEY` gives the template **only** the mapping stored at `KEY`, whose keys become top-level variables. With `data=mau.changelog` the template above uses `{{ latest }}` and `{% for version in versions %}`. `KEY` must exist and must point to a mapping (not a list or a single value). `KEY` is looked up in the environment of the included file, so with `pass_environment=false` only the `call:` variables are available.
- `data` can only be used with `preprocess=jinja`.

Rendering rules:

- Jinja tags like `{% for %}` don't leave empty lines or indentation behind, so list items generated by a loop stay in the same list.
- Undefined variables are errors.
- Mau `{name}` variables in the rendered text are replaced as usual, after Jinja.
- Mau's `{{name}}` escape is consumed by Jinja. To keep it, change the Jinja delimiters in the configuration file (see below).
- Text coming from the data is parsed as Mau, so characters like `*`, `_`, and `` ` `` become markup.
- Jinja errors point to the line of the included file. Mau errors found after rendering point to the line of the rendered text.
- Jinja's dot syntax looks up dictionary methods first: a key named `items`, `keys`, or `values` must be written with brackets, e.g. `version['items']`.

Jinja options can be set in the configuration file under `parser.jinja.options` (the environment key `mau.parser.jinja.options`), and apply even with `pass_environment=false`:

```
parser:
  jinja:
    options:
      variable_start_string: "[["
      variable_end_string: "]]"
```

### Include raw files

```
<< raw:path/to/file.txt
```

The content of the file is added to the document as raw lines, like a raw block. It is not parsed as Mau and variables are not replaced. Relative paths are resolved like for `<< mau` (see "Include paths").

## 14. Footnotes

```
This text has a footnote[footnote](mynote).

[footnote=mynote]
----
The footnote body text.
----

<< footnotes    // Render the list of all footnotes
```

- The body of a footnote must be a block (any delimiter and any engine).
- Footnotes are numbered in the order of their definitions (the `[footnote=NAME]` blocks), not in the order of the references.
- A footnote reference without a definition is an error. A definition without references is still added to the list.

## 15. Table of contents

```
<< toc
```

Collects all headers in the document, including those in non-isolated blocks and included files (`isolate=false`).

`<< toc` and `<< footnotes` accept arguments (e.g. `<< toc:depth=2`). Mau doesn't interpret them; they are stored on the node and available to templates.

## 16. Block groups

Group blocks by name, render them together with a custom template.

```
[group=mygroup, position=description]
----
A textual description.
----

[@source, python, group=mygroup, position=code]
----
x = 42
----

<< blockgroup:mygroup
```

All the arguments of a block must be in the same `[...]` line: multiple argument lines don't merge (the last one wins).

Blocks assigned to a group are NOT rendered inline. They are collected and rendered together when `<< blockgroup:NAME` is encountered.

- `group` requires `position`. Without it the block is rendered normally.
- `position` is a free name, available to the template. It must be unique within the group.
- Blocks of a group that is never included are not rendered.
- `<< blockgroup:NAME` with an unknown group is an error.

## 17. Attachments order

Labels, arguments, and control conditions precede a document node in any order and with optional blank lines between them:

```
. A title
[arg1, key=val]
@if condition==true
== My Header
```

All three attach to the header. If the control condition is false, the header is excluded but the labels/arguments are still consumed (not passed to the next node).

## 18. Complete example

```
:title:My Document
:+show_toc:

= {title}

. A subtitle for the paragraph
This is the first paragraph with *bold* and _italic_ text.

A paragraph with a [link](https://example.com, "clickable link") and a footnote[footnote](note1).

[footnote=note1]
----
This is the footnote content.
----

@if show_toc==true
<< toc

== Code Example

[@source, python]
----
def greet(name):
    return f"Hello, {name}!":1:
----

== Lists

* First item
** Nested item
* Second item

# Step one
# Step two

---

[*quote]
----
To be or not to be.
----

<< footnotes
```

## 19. Syntax quick reference table

| Element | Syntax |
|---------|--------|
| Paragraph | Plain text, separated by blank lines |
| Comment | `//` or `////...////` |
| Bold | `*text*` |
| Italic | `_text_` |
| Superscript | `^text^` |
| Subscript | `~text~` |
| Verbatim | `` `text` `` |
| Escape | `\*`, `$text$`, `%text%` |
| Variable | `:name:value` / `{name}` |
| Boolean var | `:+name:` (true) / `:-name:` (false) |
| Label | `.role text` or `. text` (title) |
| Arguments | `[arg, key=val, #tag, *subtype, @alias]` |
| Control | `@if var==val` or `@if var!=val` (only `@if`) |
| Header | `=` to `======` (levels 1-6+) |
| Unordered list | `* item` (nest with `**`, `***`) |
| Ordered list | `# item` (nest with `##`, `###`) |
| Horizontal rule | `---` |
| Block | `----`...`----` (exactly 4 identical chars) |
| Source block | `[@source, lang]` + block |
| Raw block | `[engine=raw]` + block |
| Include image | `<< image:"URI"` |
| Include file | `<< mau:path.mau` |
| Include file, non-isolated | `<< mau:path.mau, isolate=false` |
| Include file, Jinja | `<< mau:path.mau, preprocess=jinja[, data=KEY]` |
| Include raw file | `<< raw:path.txt` |
| Include ToC | `<< toc` |
| Include footnotes | `<< footnotes` |
| Include blockgroup | `<< blockgroup:name` |
| Macro link | `[link](URL, "text")` |
| Macro image | `[image](URI, alt_text, width, height)` |
| Macro class | `[class]("text", cls1)` |
| Macro header | `[header](name, "text")` |
| Macro footnote | `[footnote](name)` |
| Macro raw | `[raw]("content")` |
| Macro unicode | `[unicode](hex)` |
| Macro if | `[if:VAR==VAL]("yes", "no")` |
| Macro ifeval | `[ifeval:VAR==VAL](var1, var2)` |
| Footnote body | `[footnote=name]` + block |
