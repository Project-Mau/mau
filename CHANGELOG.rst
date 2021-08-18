=========
Changelog
=========

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
