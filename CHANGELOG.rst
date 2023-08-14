=========
Changelog
=========

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
