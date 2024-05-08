# Customized sphinx build config with elegant bells & whistles
#
# Full built-in configuration value doc can be found here:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations  # Partial | support on Python 3.8+

import os
import sys
import traceback
import subprocess  # Sphinx's git rev-parse only gets HEAD's short hash

from pathlib import Path
from textwrap import dedent
from datetime import datetime
from contextlib import contextmanager
from typing import Iterable, Generator, Callable, Pattern, TypeVar

import regex as re  # Supports repeating groups :)
from sphinx.util import logging as nasty_sphinx_logging  # See below :(

HERE = Path(__file__).parent
logger = nasty_sphinx_logging.getLogger(__name__)

########################################################################
# TL;DR: Sphinx's logging forces wrapper functions & unaligned columns #
#                                                                      #
# 1. SphinxLoggingAdapter breaks logging config like the call below:   #
#                                                                      #
#    base_python_logging.basicConfig(                                  #
#       format="%(levelname)-8s: %(created)s : %(message)", style="%") #
#                                                                      #
# 2. Sphinx uses unprefixed & no-newline info logging. This breaks it: #
#                                                                      #
#    logging.SphinxInfoLogRecord.prefix = 'INFO: '                     #
#                                                                      #
# What can we do about SphinxLoggingAdapter's rudeness? For now, we'll #
# settle for the wrapper functions below. We need to spend time on our #
# features and doc, not build script perfection. We'll have to live    #
# with hideously unaligned log columns like filthy animals. After all, #
# no fix is more permanent than a temporary one!                       #
#                                                                      #
#                              ¯\_(ツ)_/¯                              #
#                                                                      #
########################################################################


def debug(msg: str, *args, **kwargs) -> None:
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Force-prefix INFO since Sphinx won't let us have nice things.

    This is the best we can do for now since column alignment is too
    much to ask for. See above comment block. :(
    """
    logger.info(f"INFO: {msg}", *args, **kwargs)


def warn(msg: str, *args, **kwargs) -> None:
    logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    logger.error(msg, *args, **kwargs)


def critical(
        failure_msg: str,  # Will be prefixed with CRITICAL:
        exception: Exception | None = None,  # Log traceback if != None
        exit_code: int = -1,  # The only cross-platform error exit code
        **kwargs  # See LoggingAdapter.critical & SphinxLoggingAdapter
) -> None:
    """Log a failure message & any exception traceback, then exit."""
    logger.critical(failure_msg, **kwargs)
    if exception is not None:
        print()
        print(traceback.format_exc())

    exit(exit_code)


@contextmanager
def attempt_to(
    action: str,  # with attempt_to("perform a specific action"): ...
    on_attempt: Callable = lambda a: info(f"Attempting to {a}..."),
    on_failure: Callable = lambda a, e: critical(f"Failed to {a}!", e),
    on_success: Callable = lambda _: info("Success!"),
) -> Generator[str, None, None]:
    """Organize task results in code & logs, including traceback."""
    on_attempt(action)
    try:
        yield action
    except Exception as e:
        on_failure(action, e)
    on_success(action)


########################################################################
#                       External Utility Helpers                       #
########################################################################

# Some light typing to help things along
T = TypeVar('T')
R = TypeVar('R')
# Used to process the return values of functions
Converter = Callable[[T], R]


def strip_run_stdout(raw_output: str) -> str:
    """Strip annoying cruft from current subprocess runs"""
    return raw_output.strip(" \n\"")


def run_with_post(
    command: str | Iterable[str],
    converter: Converter = strip_run_stdout
) -> R:
    raw = subprocess.run(
        command, check=True,  # Auto-raise on non-zero error codes
        # Open stdout in text mode and decode the underlying stream as utf-8
        capture_output=True, encoding='utf-8', text=True)
    converted = converter(raw.stdout)
    return converted


def run_with_regex(
        command: str | Iterable[str],
        named_group_extractor: Pattern,  # MUST use named groups!
) -> dict[str, str]:
    """Run console programs & extract data via regex"""
    if "(?P<" not in named_group_extractor.pattern:
        raise ValueError("This pattern MUST use named groups!")

    # Run & attempt to match with the extractor pattern
    cleaned = run_with_post(command)
    info(f"Got cleaned info {cleaned!r}")
    match = named_group_extractor.match(cleaned)

    # Raise a ValueError if the data we got seems malformed
    # TIP: if you suddenly get this, double-check:
    # 1. The format flags you passed the CLI command
    # 2. The regex you passed this function to parse it
    if match is None:
        cmd_name = repr(command) if isinstance(command, str) else command[0]
        raise ValueError(f"{cmd_name} output seems malformed: {cleaned!r}")

    return match.groupdict()


def convert(
        source: dict[str, T], key: str, converter: Converter[T, R],
        fail_template: str = "No {key} could be parsed from HEAD"
) -> R:
    """Get & convert values from return values of Match.groupdict()."""
    if not (raw := source.get(key)) or not (converted := converter(raw)):
        raise RuntimeError(fail_template.format(key=key))
    return  converted


########################################################################
#     Preflight Python Version & TOML Compatibility Parsing Checks     #
########################################################################
info(f"Detected Python {sys.version.split()[0]}")

# This file's toml needs are simple enough to count tomli as a backport
if sys.version_info <= (3, 11):
    import tomli as tomllib  # any breaking changes are irrelevant here
    warn("Full tomllib isn't in this Python version! Using tomli fallback")
else:
    import tomllib  # noqa  # PyCharm can't understand the version check
    info("using built-in tomllib")


########################################################################
#                     Git Metadata Parsing Helpers                     #
########################################################################

COMMIT_SIMPLE_REGEX = re.compile(r"""
(?P<isodate>[^\s]+)         # Any non-whitespace for date format info
[ ]+                        # Space between data fields
(?P<full_hash>[a-fA-F0-9]+) # A hash output
""", re.VERBOSE)
# The full_hash is used to:
# 1. Template a bleeding edge zipball install example
# 2. Allow fuller debug info if we want it
#
# It's also used for the same reasons the timestamp is:
# 1. Make broken builds clearer
# 2. Preventing confusion in annoying edge cases:
#    * Around holidays or other times devs may be distracted
#    * The first 2-3 months after New Year's Eve
#    * Builds of historic / maintenance versions for comparison


########################################################################
#             Start of Sphinx Configuration Actions & Data             #
########################################################################

# -- Misc config items without much room for config exceptions --

root_doc = "index"
source_suffix = ".rst"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Conditional inclusion like r".. only::" but with Python expressions
    'sphinx.ext.ifconfig',
    # Enable cross-linking other Sphinx doc with :ref: & API directives.
    'sphinx.ext.intersphinx',
    # -- External links for APIs & templated links --
    # IMPORTANT: r"replace::" defs in rst_epilog don't directly support
    # link definitions! However, they *do* support directives, and that
    # includes custom link directives generated by extlinks config.
    'sphinx.ext.extlinks',
]


intersphinx_mapping = dict(
    python=(
        'https://docs.python.org/3', None),
    PIL=(
        'https://pillow.readthedocs.io/en/stable', None))


# --  Read git state & pyproject.toml to start configuring the build --

with attempt_to("read git HEAD"):
    git_head = run_with_regex(
        ['git', 'log', '-1', '--format="%aI %H"'],
        COMMIT_SIMPLE_REGEX)
    git_head_datetime: datetime = convert(git_head, 'isodate', datetime.fromisoformat)
    full_commit_hash = git_head['full_hash']
    short_commit_hash = full_commit_hash[:8]

    # -- Try to parse branch, but give up if in detached head state --
    raw_branch = run_with_post(
        ['git', 'status', '-s', '-b'],
        converter=lambda s: s.strip("\"").split("\n")[0])
    info(f"Got raw status 1st line: status={raw_branch!r}")

    # No need to guess since we can use the READTHEDOCS(_*)? env vars
    if "no branch" in raw_branch:
        branch = None
        _branch_reported = 'detached HEAD state'
    else:
        branch = raw_branch[2:].strip().split('.')[0]
        _branch_reported = f"{branch=}"
    info(f"Detected {_branch_reported}, {full_commit_hash=}")


with attempt_to("read pyproject.toml for Sphinx config pre-reqs"):
    pyproject_toml = tomllib.loads((HERE.parent / "pyproject.toml").read_text())
    project_section = pyproject_toml['project']
    source_url = project_section['urls']['Source']
    doc_url = project_section['urls']['Documentation']
    doc_base_url = doc_url[:-len('latest')]  # Trim end, but leave the slash


# -- Configuration variables read by Sphinx from the values in this file --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
with attempt_to("template core Sphinx config variables"):

    package_name = project_section['name']
    project = str.capitalize(package_name)
    author = f"{project} contributors"
    copyright = f'{git_head_datetime.year}, {author}'

    # -- Start version & warning display --
    # https://docs.readthedocs.io/en/stable/reference/environment-variables.html
    on_readthedocs = 'True' == os.environ.get('READTHEDOCS', None)
    readthedocs_name = os.environ.get('READTHEDOCS_VERSION_NAME', None)
    stable_build = on_readthedocs and readthedocs_name == 'stable'

    if on_readthedocs:
        version = project_section['version']
    else:
        version = f"[LOCAL] {branch} {short_commit_hash}"

    release = version
    html_title = f"{project} {version}"


# -- External & inter-version doc links --

# -- Allow templating external links with custom directives. --
#
# Each entry below is declared as r"name_str: (url_fmt, caption_fmt)."
# From an .rst file, they can be invoked as r":name_str:`to_template`".
# If an entry's caption_fmt is None, its whole URL will show unless you
# override the display text the same way you can with :ref: and other
# directives. For example:
#
#   r":ghcurrentbranch:`This will be the link text <to_template>`".
#
# Since substitution rules don't allow complex formatting, defining an
# extlinks-based custom directive is currently the best way to allow
# substitution rules to include links.
extlinks = {
    'ghbranch': (
        f"{source_url}/tree/%s", '%s branch'),
    'ghcurrentbranch': (
        f"{source_url}/tree/{branch}", None),
    'docbuildfor': (
        f"{doc_base_url}%s", "%s doc"),
    'codepoint': (
       f"https://unicode-explorer.com/c/%s",
       "U+%s"
    ),
    'wikipedia': (
        f"https://en.wikipedia.org/wiki/%s",
        "%s"),
    'simplewiki': (
        f"https://simple.wikipedia.org/wiki/%s",
        "%s"
    ),
    'wikipedia-long': (
        f"https://en.wikipedia.org/wiki/%s",
        "English Wikipedia's %s Article"),
    'simplewiki-long': (
        f"https://simple.wikipedia.org/wiki/%s",
        "Simple Wikipedia's %s Article"
    ),
    # Google fonts glossary
    'gfonts-gloss': (
        f"https://fonts.google.com/knowledge/glossary/%s",
        f"The Google Fonts Glossary page for %s"
    ),
    # Project dependencies, but pretty printed in the doc
    'pypi-dep-page': (
        'https://pypi.org/project/%s/',
        f"%s"
    ),
}


########################################################################
#                   Single-Sourced Truth Definitions                   #
########################################################################

# Centralizes min Python version, but not a Sphinx config var per se
with attempt_to('get minimum python version'):
    min_python_version = project_section['requires-python'].strip('>=')

# -- Custom substitution definitions to save us from page desync --
# IMPORTANT: |release| and |version| are auto-added to this using
# the values of the variables with the same names defined above.
# https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#substitutions
with attempt_to("template rst_prolog"):

    rst_prolog = dedent(f"""
        .. |project_name| replace:: {project}
        .. |package_name| replace:: {package_name}
        .. |branch_name| replace:: ``{branch}``
        .. |branch_github_link| replace:: :ghbranch:`{branch}`
        .. |full_commit_hash| replace:: {full_commit_hash}
        .. |min_python_version| replace:: {min_python_version}
        .. |min_python_version_cli_name| replace:: ``python{min_python_version}``
        .. |min_python_version_plus| replace:: Python {min_python_version}+
        .. |dependency_pypi_line| replace:: '|package_name| == |release|'
        .. |dependency_zipball_line| replace:: '|package_name| @ {source_url}/zipball/{full_commit_hash}'
        """).strip()
    #       .. |ZWJ| replace:: :codepoint:`ZWJ (U+200D) <200D>`

    # -- Add warning to top of all pages on local & unstable builds --
    # NOTE: You can override this with env vars or ./fake_stable.sh
    if stable_build:
        build_warning = None
    elif on_readthedocs:
        build_warning = "an unstable |branch_github_link| preview build"
        html_title = f"[{readthedocs_name}] {html_title}"
    else:
        build_warning = f"a local build of the {branch} branch"
        html_title = f"[LOCAL: {branch}] {html_title}"

    if build_warning:
        rst_prolog += dedent(f"""
            .. warning:: This page is {build_warning}!

                        See the :docbuildfor:`stable` for a safer version.
            """).rstrip()


# -- Log our config generation win to console. :) --
info("Finished processing git HEAD & pyproject.toml into the rst_prolog below:")
print()
print('rst_prolog = f"""')
print(rst_prolog)
print('"""')
print()


def setup(app):
    app.add_config_value('unstable_branch', None if stable_build else branch, 'env')


info("Proceeding to output phase")

# -- Options for HTML output --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']