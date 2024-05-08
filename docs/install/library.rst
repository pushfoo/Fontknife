
.. _install_library:


Library Install
===============

.. _install_pin_versions: https://pip.pypa.io/en/stable/topics/repeatable-installs/

This page is for developers who want to use |project_name| from
Python code.

If you only want a command line utility, see please see
:ref:`install_user`.

Overview: Pin Your Packages!
----------------------------

**TL;DR: Keep your code working by telling pip to use specific
package versions.**

What's Pinning?
^^^^^^^^^^^^^^^

.. _semver: https://semver.org/

By default, ``pip install`` will install the latest version of a
package released. This can break your code if the latest release
of a package changes features your code relies on.

To keep your code working, you can tell ``pip`` to use a specific
version. This is called **pinning** a package.

.. _usage_library_why_pin:

Why Pin Packages?
^^^^^^^^^^^^^^^^^

Before version 1.0, projects often change unexpectedly. |project_name|
is no exception. Things **will** break until it reaches 1.0:

* Large changes may release without warning
* Doc may end up lacking features or become incorrect

.. _usage_library_how_pin:

How do I Pin?
^^^^^^^^^^^^^

.. _requirements_txt: https://pip.pypa.io/en/latest/user_guide/#requirements-files
.. _Rye: https://rye-up.com/
.. _Poetry: https://python-poetry.org/


If you're using a tool like `Rye`_ or `Poetry`_, consult their
documentation. Otherwise, continue reading.


1. Find where you specify dependencies
--------------------------------------

In requirements.txt
^^^^^^^^^^^^^^^^^^^
The simplest and oldest way is a ``requirements.txt`` file. These
have one package per line. Example:

.. code-block::

   example_package_name == 1.0
   another_example_name == 2.1

In pyproject.toml
^^^^^^^^^^^^^^^^^
It's often better to use a ``pyproject.toml`` file instead of
``requirements.txt``. Although the TOML-based format is more complex, it
adds features which are often worth it for most projects. You can create
or edit it directly if you aren't using a tool which generates it for you
like `Poetry`_ does.

To add |project_name| as a dependency:

#. Open ``pyproject.toml``
#. Search for a ``[project]`` heading
#. Look for a ``dependencies``  variable under it which looks like this

   .. The example below isn't a code-block:: because it'd syntax
   .. highlight and become inconsistent with the templated example
   .. .. parsed-literal:: blocks below. TODO: Fix this flaw ;_;

   .. parsed-literal::

      [project]
      dependencies = [
        'example_package_name == 1.0',
        'another_example_name == 1.1'
      ]

Other Options
^^^^^^^^^^^^^

If you haven't chosen an option, consider ``pyproject.toml`` or
`Poetry`_. If you're working on an existing project and it's using
another dependency management approach, consult the relevant
documentation.

2. Choose: Safety or Freshness?
-------------------------------

Safe & Stable
^^^^^^^^^^^^^

.. _PyPI Release history:  https://pypi.org/project/fontknife/#history

The current latest version is specified by this string:

   .. parsed-literal::

      |package_as_dep_latest_stable|

You can choose from other versions on PyPI by checking |project_name|'s
`PyPI Release history`_.


Advanced: Straight from GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: These versions **will** be buggy!

             Even if builds pass tests, this is a pre-release WIP unless it's
             a release commit. Again, things **will break!**

Very adventurous users can install directly from the latest commit
at the time of build by using the following:

   .. parsed-literal::

      |dependency_zipball_line|


3. Add |project_name| to your dependencies
------------------------------------------

Adding it to requirements.txt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say your ``requirements.txt`` looks like the example from
earlier:

.. code-block::

   example_package_name == 1.0
   another_example_name == 2.1

To add a released version of |project_name|, add it at the end
as shown below:

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1
   |package_as_dep_latest_stable|

You can also choose any other version listed in |project_name|'s
`PyPI Release history`_.

If you want a zipball for a specific commit regardless of stability,
you can add it like this:

.. parsed-literal::

   example_package_name == 1.0
   another_example_name == 2.1
   |dependency_zipball_line|


Adding it to pyproject.toml
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assume your ``pyproject.toml``'s dependencies are simple and
looks like this:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.2'
   ]

To add a released version to ``pyproject.toml``, add it to the
dependencies list you found earlier:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|package_as_dep_latest_stable|'
   ]

To install from a specific commit on GitHub, you'd add it like this:

.. parsed-literal::

   [project]
   dependencies =[
       'example_package_name == 1.0',
       'another_example_name == 2.1'
       '|dependency_zipball_line|'
   ]

For more complicated situations, like dev and doc dependencies, you may
need to add similar lines to other sections. This may be either in addition
or instead of the onies shown here.

4. Update & Resolve Any Conflicts
----------------------------------

Assuming you don't need dev or docs dependencies, re-install packages by
running ``pip install -Ie .``. If you get conflicts, you'll need to resolve
these. This is outside the scope of this document.