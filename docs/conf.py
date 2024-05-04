# Customized sphinx build config with elegant bells & whistles
#
# Full built-in configuration value doc can be found here:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations  # Partial | support on Python 3.8+

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
# -- Sphinx has some odd logging choices, so let's try to fix some! -- #
#                                                                      #
# What's been tried & doesn't work for fixing those odd decisions:     #
#                                                                      #
# 1. base_python_logging.basicConfig(                                  #
#       format="%(levelname)-8s: %(created)s : %(message)", style="%") #
#                                                                      #
#    For some reason, Sphinx thought it'd be a good idea to hardcode   #
#    prefixes. This overrides any formatting config to helpfully       #
#    'ensure consistency'. Okay... :/                                  #
#                                                                      #
# 2. logging.SphinxInfoLogRecord.prefix = 'INFO: '                     #
#                                                                      #
#    Even worse, we can't override SphinxInfoLogRecord.prefix because  #
#    Sphinx seems to using its own logging functions without a newline #
#    at the end. This would be fine if it didn't clobber formatting.   #
#                                                                      #
# So what can we do about this nasty SphinxLoggingAdapter we get? For  #
# now, not much. Too many things are unfinished or broken to spend any #
# time polishing this build script to perfection. Afterwards, we will  #
# probably have to live with our hideously unaligned columns for years #
# like filthy animals. After all, there's no fix more permanent than a #
# temporary fix! Since you made it through this entire block, here are #
# some more aesthetic shorthand functions to make your life a bit more #
# tolerable after reading all of this.                                 #
#                                                                      #
#                              ¯\_(ツ)_/¯                              #
#                                                                      #
########################################################################


def debug(msg: str, *args, **kwargs) -> None:
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Force-prefix INFO since Sphinx doesn't us to have nice things.

    This is the best we can do since colum aligment is too much to ask
    for. See above comment block. :(
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
        on_fail: Callable = critical,  # fn(msg, e: Exception | None = None)
        on_attempt: Callable = lambda a: info(f"Attempting to {a}..."),
        on_success: Callable = lambda _: info("Success!"),
) -> Generator[str, None, None]:
    """Organize task results in code & logs, including traceback."""
    on_attempt(action)
    try:
        yield action
    except Exception as e:
        on_fail(f"Failed to {action}!", e)
    on_success(action)


########################################################################
#                       External Utility Helpers                       #
########################################################################

# Some light typing to help things along
T = TypeVar('T')
R = TypeVar('R')
# Used to process the return values of the ugly function below
Converter = Callable[[T], R]


def run_and_regex(
        command: str | Iterable[str],
        named_group_extractor: Pattern,  # MUST use named groups!
) -> dict[str, str]:
    """Run console progams & extract data via regex"""
    if "(?P<" not in named_group_extractor.pattern:
        raise ValueError("This pattern MUST use named groups!")

    # Run & attempt to match with the extractor pattern
    result = subprocess.run(
        command, check=True,  # Auto-raise on non-zero error codes
        # Open stdout in text mode and decode the underlying stream as utf-8
        capture_output=True, encoding='utf-8', text=True)
    cleaned = result.stdout.strip(" \n\"")
    info(f"Got cleaned info {cleaned!r}")
    match = named_group_extractor.match(cleaned)

    # Raise a ValueError if the data we got seems malformed
    # TIP: if you suddenly get this, double check the regex you passed
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

COMMIT_SIMPLE_REGEX = re.compile(
    r'(?P<isodate>[^\s]+) +(?P<branch>\([^)]+\)) +(?P<full_hash>[a-fA-F0-9]+)'
)
# The full_hash is used to:
# 1. Template a bleeding edge zipball dependency line in the install guide.
# 2. Allow fuller debug info if we want it
#
# It's also used for the same reasons the timestamp is:
# 1. Make broken builds clearer
# 2. Preventing confusion in annoying edge cases:
#    * Around holidays or other times devs may be distracted
#    * The first 2-3 months after New Year's Eve
#    * Builds of historic / maintenance versions for comparison


# The raw branch output of git varies for unclear reasons. Figuring out
# why doesn't seem worth the time when more important things need to be
# fixed & finished. Trying patterns in series is faster than regex golf.
def extract_branch_name(
    raw: str,
    regexes: Iterable[Pattern] = tuple(
        re.compile(p) for p in (
            # The readthedocs build runner shows git's branch like this
            r'HEAD, origin\/(?P<branch>\w+), origin\/HEAD, (?P&branch)',
            # Local dev machines seem to favor this form
            r'\(HEAD -> (?P<branch>[a-zA-Z0-9_\-]+)(, \w+)*\)'
        )
    )
) -> str | None:
    for pattern in regexes:
        debug(f"Trying pattern r'{pattern.pattern}'")
        match = pattern.match(raw)
        if match:
            return match.group('branch')
    return None


########################################################################
#             Start of Sphinx Configuration Actions & Data             #
########################################################################

# -- Misc config items without much room for config exceptions --

root_doc = "index"
source_suffix = ".rst"

# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Conditional inclusion like .. only::, but with Python expressions
    'sphinx.ext.ifconfig',
    # Workaround for the limitations of replace:: since it can use
    # directives, but not most forms of inline formatting. See below.
    'sphinx.ext.extlinks'  # Configured after pyproject & git are read
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


# --  Read git HEAD & pyproject.toml to start configuring the build --

with attempt_to("read git HEAD"):
    git_head = run_and_regex(
        ['git', 'log', '-1', '--format="%aI %d %H"'],
        COMMIT_SIMPLE_REGEX)

    git_head_datetime: datetime = convert(git_head, 'isodate', datetime.fromisoformat)
    branch = convert(git_head, 'branch', extract_branch_name)
    full_commit_hash = git_head['full_hash']

    stable = branch.startswith('stable')
    info(f"Detected {'stable' if stable else 'UNSTABLE'} branch, {stable=}")


with attempt_to("read pyproject.toml for Sphinx config pre-reqs"):
    pyproject_toml = tomllib.loads((HERE.parent / "pyproject.toml").read_text())
    project_section = pyproject_toml['project']
    source_url = project_section['urls']['Source']
    doc_url = project_section['urls']['Documentation']
    doc_base_url = doc_url[:-len('latest')]  # Trim end, but leave the slash

# Allow templating external links with custom directives.
# If caption is None, the whole URL will show unless you use
# :directivename:`customname <original>` as with refs / etc.
extlinks = {  # Each entry is you directivename: (url, caption)
    'ghbranch': (f"{source_url}/tree/%s", '%s branch'),
    'ghcurrentbranch': (f"{source_url}/tree/{branch}", None),
    'docbuildfor': (f"{doc_base_url}%s", "%s doc")
}


# -- Configuration variables read by Sphinx from the values in this file --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
with attempt_to("template core Sphinx config variables"):

    package_name = project_section['name']
    project = str.capitalize(package_name)
    author = f"{project} contributors"
    copyright = f'{git_head_datetime.year}, {author}'

    # -- Handle stable vs dev boilerplate --
    version = project_section['version']
    release = version


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


# -- Log our config generation win to console. :) --
info("Finished processing git HEAD & pyproject.toml into the rst_prolog below:")
print()
print('rst_prolog = f"""')
print(rst_prolog)
print('"""')
print()


def setup(app):
    app.add_config_value(
        'unstable_branch', None if stable else branch, 'env')


info("Proceeding to output phase")
