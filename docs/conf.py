#!python3

"""
    Configuration for project documentation using Sphinx.
"""

# standard
import os
from datetime import datetime
from pathlib import Path

# project
from qgis_deployment_toolbelt import __about__
from qgis_deployment_toolbelt.commands.upgrade import (
    get_download_url_for_os,
    get_latest_release,
    replace_domain,
)

# -- Build environment -----------------------------------------------------
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# -- Project information -----------------------------------------------------
author = __about__.__author__
copyright = __about__.__copyright__
description = __about__.__summary__
project = __about__.__title__
version = release = __about__.__version__

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Sphinx included
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    # 3rd party
    "myst_parser",
    "sphinx_argparse_cli",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
# language = "fr"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "*.csv",
    "samples/*",
    "Thumbs.db",
    ".DS_Store",
    "*env*",
    "libs/*",
    "*.xml",
    "input/*",
    "output/*",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# Theme
html_favicon = "static/logo_qdt.png"
html_logo = "static/logo_qdt.png"
html_theme = "furo"
html_theme_options = {
    "source_repository": __about__.__uri__,
    "source_branch": "main",
    "source_directory": "docs/",
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["static"]

html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#


# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
html_search_language = "en"


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}


# -- Extension configuration -------------------------------------------------

# mermaid
mermaid_params = [
    "--theme",
    "forest",
    "--width",
    "100%",
    "--backgroundColor",
    "transparent",
]

# MyST Parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    # "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
]

myst_heading_anchors = 3

# replacement variables
myst_substitutions = {
    "author": author,
    "date_update": datetime.now().strftime("%d %B %Y"),
    "description": description,
    "repo_url": __about__.__uri__,
    "title": project,
    "version": version,
}


# OpenGraph
ogp_image = (
    f"{__about__.__uri_homepage__}/_images/qgis-deployment-toolbelt_cli_help.png"
)
ogp_site_name = f"{project} - Documentation"
ogp_site_url = __about__.__uri_homepage__
ogp_custom_meta_tags = [
    "<meta name='twitter:card' content='summary_large_image'>",
    f'<meta property="twitter:description" content="{description}" />',
    f'<meta property="twitter:image" content="{ogp_image}" />',
    '<meta property="twitter:site" content="@geojulien" />',
    f'<meta property="twitter:title" content="{project}" />',
]

# -- Functions ------------------------------------------------------------------


def populate_download_page(_):
    """Generate download section included into installation page."""
    latest_release = get_latest_release(
        replace_domain(
            url=__about__.__uri_repository__, new_domain="api.github.com/repos"
        )
    )

    dl_link_linux, dl_link_macos, dl_link_windows = (
        get_download_url_for_os(latest_release.get("assets"), override_opersys=os)[0]
        for os in ["linux", "darwin", "win32"]
    )

    out_download_section = (
        "::::{grid} 3\n:gutter: 2\n"
        ":::{grid-item}\n"
        f"\n```{{button-link}} {dl_link_linux}\n:color: primary\n"
        ":shadow:\n:tooltip: Generated with PyInstaller on Ubuntu LTS\n"
        "\n{fab}`linux` Download for Linux\n```\n"
        ":::\n"
        ":::{grid-item}\n"
        f"\n```{{button-link}} {dl_link_macos}\n:color: primary\n"
        ":shadow:\n:tooltip: Generated with PyInstaller on MacOS 12.6\n"
        "\n{fab}`apple` Download for MacOS\n```\n"
        ":::{grid-item}\n"
        ":::\n"
        f"\n```{{button-link}} {dl_link_windows}\n:color: primary\n"
        ":shadow:\n:tooltip: Generated with PyInstaller on Windows 10\n"
        "\n{fab}`windows` Download for Windows\n```\n"
        ":::\n"
        "\n::::"
    )

    Path("./docs/usage/download_section.md").write_text(
        data=out_download_section, encoding="UTF-8"
    )


# run api doc
def run_apidoc(_):
    """Options for Sphinx API doc."""
    from sphinx.ext.apidoc import main

    cur_dir = os.path.normpath(os.path.dirname(__file__))
    output_path = os.path.join(cur_dir, "_apidoc")
    modules = os.path.normpath(os.path.join(cur_dir, "../qgis_deployment_toolbelt/"))
    exclusions = ["../input", "../output", "/tests"]
    main(["-e", "-f", "-M", "-o", output_path, modules] + exclusions)


# launch setup
def setup(app):
    app.connect("builder-inited", run_apidoc)
    # app.connect("builder-inited", populate_download_page)
