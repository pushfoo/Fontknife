
.. _usage_library:


Library Usage
=============

.. _pin_versions: https://pip.pypa.io/en/stable/topics/repeatable-installs/

This page is for developers who want to use |project_name| from the
Python code of a project.

Overview: Pin Your Packages!
----------------------------

**TL;DR: Keep your code working by telling ``pip`` to use specific
package versions.**

What's Pinning?
^^^^^^^^^^^^^^^

.. _semver: https://semver.org/

By default, ``pip install`` will install the latest version of a
package released. This can break your code if the latest release
of a package changes features your code relies on.

You can **pin** your project's package versions so ``pip`` only
uses the exact version you tell it. This is called **pinning** a
package.

.. _usage_library_why_pin:

Why Pin Packages?
^^^^^^^^^^^^^^^^^

Before version 1.0, projects often change unexpectedly. |project_name|
is no exception! Once it reaches 1.0, it will follow
`semantic versioning <semver>`_. Until then:

* Large changes may release without warning
* When that happens, projects without pinned package versions
  may break!



.. _usage_library_how_pin:

How do I Pin?
-------------

.. _requirements_txt: https://pip.pypa.io/en/latest/user_guide/#requirements-files
.. _Rye: https://rye-up.com/
.. _Poetry: https://python-poetry.org/


If you're using a tool like `Rye`_ or `Poetry`_, consult their
documentation. Otherwise, the following steps may help:

1. Find where you specify dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest and oldest way is a ``requirements.txt`` file with
one package per line.

However, many projects now use a ``pyproject.toml`` file instead.
If you aren't using a tool which generates it for you, then you
can edit it directly:

#. Open ``pyproject.toml``
#. Search for a ``[project]]`` heading
#. Look for a ``dependencies``  variable under it which looks like this

   .. code-block:: toml

      [project]
      dependencies = [
        'example_package_name == 1.0',
        'another_example_name == 1.1'
      ]


2. Choose Your Version
^^^^^^^^^^^^^^^^^^^^^^

.. _pypi_history: https://pypi.org/project/fontknife/#history

Safe & Stable
"""""""""""""

The current latest version is specified by this string:

   .. parsed-literal::

             |dependency_pypi_line|

You can choose from other versions on PyPI by checking the
`Release history tab <pypi_history>`_.


Advanced: Straight from GitHub
""""""""""""""""""""""""""""""

.. warning:: These versions **will** be buggy!

             Even if builds pass tests, this is a pre-release WIP unless it's
             a release commit. Things **will break!**

Very adventurous users can install directly from the latest commit
at the time of build by using the following:

   .. parsed-literal::

            |dependency_zipball_line|


3. Add it to your dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   .. list-table::
      :header-rows: 1

      * - Where your dependencies are kept
        - Where to put it
        - Example

      * - `requirements.txt <requirements_txt_>`_

        - At the end of ``requirements.txt``

        - .. parsed-literal::

             |dependency_pypi_line|


      * - ``pyproject.toml``

        - Under ``[project]`` section in the ``dependencies`` list

        - .. parsed-literal::

            [project]
            dependencies =[
                'example_package_name == 1.0',
                'another_example_name == 1.1'
                |dependency_pypi_line|
            ]


Now ``pip install -Ie .`` or use your preferred project management tool
to install dependencies!
