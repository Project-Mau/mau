# Mau Markup Language — Syntax Reference (v5)

This is a machine-readable reference for generating valid Mau markup. Mau is a lightweight markup language that compiles to an AST and renders through Jinja templates to HTML, LaTeX, or other formats.

## 1. Document structure

A Mau document is a sequence of **document nodes** separated by blank lines. Blank lines delimit paragraphs and separate structural elements.

```
This is a paragraph.

This is another paragraph.
```

Adjacent non-blank lines are merged into a single paragraph (joined with a space in output).

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
- Dollar/percent wrappers: `$not_styled$` or `%not_styled%` (escape everything inside, including each other)
- Verbatim (backticks): suppresses all parsing and variable substitution

## 4. Macros

Inline commands with syntax `[name](arguments)`. Arguments are comma-separated, unnamed before named, quoted if containing spaces/commas/closing brackets.

| Macro | Syntax | Purpose |
|-------|--------|---------|
| link | `[link](URL, "text")` | Hyperlink. Text optional (defaults to URL). |
| mailto | `[mailto](email, "text")` | Email link. Text optional. |
| image | `[image](URI)` | Inline image. |
| class | `[class]("text", cls1, cls2)` | Wraps text with CSS classes. |
| header | `[header](name, "text")` | Internal link to a named header. Text optional (defaults to header text). |
| footnote | `[footnote](name)` | Reference to a footnote. |
| raw | `[raw]("content")` | Insert content without escaping. |
| unicode | `[unicode](hex_codepoint)` | Unicode character, e.g. `[unicode](1F30B)`. |
| if | `[if:VAR==VAL]("true text", "false text")` | Conditional inline text. False case optional. |
| ifeval | `[ifeval:VAR==VAL](true_var, false_var)` | Like `if` but looks up variable values. Lazy evaluation. |

Quoting rules: `("argument with space", "argument, with comma")`. Escape inner quotes with `\"`.

## 5. Variables

```
:name:value           // Declare variable (value is always a string)
:namespace.name:value // Namespaced variable
:+flag:               // Boolean shortcut: sets value to "true"
:-flag:               // Boolean shortcut: sets value to "false"
```

Use with `{name}` or `{namespace.name}`. Escape: `{{name}}` outputs literal `{name}`, or `\{name\}`.

Verbatim (backticks) suppresses variable substitution.

## 6. Labels

Labels attach metadata to the next document node. Syntax: `.ROLE text content`

```
.title My Title
. Also a title (default role is "title")
.cite Author Name
.details Some details
```

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
- `engine=VALUE` — on blocks, selects the processing engine.
- `language=VALUE` — on source blocks, sets the highlight language.
- `start=N` or `start=auto` — on ordered lists, sets starting number.
- `group=NAME, position=POS` — on blocks, assigns block to a block group.
- `footnote=NAME` — on blocks, turns block into a footnote body.
- `isolate=false` — on blocks, merges inner headers/footnotes into outer document.

## 8. Control conditions

Conditionally include/exclude the next document node.

```
@if variable==value
The next node (paragraph, block, header, etc.)

@if variable!=value
This node is excluded if variable equals value.
```

Spaces around `==`/`!=` are optional. The condition is evaluated at parse time.

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

Any number of `=` is valid. Headers support inline styles. HTML maps levels > 6 to `<h6>`.

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

Ordered and unordered can be mixed at different levels. Leading spaces are ignored.

```
[start=10]
# Starts at 10
# Item 11

[start=auto]
# Continues from previous list
```

## 11. Horizontal rule

```
---
```

Three dashes on a line by themselves.

## 12. Blocks

Blocks are fenced regions delimited by 4+ identical characters (except `////` which is a comment).

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

`@source` is an alias for `engine=source`. First positional arg maps to `language`.

### Source markers and highlighting

```
[@source, python]
----
def hello():
    print("world"):1:       // Marker "1" on this line
    return True:@add:        // Highlight with style "add"
    return False:@-:         // Highlight with style "remove" (alias)
----
```

Marker syntax: `:LABEL:` at end of line. Highlight: `:@STYLE:`.

Highlight aliases: `@` = default, `@+` = add, `@-` = remove, `@!` = important, `@x` = error.

Customize: `marker_delimiter="|"` changes `:` to `|`. `highlight_marker="#"` changes `@` to `#`.

### Block isolation

Blocks are isolated by default: headers and footnotes inside are not added to the global ToC/footnotes list. Use `[isolate=false]` to merge them.

## 13. Include

Include external content with `<< TYPE`.

```
<< image:"path/to/image.png"
<< image:uri="path.png", alt_text="desc", classes="c1, c2"
<< mau:path/to/file.mau
<< toc
<< footnotes
<< blockgroup:groupname
<< customtype: key1=val1, key2=val2
```

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
<< mau:other_file.mau, call:answer=42    // Pass variables
<< mau:other_file.mau, pass_environment=false  // Don't inherit env
```

Included files inherit the current environment. `call:NAME=VALUE` passes new variables. Mau detects and prevents include loops.

## 14. Footnotes

```
This text has a footnote[footnote](mynote).

[footnote=mynote]
----
The footnote body text.
----

<< footnotes    // Render the list of all footnotes
```

## 15. Table of contents

```
<< toc
```

Collects all headers in the document. Affected by block isolation.

## 16. Block groups

Group blocks by name, render them together with a custom template.

```
[group=mygroup, position=description]
----
A textual description.
----

[group=mygroup, position=code]
[@source, python]
----
x = 42
----

<< blockgroup:mygroup
```

Blocks assigned to a group are NOT rendered inline. They are collected and rendered together when `<< blockgroup:NAME` is encountered.

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
| Control | `@if var==val` or `@if var!=val` |
| Header | `=` to `======` (levels 1-6+) |
| Unordered list | `* item` (nest with `**`, `***`) |
| Ordered list | `# item` (nest with `##`, `###`) |
| Horizontal rule | `---` |
| Block | `----`...`----` (4+ identical chars) |
| Source block | `[@source, lang]` + block |
| Raw block | `[engine=raw]` + block |
| Include image | `<< image:"URI"` |
| Include file | `<< mau:path.mau` |
| Include ToC | `<< toc` |
| Include footnotes | `<< footnotes` |
| Include blockgroup | `<< blockgroup:name` |
| Macro link | `[link](URL, "text")` |
| Macro image | `[image](URI)` |
| Macro class | `[class]("text", cls1)` |
| Macro header | `[header](name, "text")` |
| Macro footnote | `[footnote](name)` |
| Macro raw | `[raw]("content")` |
| Macro unicode | `[unicode](hex)` |
| Macro if | `[if:VAR==VAL]("yes", "no")` |
| Macro ifeval | `[ifeval:VAR==VAL](var1, var2)` |
| Footnote body | `[footnote=name]` + block |
