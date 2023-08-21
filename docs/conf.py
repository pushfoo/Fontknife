# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations
from itertools import chain
from pathlib import Path
from typing import Any, Mapping

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys


# Use tomli on versions before tomllib was added to the core library
if sys.version_info < (3, 11):
    import tomli as tomllib


def multi_get(source: Mapping, *name: str, **name_default: Any):
    """
    Fetch multiple pieces of data from a mapping at once.

    * Unlike :py:meth:`dict.get`, names in ``*name`` absent from
      ``source`` will raise a :py:class`KeyError`.
    * Values in ``**name_default.items()`` provide a default for each
      name.

    :param source: The source mapping.
    :param name: Names which must be present in ``source``'s keys.
    :param name_default: Names which will use a provided default if they
        are absent from ``source``.
    :return: The val
    """
    value = tuple(chain(
        (source[n] for n in name),
        (source.get(n, d) for n, d in name_default.items())
    ))
    return value[0] if len(value) == 1 else value


# Read the toml for data
toml_data = tomllib.loads(Path("../pyproject.toml").read_text())
project_data = toml_data['project']

project, release = multi_get(project_data, 'name', 'version')
project = project.capitalize()
author = f"{project} contributors"
copyright = f'2023, {author}'
min_python = project_data['requires-python'][2:]


# Custom substitution definitions
rst_prolog = """
.. |project_name| replace:: {project}
.. |current_project_release| replace:: {release}
.. |min_python_version| replace:: {min_python_version}
.. |min_python_version_cli_name| replace:: ``python{min_python_version}``
.. |min_python_version_plus| replace:: Python {min_python_version}+  
""".format(
    project=project,
    release=release,
    min_python_version=min_python
)


root_doc = "index"
source_suffix = ".rst"

# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
