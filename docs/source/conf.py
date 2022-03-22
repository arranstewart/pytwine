# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# see further:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../../pytwine/'))

# -- Project information -----------------------------------------------------

project = 'pytwine'
copyright = '2022, Arran D. Stewart'
author = 'Arran D. Stewart'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
      'sphinx.ext.autodoc',
      'sphinx.ext.coverage',
      'sphinx.ext.napoleon',
      'sphinx.ext.viewcode',
      'sphinx.ext.intersphinx',
      ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'env', 'docs']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

## Custom sidebar templates, maps document names to template names.
#html_sidebars = {
#    "index": ["sidebarintro.html", "sourcelink.html", "searchbox.html", "hacks.html"],
#    "**": [
#        #"sidebarlogo.html",
#        #"localtoc.html",
#        #"relations.html",
#        "sourcelink.html",
#        "searchbox.html",
#        "hacks.html",
#    ],
#}

# default is 940px
html_theme_options = {
    'page_width': '1200px',
}

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'custom.css',
]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False




