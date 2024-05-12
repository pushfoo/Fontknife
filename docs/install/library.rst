.. _library-install:

Library Install
===============

.. _install_pin_versions: https://pip.pypa.io/en/stable/topics/repeatable-installs/

This page you use |project_name|'s current features from your own
Python code.

.. list-table::
   :header-rows: 1

   * - |if_need_to|
     - |may_want|

   * - Convert font data in the terminal
     - |redir_to_use|

   * - Contribute fixes or new features
     - |redir_contributing|


Overview: Pin Your Packages!
----------------------------

**TL;DR: Keep your code working by telling pip to use specific
package versions.**

.. toctree::
   :hidden:

   ./choosing_a_dependency_approach


What's Pinning?
^^^^^^^^^^^^^^^

.. _semver: https://semver.org/

By default, ``pip install`` fetches the latest release of a package.
This can break your code if the latest release changes features or
behavior your code relies on.

To keep your code working, you can tell ``pip`` to use a specific
version. This is called **pinning** a package.

.. _usage_library_why_pin:

Why Pin Packages?
^^^^^^^^^^^^^^^^^

Before version 1.0, projects often change unexpectedly. |project_name|
is no exception. Things **will** break and change until it reaches 1.0.
Many of them could break your code:

* Large changes may release without warning
* Doc may end up lacking features or become incorrect


.. _usage_library_how_pin:

How do I Pin?
^^^^^^^^^^^^^

This depends on how you manage dependencies.

.. list-table::
   :header-rows: 1

   * - If you're...
     - |may_want_to|:

   * - Not using any dependency management
     - :ref:`library-install-choosing_dependency-approach`

   * - Using ``requirements.txt`` or ``pyproject.toml``
     - Skip to :ref:`install-library-find_deps_section`

   * - Automating dependency management with a tool like:

       * `Rye`_
       * `Poetry`_

     - See the next section


My Favorite Tool Manages Dependencies
"""""""""""""""""""""""""""""""""""""

.. _rye_deps_intro: https://rye-up.com/guide/basics/#adding-dependencies
.. _rye_deps_full: https://rye-up.com/guide/deps/
.. _poetry_deps_intro: https://python-poetry.org/docs/managing-dependencies/
.. _poetry_deps_full: https://python-poetry.org/docs/basic-usage/#installing-dependencies

That's okay too. It means you can :wikipedia:`speedrun <Speedrunning>`
this page. Start with the table below and copying down the dependency
line which sounds preferable.

.. list-table::
   :header-rows: 1

   * - |if_need|
     - |may_want|

   * - Safety
     - |dep_line_latest_stable|

   * - New Features
     - |dep_line_commit_zipball|


You'll want to consult your tool's documentation from this point. For
your convenience, links for Rye and Poetry's documentation are provided
below.

.. list-table::
   :header-rows: 1

   * - `Rye`_
     - `Poetry`_

   * - `Rye's Dependency Intro <rye_deps_intro>`_
     - `Rye's Dependency Guide <rye_deps_full>`_

   * - `Poetry's Dependency Intro <poetry_deps_intro>`_
     - `Poetry's Dependency Guide <poetry_deps_guide>`_

If you're using another tool, please consult its documentation.


.. _install-library-find_deps_section:

1. Find where you specify dependencies
--------------------------------------

.. tip:: If you don't specify them anywhere yet, that's okay.

.. _library-install-requirements.txt:

In requirements.txt
^^^^^^^^^^^^^^^^^^^

.. _requirements.txt: https://pip.pypa.io/en/latest/user_guide/#requirements-files

The simplest way is a ``requirements.txt`` file. These have one package
per line. For example:

.. None of the examples on this page use .. code-block:: because:
.. 1. It triggers more auto-highlighting on them than it already does
.. 2. Those will be even more inconsistent with the style of the ones
..    which include a replacement.
.. TODO: Fix this ugly flaw ;_;

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1


To learn more, see ``pip``'s
`documentation on requirements.txt <requirements.txt>`_.

.. _library-install-pyproject.toml:

In pyproject.toml
^^^^^^^^^^^^^^^^^

If you have a ``pyproject.toml``, it's probably at the root of your
project's repo folder.

If you see it, open it and search for a ``[project]`` section. It should
have a ``dependencies`` value which looks something like this:

   .. parsed-literal::

      [project]
      dependencies = [
        'example_package_name == 1.0',
        'another_example_name == 2.1'
      ]

This is where you'll be adding the dependency line.

2. Choose: Safety or Freshness?
-------------------------------

Safe & Stable
^^^^^^^^^^^^^

.. _PyPI Release history:  https://pypi.org/project/fontknife/#history

The current latest version is specified by this string:

.. parsed-literal::

   |dep_line_latest_stable|

You can choose from other versions on PyPI by checking |project_name|'s
`PyPI Release history`_.


Advanced: Straight from GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: These versions **will** be buggy!

             Even if builds pass tests, this is a pre-release WIP unless
             it's a release commit. Again, things **will break!**

Very adventurous users can install directly from the latest commit
at the time of build by using the following:

.. parsed-literal::

   |dep_line_commit_zipball|


3. Add |project_name| to your dependencies
------------------------------------------

.. _install-library-requirements.txt:

Adding it to requirements.txt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say your ``requirements.txt`` looks like the example from
earlier:

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1

To add a released version of |project_name|, add it at the end
as shown below:

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1
   |dep_line_latest_stable|

You can also choose any other version listed in |project_name|'s
`PyPI Release history`_.

If you want a zipball for a specific commit regardless of stability,
you can add it like this:

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1
   |dep_line_commit_zipball|


Adding it to pyproject.toml
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assume your ``pyproject.toml``'s dependencies are simple and
looks like this:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
   ]

To add a released version to ``pyproject.toml``, add it to the
dependencies list you found earlier:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|dep_line_latest_stable|'
   ]

To install from a specific commit on GitHub, you'd add it like this:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|dep_line_commit_zipball|'
   ]

For more complicated situations, like dev and doc dependencies, you may
need to add similar lines to other sections. This may be either in
addition or instead of the onies shown here.

Cleanup: Update & Resolve Any Conflicts
---------------------------------------

Assuming you don't need dev or docs dependencies, re-install packages by
running ``pip install -Ie .``. If you get conflicts, you'll need to
resolve these. This is outside the scope of this document.

Otherwise, run any tests once the conflicts are resolved. If they pass,
you're done!
