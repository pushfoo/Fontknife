.. _user-install:

User Install
============

These instructions for command line usage, such as making sprite sheets
or filler assets from fonts.

For other purposes, you should see the following:

.. list-table::
   :header-rows: 1

   * - |if_need_to|
     - |may_want|

   * - ``import fontknife`` in Python code
     - |redir_library|

   * - Contribute fixes or new features
     - |redir_contributing|


Check your Requirements
-----------------------

|project_name|'s Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Make sure you're in an active virtual environment with
|min_py_fullname| or higher. To learn how, see :ref:`install_requirements`.


.. _install-instructions-user-your_needs:

Your Needs
^^^^^^^^^^
Pick from the table below:

.. list-table::
   :header-rows: 1

   * - If you need...
     - ...you may want:

   * - Safer Code & Finished Documentation
     - :ref:`install-user-stable_pypi`

   * - The Latest Features
     - :ref:`install-user-buggy_source`


.. _install-user-stable_pypi:

Planned Releases via PyPI
-------------------------

The easiest option is to install the latest stable |project_name|
release via ``pip``. This has the following advantages:

#. The most stable features available
#. Corresponding doc builds

Installing
^^^^^^^^^^

Fresh Install
"""""""""""""

To install |project_name|, run the following commands:

.. parsed-literal::

   pip install |package_name|

Upgrading to the Latest Stable Release
""""""""""""""""""""""""""""""""""""""

.. parsed-literal::

   pip install |package_name| --upgrade

You can also use the following syntax:

.. parsed-literal::

   pip install |package_name| -U



.. _install-user-buggy_source:

The Newest & Buggiest Source
----------------------------

To live dangerously, you can install the current ``main`` branch
directly from GitHub:

.. parsed-literal::

   pip install |cli_pip_install_gh_branch_main|

The unstable :docbuildfor:`main` is rebuilt automatically each time a
commit is pushed to the branch.

.. ifconfig:: not unstable_branch

   .. warning:: You are currently viewing the stable :docbuildfor:`stable`.

                Please see the unstable :docbuildfor:`main` if you intend
                to install from branch source.

You can also specify a commit hash instead of a branch if you want to
install a specific commit. For example, the command below will install
the commit this doc was built from:

.. parsed-literal::

   pip install |cli_pip_install_gh_commit_curr|

.. warning:: There are no doc builds for specific commits!

             You'll be on your own, although you could try to build
             doc locally.

If you're getting into specifics like this, you may want to see


#. Add a ``requirements.txt`` somewhere
#. See :ref:`library-install-requirements.txt`

GitHub Archives Aren't Deterministic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _stability of source code archives: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives#stability-of-source-code-archives

GitHub's compression settings and hashes for archive links can change.

If you don't know what this means, you can probably skip this section.
Otherwise, you may want to see the following:

* The :ref:`library-install` instructions instead
* GitHub's explanation of the
  `stability of source code archives`_
