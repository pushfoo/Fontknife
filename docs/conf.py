# Customized sphinx build config with elegant bells & whistles
#
# Full built-in configuration value doc can be found here:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations


import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import TypedDict

# This file's toml needs are simple enough to count tomli as a backport
if sys.version_info <= (3, 11):
    import tomli as tomllib  # any breaking changes are irrelevant here
else:
    import tomllib  # noqa  # PyCharm can't understand the version check


COMMIT_SIMPLE_REGEX = re.compile(
    r'(?P<unix_timestamp>\d+) +(?P<branch>\([^)]*\)) +(?P<full_hash>[a-fA-F0-9]+)'
)


class GitCommitMetadata(TypedDict):
    """Stores result of above regex for build time visibility & examples.

    The hash is used to template a bleeding edge zipball dependency line
    in the install guide.

    It's also used for the same reasons the timestamp is:

    1. Making broken builds clearer
    2. Preventing confusion in annoying edge cases:
       * The first 2-3 months after New Year's Eve
       * Around holidays or other times devs may be distracted
       * Builds of historic / maintenance versions for comparison

    * a bleeding edge zipball dependency line & making
    broken RTD builds clearer to people without GitHub knowhow
    showing broken RTD builds.

    """
    unix_timestamp: int | None
    branch: str | None
    full_hash: str | None


def get_commit_metadata() -> GitCommitMetadata:
    """Extract metadata from the currently checked out commit.

    Zero configurable input means no injected shell command nonsense :)
    """
    # Don't use text=True because it adds nasty extra formatting
    result = subprocess.run(
        ['git', 'log', '-1', '--format="%at %d %H"'],
        capture_output=True,
    )
    cleaned = result.stdout.decode('utf-8').strip(" \n\"")
    exit_code = result.returncode
    if exit_code != 0:
        raise RuntimeError(f"git failed with exit status {exit_code}: {cleaned!r}")

    match = COMMIT_SIMPLE_REGEX.match(cleaned)
    if match is None:
        raise RuntimeError(f"git output seems malformed: {cleaned!r}")

    kwargs = match.groupdict()

    if (t := kwargs.get('unix_timestamp')) is not None:
       kwargs.update({'unix_timestamp': int(t)})

    return GitCommitMetadata(**kwargs)


# Read the current git commit full hash & raw timestamp
git_head = get_commit_metadata()
git_head_datetime = datetime.fromtimestamp(git_head['unix_timestamp'])


# Read pyproject.toml for data to configure our doc build
pyproject_toml = tomllib.loads(Path("../pyproject.toml").read_text())
pyproject_project_section = pyproject_toml['project']
urls = pyproject_project_section['urls']
source_url = urls['Source']


# -- Project information variables, these are used as config sources ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'Fontknife'
package_name = pyproject_project_section['name']
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
.. |project_name| replace:: {project_name}
.. |package_name| replace:: {package_name}
.. |doc_commit_branch| replace:: {branch}
.. |doc_commit_hash| replace:: {full_hash}
.. |min_python_version| replace:: {min_python_version}
.. |min_python_version_cli_name| replace:: ``python{min_python_version}``
.. |min_python_version_plus| replace:: Python {min_python_version}+  
.. |dependency_pypi_line| replace:: '|package_name| == |release|'
.. |dependency_zipball_line| replace:: '|package_name| @ {source_url}/zipball/{full_hash}'
""".format(  # str.format handles dicts more elegantly than f-strings
    project_name=project,
    source_url=source_url,
    **git_head,
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
