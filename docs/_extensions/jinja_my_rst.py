"""Run Jinja2 on all .rst source files read before any syntax is parsed.

.. warning:: This is inefficient right now!

             It processes **all** files without any selectivity each
             time a source file is read!

Caching helps local builds after the initial build. Its current state
may not be ready for larger codebases, but can try if you want. :')
"""
from sphinx.util import logging
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata


log = logging.getLogger(__file__)


def jinja_my_rst(app, docname, source) -> None:

    log.info(f"jinja_all_rst processing {docname=}...")
    source_code = source[0]

    # TL;DR: This is awful and there's definitely a better way.
    # We're leaving it here because bad is good enough for now.
    # The SEO / AI spam is killing google and I haven't had
    # enough time to finish doing the deep-dive on directives yet,
    # so efficient selectivity will have to wait.
    # if source_code.startswith('.. jinja'):
    #     log.info(f"{docname} marked for jinja")
    # else:
    #     log.info(f"{docname}")

    output = app.builder.templates.render_string(
        source_code, app.config.html_context
    )
    source[0] = output


def setup(app: Sphinx) -> ExtensionMetadata:
    app.connect('source-read', jinja_my_rst)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
