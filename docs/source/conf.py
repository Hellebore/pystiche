# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full list see
# the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Imports ---------------------------------------------------------------------------

import os
import shutil
import warnings
from datetime import datetime
from distutils.util import strtobool
from os import path
from urllib.parse import urljoin

from sphinx_gallery.sorting import ExampleTitleSortKey, ExplicitOrder

import torch

import pystiche
from pystiche.misc import download_file

# -- Run config ------------------------------------------------------------------------


def get_bool_env_var(name, default=False):
    try:
        return bool(strtobool(os.environ[name]))
    except KeyError:
        return default


run_by_github_actions = get_bool_env_var("GITHUB_ACTIONS")
run_by_travis_ci = get_bool_env_var("TRAVIS")
run_by_appveyor = get_bool_env_var("APPVEYOR")
run_by_rtd = get_bool_env_var("READTHEDOCS")
run_by_ci = (
    run_by_github_actions
    or run_by_travis_ci
    or run_by_appveyor
    or run_by_rtd
    or get_bool_env_var("CI")
)

# -- Path setup ------------------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory, add
# these directories to sys.path here. If the directory is relative to the documentation
# root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

PROJECT_ROOT = path.abspath(path.join(path.dirname(__file__), "..", ".."))


# -- Project information ---------------------------------------------------------------

project = pystiche.__name__
author = pystiche.__author__
copyright = f"2019 - {datetime.now().year}, {author}"
version = release = pystiche.__version__


# -- General configuration -------------------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
    "sphinx_autodoc_typehints",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and directories to
# ignore when looking for source files. This pattern also affects html_static_path and
# html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- intersphinx configuration ---------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.6", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
    "torchvision": ("https://pytorch.org/docs/stable/", None),
    "PIL": ("https://pillow.readthedocs.io/en/stable/", None),
    "numpy": ("https://numpy.org/doc/1.18/", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
    "matplotlib": ("https://matplotlib.org", None),
}


# -- sphinx-gallery configuration ------------------------------------------------------

extensions.append("sphinx_gallery.gen_gallery")

plot_gallery = get_bool_env_var("PYSTICHE_PLOT_GALLERY", default=True) and not run_by_ci

download_gallery = get_bool_env_var("PYSTICHE_DOWNLOAD_GALLERY") or run_by_ci

if download_gallery:
    base = "https://download.pystiche.org/galleries/"
    file = (
        "master.zip"
        if pystiche.__about__._IS_DEV_VERSION
        else f"v{pystiche.__base_version__}.zip"
    )

    url = urljoin(base, file)
    print(f"Downloading pre-built galleries from {url}")
    download_file(url, file)

    shutil.unpack_archive(file, extract_dir=".")
    os.remove(file)

if plot_gallery and not torch.cuda.is_available():
    msg = (
        "The galleries will be built, but CUDA is not available. "
        "This will take a long time."
    )
    print(msg)


def show_cuda_memory(func):
    torch.cuda.reset_peak_memory_stats()
    out = func()

    stats = torch.cuda.memory_stats()
    peak_bytes_usage = stats["allocated_bytes.all.peak"]
    memory = peak_bytes_usage / 1024 ** 2

    return memory, out


sphinx_gallery_conf = {
    "examples_dirs": path.join(PROJECT_ROOT, "examples"),
    "gallery_dirs": path.join("galleries", "examples"),
    "filename_pattern": os.sep + "example_",
    "line_numbers": True,
    "remove_config_comments": True,
    "plot_gallery": plot_gallery,
    "subsection_order": ExplicitOrder(
        [
            path.join("..", "..", "examples", sub_gallery)
            for sub_gallery in ("beginner", "advanced")
        ]
    ),
    "within_subsection_order": ExampleTitleSortKey,
    "show_memory": show_cuda_memory if torch.cuda.is_available() else True,
}

# Remove matplotlib agg warnings from generated doc when using plt.show
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=(
        "Matplotlib is currently using agg, which is a non-GUI backend, so cannot show "
        "the figure."
    ),
)


# -- Options for HTML output -----------------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for a list of
# builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
