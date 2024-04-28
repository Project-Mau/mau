=========
Changelog
=========

Version 4.0.0
=============

Please be aware that this major release contains breaking changes from Mau 3. All changes marked `syntax` are breaking and thus require manual modification of the Mau source.

- [enhancement] Block aliases can be defined through the environment.
- [enhancement] Header anchor can be forced through the attribute `anchor`.
- [enhancement] Headers support variables and rich text.
- [enhancement] Variable values can contain other variables.
- [enhancement] List start can be forced through the attribute `start` and automated to link to a previous list.
- [enhancement] Macros can contain rich text.
- [enhancement] New macro `[header](id)` that creates an internal link to a header with that `id`.
- [enhancement] New macro `if` that renders text conditionally.
- [enhancement] New macro `ifeval` that renders the content of variables conditionally (short-circuit evaluation). 
- [enhancement] Paragraphs now store a title defined before them.
- [enhancement] Parser output contains a separate ToC that can be rendered using different templates (e.g. using a prefix).
- [enhancement] The list of template names that Mau considers for each node has been considerably increased. Now templates can include the parent type, subtype, the node position in the parent node, visitor prefixes, node subtype, and node tags.
- [enhancement] The variable `mau.visitor.format` contains the output format.
- [enhancement] Added `$` and `%` to escape text like verbatim without using `VerbatimNode`.
- [internal] All nodes contain a link to the parent node and to the position they have in it.
- [internal] Blocks use positions `primary` and `secondary` for children.
- [internal] Titles and headers use `SentenceNode` and all nodes inside the sentence are given the position `title` or `header` respectively.
- [internal] All nodes receive the same basic arguments to promote a uniform interface.
- [syntax] Content nodes receive only the content type and the list of URIs, all other parameters are passed as attributes.
- [syntax] New way to define and print boolean variables
- [syntax] Node subtype is created using `*` in the attributes. All document nodes can now have a subtype.
- [syntax] Removed reference engine, reference macro, and references command from syntax.
- [syntax] The variable `mau.parser.content_wrapper` now accepts an instance and not a class any more, which allows to customise the wrapper through attributes like subtype and tags.
- [syntax] New syntax for control statements that allow uniform conditional rendering of document and text nodes.
- [syntax] Removed `condition` flag to render blocks (replaced with control statements).
- [syntax] Admonitions don't use the argument `label` any more. They use the block title.
- [syntax] Macro `class` now accepts multiple classes as arguments instead of using a comma-separated single argument.

Version 3.1.0
=============

- [fix] Added RawNode node and make source blocks emit lists of RawNode instead of TextNode. This prevents escaping characters in formats like HTML. Raw blocks now use a list of RawNode as well.

Version 3.0.3
=============

- [enhancement] Better error reporting
- [fix] Fixed incorrect context passed to sub parsers

Version 3.0.2
=============

- [fix] Fixed missing transfer of args and kwargs through visitor functions
- [fix] Added the missing macro node visitor function
- [fix] Tidy up configuration of development tools
- [enhancement] Management of visitor configuration (variables) moved to the class BaseVisitor

Version 3.0.1
=============

- [fix] Fixed type hints to keep compatibility with Python 3.8

Version 3.0.0
=============

This is a major rewrite of the Mau engine that introduces some incompatibilities with the syntax of Mau 2.x. Please check the documentation for more details.
The source code now contains a basic visitor that returns the AST and a Jinja visitor which works with any Jinja template. Other visitors are being migrated to plugins that have to be installed separately. The HTML and Markua visitor have been ported from version 2.x, and a PDF Visitor has been added. The AsciiDoctor visitor has been removed.

Version 2.0.3
=============

- [enhancement] Added two new styles: `^caret^` and `~tilde~`. Since in both Markua and AsciiDoctor these are connected with superscript and subscript this has been implemented as the default behaviour of the HTML visitor.

Version 2.0.2
=============

- [fix] Markua footnotes contain an hash that avoids clashes.
- [fix] Markus footnotes end with a newline so they are not rendered on the same line.
- [fix] Resolved issue #4: README updated to reflect the current API.
- [fix] HTML visitor escapes special characters like `&`, `>`, and `<` in verbatim and links.

Version 2.0.1
=============

- [fix] Fixed a bug in the Markua and AsciiDoctor visitors.
- [fix] Fixed the documentation source code

Version 2.0.0
=============

This version contains a huge amount of internal changes, and a good amount of new features. This list shows the most important ones, see the Git history for full details.

- [fix] Fixed automatic links ending with period or comma
- [fix] Fixed management of configuration errors
- [fix] Fixed failing tests of Markua visitor
- [fix] Header anchors preserve dots
- [fix] Image template now properly closes the `img` tag.
- [enhancement] Added support for lexer directives and directive `::#include:` to include files.
- [enhancement] Headers support tags that can be filtered in the TOC.
- [enhancement] Added new macro `[class]`, old syntax `[CLASS]#text#` is still supported but considered deprecated.
- [enhancement] Added the concept of engine, and implemented `raw`, `source`, and `mau` engines porting the code from the relative block types.
- [enhancement] Added initial support for preprocessors.
- [enhancement] Added support for block definitions through `defblock`.
- [enhancement] Moved custom block types (`quote`, `admonition`, and `source`) to block definitions.
- [enhancement] Blocks are now rendered using a set of possible templates, according to the block type and the engine.
- [enhancement] Read custom templates from the configuration file
- [enhancement] Conditional rendering is now a property of blocks.
  
Version 1.4.1
=============

- [fix] Fixed wrong behaviour of footnotes and links with round brackets
- [fix] Better management of footnotes in the Markua visitor

Version 1.4.0
=============

- [enhancement] The README has been improved to provide documentation about the syntax and the templates. 
- [enhancement] Added a link to the docs (`#2`_)
- [enhancement] A new visitor for Leanpub's Markua language has been added.
- [break] The interface of the main object has changed to accept the argument ``full_document`` that replaces the configuration entry ``no_document``

Version 1.3.0
=============

- [fix] Fixed behaviour of the ``link`` macro when no text is specified
- [enhancement] Added link to blog page with a rendered version of the examples
- [enhancement] Added documentation for the CLI and the API
- [enhancement] New default header anchor function that produces deterministic IDs. Added config value ``mau.header_anchor_function`` that allows the user to provide a different function

Version 1.2.0
=============

- [enhancement] Callouts can be added to source code without any definition
- [enhancement] Lines can be highlighted with special markers and with Pygments syntax
- [enhancement] Pygments can be configured through Mau's config dictionary
- [enhancement] Source blocks now accept ``pygments.hl_lines`` to highlight lines
- [fix] Fixed structure of the config dictionary
- [internal] Simplified code to manage callouts

Version 1.1.1
=============

- GitHub user AlexNodex (https://github.com/AlexNodex) contributed a fix to the documentation (wrong headers). Thanks!

Version 1.1.0
=============

- [enhancement] Default templates are simpler. Some templates were copied from Asciidoc and referenced CSS classes that are defined by their website
- [enhancement] Documentation of node objects has been improved to make it easier to write custom templates
- [enhancement] Documents can use a pure container as template through the option ``no_document`` (useful for blogs, where the HTML head and body are provided by the engine)
- [enhancement] Images now have classes
- [enhancement] Node joins are now performed inside the visitor instead of by the templates
- [fix] Backtick can now be printed in verbatim escaping it
- [fix] Basic blocks now have a blocktype attribute
- [fix] Nested lists are now properly handled and rendered in HTML
- [internal] A global review of arguments and how they are passed to nodes
- [internal] A global review of node objects
- [internal] Code of ``Visitor`` objects has been improved to make them simpler to write

Version 1.0.0
=============

- A working initial implementation

.. _#2: https://github.com/Project-Mau/mau/pull/2
