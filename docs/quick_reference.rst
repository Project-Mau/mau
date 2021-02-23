.. highlight:: none

==========================
Mau Syntax Quick Reference
==========================

A quick overview of what Mau can do.

Paragraphs
==========

::
   
   Paragraphs don't require special markup in Mau.
   A paragraph is defined by one or more consecutive lines of text.
   Newlines within a paragraph are not displayed.
   
   Leave at least one blank line to begin a new paragraph.
   
Comments
========
    
You can comment a single line with ``//``::

  // This is a comment

or you can comment a block of lines enclosing them between two markers ``////``::

  ////
  This is
  a multiline
  comment
  ////
    
Thematic break
==============

You can insert an horizontal line using three dashes::

  ---

Text formatting
===============

Mau supports three inline styles triggered by ``_``, ``*``, and `````.::

  Stars identify *strong* text.
  
  Underscores for _emphasized_ text
  
  Backticks are used for `verbatim` text.

You can use them together, but pay attention that verbatim is very strong in Mau.::

  You can have _*strong and empashized*_ text.

  You can also apply styles to _*`verbatim`*_.
  
  But verbatim will `_*preserve*_` them.

Styles can be applied to only part of a word::

  *S*trategic *H*azard *I*ntervention *E*spionage *L*ogistics *D*irectorate
  
  It is completely _counter_intuitive.
  
  There are too many `if`s in this function.

Using a single style marker doesn't trigger any effect, if you need to use two of them in the sentence, though, you have to escape at least one::

  You can use _single *markers.
  
  But you \_need\_ to escape pairs.
  
  Even though you can escape \_only one_ of the two.
  
  If you have \_more than two\_ it's better to just \_escape\_ all of them.
  
  Oh, this is valid for `verbatim as well.

You can use inline classes to transform the text. Mau has no embedded classes, they have to be implemented in the theme.::

  The following word is underlined: [underline]#really!#
  
  Now let's create a label like [label]#this#
  
  You can use multiple classes separating them with commas: [label,success]#yeah!#
    
Links
=====

Links beginning with ``http://`` or ``https://`` are automatically parsed. If you want to use a specific text for the link you need to use the macro ``link`` and specify target and text.::

  https://projectmau.org - automatic!
  
  [link](https://projectmau.org,"Project Mau")

You can include spaces and other special characters in the URL::

  [link]("https://example.org/?q=[a b]","URL with special characters")
  
  [link]("https://example.org/?q=%5Ba%20b%5D","URL with special characters")

Headers
=======

Headers are created using the character ``=``. The number of equal signs represents the level of the header::
  
  = Header 1
  
  == Header 2
  
  === Header 3
  
  ==== Header 4
  
  ===== Header 5
  
  ====== Header 6

Headers are automatically collected and included in the Table of Contents, but if you want to avoid it for a specific section you can exclude the header using an exclamation mark::

  ===! This header is not in the TOC

Variables
=========

You can define variables and use them in paragraphs::

  :answer:42
	  
  The answer is {answer}

You can avoid variable replacement escaping curly braces::

  :answer:42

  The answer is \{answer\}

Curly braces are used a lot in programming languages, so verbatim text automatically escapes them::

  :answer:42

  The answer is `{answer}`

Variables are replaced before parsing paragraphs, so they can contain any inline item such as styles or links::

  :styled:_this is text with style_
  :homepage:https://projectmau.org

  For example {styled}. Read the docs at {homepage}

Variables without a value will automatically become booleans::

  :flag:

  The flag is {flag}.

You can set a flag to false negating it::

  :!flag:

  The flag is {flag}.

Blocks
======

Mau has the concept of blocks, which are parts of the text delimited by fences::

  ----
  This is a block
  ----

you can use any sequence of 4 identical characters to delimit a block, provided this doesn't clash with other syntax like headers::

  ++++
  This is a block
  ++++

  %%%%
  This is another block
  %%%%

Should you need to insert 4 identical characters on a line for some reasons, you need to escape one of them:::

  \++++

Blocks have the concept of secondary content, which is any paragraph that is adjacent to the closing fence. This paragraph is included in the block metadata and used according to the type of block (for example callouts by ``source`` blocks). The default block simply discards that content::

  ----
  Content of the block
  ----
  Secondary content that won't be in the output

  This is not part of the block

Block titles
============

Blocks can have titles::

  . The title
  ----
  This is a block
  ----

Block attributes
================

Blocks can have attributes, specified before the opening fence between square brackets::

  [classes="callout"]
  ----
  This is a block with the class `callout`
  ----

Attributes can be unnamed or named, and the first unnamed attribute is the type of the block. Mau provides some special block types like ``source``, ``admonition``, and ``quote`` (see the documentation below), and each one of them has a specific set of required or optional attributes.

You can combine title and attribute in any order::

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

Title and attributes are consumed by the next block, so they don't need to be adjacent, should you want to separate them for some reasons::

  [classes="callout"]

  ----
  This is a block with the class `callout`
  ----

Quotes
======

The simplest block type the Mau provides is called ``quote``. The second attribute is the attribution, and the content of the block is the quote itself.::

  [quote,"Star Wars, 1977"]
  ----
  Learn about the Force, Luke.
  ----

Admonitions
===========

Mau supports admonitions, special blocks that are meant to be rendered with an icon and a title like warnings, tips, or similar things. To create an admonition you need to use the type ``admonition`` and specify a ``class``, and ``icon``, and a ``label``::

  [admonition,someclass,someicon,somelabel]
  ----
  This is my admonition
  ----

Conditional blocks
==================

You can wrap Mau content in a conditional block, which displays it only when the condition is met.::

  :render:yes

  [if,render,yes]
  ----
  This will be rendered
  ----

  [if,render,no]
  ----
  This will not be rendered
  ----

You can use booleans directly without specifying the value::

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

You can reverse the condition using ``ifnot``::

  :render:

  [ifnot,render]
  ----
  This will not be rendered
  ----

Source code
===========

Literal paragraphs and Source code can be printed using block type ``source``::

  [source]
  ----
  This is all literal.

  = This is not a header

  [These are not attributes]
  ----

You can specify the language for the highlighting::

  [source,python]
  ----
  def header_anchor(text, level):
      return "h{}-{}-{}".format(
          level, quote(text.lower())[:20], str(id(text))[:8]
      )  # pragma: no cover
  ----

Callouts
========

Source code supports callouts, where you add notes to specific lines of code. Callouts are listed in the code using a delimiter and their text is added to the secondary content of the block::

  [source,python,callouts=":"]
  ----
  def header_anchor(text, level)::1:
      return "h{}-{}-{}".format(
          level, quote(text.lower())[:20], str(id(text))[:8]:2:
      )  # pragma: no cover
  ----
  1: The name of the function
  2: Some memory-related wizardry

Callouts use a delimiter that can be any character, and are automatically removed from the source code. The default delimiter is ``:``, so if that clashes with the syntax of your language you can pick a different one with the attribute ``callouts``::

  [source,python,callouts="|"]
  ----
  def header_anchor(text, level):|1|
      return "h{}-{}-{}".format(
          level, quote(text.lower())[:20], str(id(text))[:8]|2|
      )  # pragma: no cover
  ----
  1: The name of the function
  2: Some memory-related wizardry

Callouts names are not manipulated by Mau, so you can use them our of order::

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

Callouts are not limited to digits, you can use non-numeric labels::

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

Lists
=====

You can create unordered lists using the character ``*``::

  * List item
  ** Nested list item
  *** Nested list item
  * List item
  ** Another nested list item (indented)
  * List item

and ordered lists with the character ``#``::

  # Step 1
  # Step 2
  ## Step 2a
  ## Step 2b
  # Step 3

Mixed lists are possible::

  * List item
  ** Nested list item
  ### Ordered item 1
  ### Ordered item 2
  ### Ordered item 3
  * List item

Footnotes
=========

You can insert a footnote in a paragraph using the macro ``footnote``::

  This is a paragraph that ends with a note[footnote](extra information here)

Footnotes can be inserted with the command ``::footnotes:`` and are then rendered according to the template.

Table of contents
=================

The table of contents (TOC) can be inserted with the command ``::toc:`` and is rendered according to the template

Images
======

Images can be included with::

  << image:/path/to/it.jpg

You can add a caption using a title::

  . This is the caption
  << image:/path/to/it.jpg

and specify the alternate text with ``alt_text``::

  [alt_text="Description of the image"]
  << image:/does/not/exist.jpg

Images can be added inline with the macro ``image``::

  This is a paragraph with an image [image](/path/to/it.jpg,alt_text="A nice cat",width=120,height=120)
