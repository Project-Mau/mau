=======
Mau CLI
=======

You can use Mau as a stand-alone tool. The command line is::

  mau [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-c CONFIG_FILE] [-f {html,asciidoctor}] [--verbose] [--debug] [--version]

The default target format is ``html``, while the default config file is just an empty dictionary.

=======
Mau API
=======

You can use Mau as a library to render text contained in Python strings::

  mau = Mau(config, target_format, default_templates=None, templates_directory=None)
  output = mau.process(text)
  variables = mau.variables

The argument ``default templates`` overwrites the templates contained in the Mau source code. You can overwrite them partially importing the default templates and updating the dictionary, e.g.::

  from mau.visitors.html_visitor import DEFAULT_TEMPLATES as mau_default_templates

  custom_templates = {"header.html": "...", ...}
  mau_default_templates.update(custom_templates)

  mau = Mau(config, output_format, default_templates=mau_default_templates)
  
==================
Configuration file
==================

The configuration file passed on the command line is a YAML file and is directly converted into a Python dictionary. The argument ``config`` passed to the object ``Mau`` is that dictionary.

Allowed keys are

``theme``: specifies the name of the theme. This is used as a path that has to contain a directory named ``templates`` where custom templates can be stored.

``no_document``: prevents Mau from wrapping the file in a ``Document`` object that renders using the relative template. This is useful in tools like static site generators that already have a template for the page.

``mau.header_anchor_function``: a function that accepts a header's ``text`` and ``level`` and returns a string that is a unique ID for that header. The default function can be found in ``parsers/main_parser.py``.

================
Custom templates
================

You can achieve a lot with custom templates. For example, let's say that you want to add a permanent link to all ``h1`` and ``h2`` headers. You can replace the default template::

  "header.html": '<h{{ level }} id="{{ anchor }}">{{ value }}</h{{ level }}>'

with::

  "header.html": (
      '<h{{ level }} id="{{ anchor }}">'
      "{{ value }}"
      '{% if anchor and level <= 2 %}<a href="#{{ anchor }}" title="Permanent link">¶</a>{% endif %}'
      "</h{{ level }}>"
  )

