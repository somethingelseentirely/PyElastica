# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys

sys.path.insert(0, os.path.abspath("../"))

from elastica.version import VERSION


# -- Project information -----------------------------------------------------

project = "PyElastica"
copyright = "2024, Gazzola Lab"
author = "Gazzola Lab"

# The full version, including alpha/beta/rc tags
release = VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx_autodoc_typehints",
    #'sphinx.ext.napoleon',
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "numpydoc",
    "myst_parser",
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "README.md",  # File reserved to explain how documentationing works.
]

autodoc_default_flags = [
    "members",
    "private-members",
    "special-members",
    "show-inheritance",
]
autosectionlabel_prefix_document = True

source_parsers = {}
source_suffix = [".rst", ".md"]

master_doc = "index"
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/GazzolaLab/PyElastica",
    "use_repository_button": True,
}
html_title = "PyElastica"
html_logo = "_static/assets/Logo.png"
# pygments_style = "sphinx"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/*", "css/logo.css"]

# -- Options for autodoc  ---------------------------------------------------
autodoc_member_order = "bysource"

# -- Options for numpydoc ---------------------------------------------------
numpydoc_show_class_members = False
