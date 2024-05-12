.. _library-install:

Library Install
===============

.. _install_pin_versions: https://pip.pypa.io/en/stable/topics/repeatable-installs/

This page you use |project_name|'s current features from your own
Python code.

.. list-table::
   :header-rows: 1

   * - |if_need_to|
     - |may_want_see|

   * - |task_convert|
     - |redir_to_use|

   * - |task_contribute|
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

   * - If you...
     - |may_want_see|

   * - Don't track dependencies yet
     - :ref:`library-install-choosing_dependency-approach`

   * - Use ``requirements.txt`` or ``pyproject.toml``
     - :ref:`install-library-find_deps_section`

   * - Use automatic tools (`Rye`_, `Poetry`_)
     - The heading directly below this line


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

         Try skimming through
         :ref:`library-install-choosing_dependency-approach`.
         If you feel overwhelmed:

         #. Save an empty ``requirements.txt`` file in your project's
            folder
         #. See the heading directly below this sentence

.. _library-install-requirements.txt:

In requirements.txt
^^^^^^^^^^^^^^^^^^^

.. _requirements.txt: https://pip.pypa.io/en/latest/user_guide/#requirements-files

The simplest way to manage dependencies is a ``requirements.txt`` file.

These have one package per line. If yours isn't empty, it may look like
this:

.. None of the examples on this page use .. code-block:: because:
.. 1. It triggers more auto-highlighting on them than it already does
.. 2. Those will be even more inconsistent with the style of the ones
..    which include a replacement.
.. TODO: Fix this ugly flaw ;_;

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1


To add a dependency right away, skip to
:ref:`library-install-safe_or_features`. To learn more first, please
see ``pip``'s `guide to requirements.txt <requirements.txt>`_.

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


.. _library-install-safe_or_features:

2. Choose: Safety or Freshness?
-------------------------------

Safe & Stable
^^^^^^^^^^^^^

.. _PyPI Release history:  https://pypi.org/project/fontknife/#history

The current latest version is specified by this string:

.. parsed-literal::

   |dep_line_latest_stable|

To add it right away:

#. Select the text
#. Copy it to your clipboard
#. Skip to :ref:`install-library-adding-requirements.txt`


You can also choose from other stable versions on PyPI by checking
|project_name|'s `PyPI Release history`_.


Advanced: Straight from GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: Non-release commits **will** break things!

             Even if they seem to pass tests, its no guarantee they
             haven't changed behavior your code relies on.

Very adventurous users can install directly from the latest commit
at the time of build by using the following:

.. parsed-literal::

   |dep_line_commit_zipball|


3. Add |project_name| to your dependencies
------------------------------------------

.. _install-library-adding-requirements.txt:

Adding it to requirements.txt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your ``requirements.txt`` is empty, then:

#. Paste your line
#. Hit save
#. Scroll to the end of this section to finish up

Otherwise, you'll want to add the new line it at the end of the file as
shown below.

A Stable Version in requirements.txt
""""""""""""""""""""""""""""""""""""

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1
   |dep_line_latest_stable|

An unstable zipball in requirements.txt
"""""""""""""""""""""""""""""""""""""""

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

Paste your dependency line at the end.

Stable Version
""""""""""""""

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|dep_line_latest_stable|'
   ]

Unstable Zipball from GitHub
""""""""""""""""""""""""""""

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|dep_line_commit_zipball|'
   ]

For more complicated situations such as dev or doc dependencies,
you may need to add similar lines to other sections. If it's required
for both dev and docs, you may need to add it to both the dev and docs
dependency lists.

Consult the following reference from the Python Packaging Authority
to learn more:

* Their `guide to writing a pyproject.toml`_
* Their well-commented `sample project`_

.. _post-install:

Cleanup: Update & Resolve Any Conflicts
---------------------------------------

You're nearly done.

Your next steps are telling ``pip`` to reinstalling and upgrade
packages. If there are version conflicts, you might have to make
soem choices to resolve them. The details of how are outside this
document's scope.

For requirements.txt
^^^^^^^^^^^^^^^^^^^^

.. _report a bug: https://github.com/pushfoo/Fontknife/issues/new

Run ``pip install -r requirements.txt``.

If your requirements file only has |project_name| in it:

* There should be no dependency conflicts
* If there are, `report a bug`_!

For pyproject.toml
^^^^^^^^^^^^^^^^^^


Run ``pip install -Ie .`` to reinstall anything and everything
which needs it.

Any Tests?
----------

You may want to run any unit tests your project has. If nothing broke
or if you don't have any tests yet, then you're done!
