# Configuration file for the Sphinx documentation builder.
import os
import sys
import subprocess

# -- Project information -----------------------------------------------------
project = 'FORECAST'
copyright = '2023-2026, Flaminia Fortuni, Carlo Giocoli, Erik Romelli, FORECAST Collaboration'
author = 'Flaminia Fortuni, Carlo Giocoli, Erik Romelli, Pablo MSanAla'
release = '1.0.0 (Optimized)'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'breathe',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# MyST Markdown Parser Configuration
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_image",
    "html_admonition",
]
myst_heading_anchors = 3

# Breathe Configuration (Doxygen C++ Bridge)
breathe_projects = {
    "FORECAST": os.path.abspath("_doxygen/xml")
}
breathe_default_project = "FORECAST"

# Automatically run Doxygen before building Sphinx
def run_doxygen(app):
    docs_dir = os.path.abspath(os.path.dirname(__file__))
    doxyfile = os.path.join(docs_dir, "Doxyfile")
    if os.path.exists(doxyfile):
        try:
            print("Running Doxygen to extract C++ API documentation...")
            subprocess.run(["doxygen", doxyfile], cwd=docs_dir, check=True)
            print("Doxygen XML generation complete.")
        except Exception as e:
            print(f"Warning: Doxygen execution failed: {e}")

def setup(app):
    app.connect("builder-inited", run_doxygen)

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_doxygen']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_book_theme'
html_title = 'FORECAST Documentation'
html_static_path = ['_static']

html_theme_options = {
    "repository_url": "https://github.com/flaminiafortuni/FORECAST",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": False,
    "path_to_docs": "docs",
    "show_navbar_depth": 2,
    "show_toc_level": 3,
    "navigation_with_keys": True,
}
