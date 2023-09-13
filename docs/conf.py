# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import subprocess
from pathlib import Path
from datetime import datetime


# Use tomli on versions predating tomllib, ie < 3.11
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# Read the git timestamp to provide the copyright year.
# This prevents confusion during the following edge cases:
# 1. The first 2-3 months after New Year's Eve
# 2. Around holidays or other times developers may be distracted
# 3. Retrospective builds of historical documentation versions
git_head_timestamp = int(
    subprocess.run(['git', 'log', '-1', '--format="%at"'], capture_output=True)
        .stdout
        .decode('utf-8')
        .strip('"\n')
)
git_head_datetime = datetime.fromtimestamp(git_head_timestamp)


# Read pyproject.toml for data to configure our doc build
pyproject_toml = tomllib.loads(Path("../pyproject.toml").read_text())
pyproject_project_section = pyproject_toml['project']


# -- Project information variables, these are used as config sources ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'Fontknife'
package_name=pyproject_project_section['name']
author = f"{project} contributors"
copyright = f'{git_head_datetime.year}, {author}'
release = pyproject_project_section['version']
version = '.'.join(release.split('.')[2:])  # This looks odd but matches sphinx spec


# Custom substitutions usable in RST doc
# |release| and |version| are automatically added by sphinx
PROLOG_KEYS = dict(
    package_name=package_name,
    min_python_version=pyproject_project_section['requires-python'][2:],
)
# Custom substitution definitions
# https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#substitutions
rst_prolog = """
.. |package_name| replace:: {package_name}
.. |min_python_version| replace:: {min_python_version}
.. |min_python_version_cli_name| replace:: ``python{min_python_version}``
.. |min_python_version_plus| replace:: Python {min_python_version}+  
.. |dependency_line| replace:: |package_name|\ ==\ |release|\ 
""".format(
    **PROLOG_KEYS
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
