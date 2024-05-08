
.. _install_user:

User Install
============

These instructions for command line usage, such as making sprite sheets
or filler assets from fonts.

For other purposes, you should see the following:

.. list-table::
   :header-rows: 0

   * - ``import fontknife`` in Python code
     - :ref:`install_library`

   * - Contribute fixes or new features
     - :ref:`install_contributor`


Check your Requirements
-----------------------

First, make sure you an active virtual environment with
|min_python_version_plus|. To learn how, see
:ref:`install_requirements`.

.. _install_user_instructions_venv:

User Install Steps
------------------

Choose: Safety or Freshness?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can install in one of two ways:

* For more safety, install planned releases from PyPI
* To get fresh features at the price of bugs, you can install from GitHub


Planned Releases via PyPI
"""""""""""""""""""""""""

The easiest option is to install |project_name| from PyPI (Python Package
Index). It has the following advantages:

#. As much stability as pre-alpha software can have
#. Corresponding doc builds such as this one

To install this way, all you need to do is:

#. ``pip install fontknife`` to install the latest version
#. ``fontknife convert --help`` to make sure it runs.


Straight from the Buggy Source
""""""""""""""""""""""""""""""

.. tip:: If you're getting into specifics like this, you may want to:

         #. Add a ``requirements.txt`` somewhere
         #. Follow the :ref:`install_library` instructions instead

To live dangerously and get cutting-edge builds, you can install the
current ``main`` branch directly from GitHub:

.. parsed-literal::

   pip install |cli_pip_install_gh_branch_main|


To install another branch, replace ``main`` with that branch name. If
you install the ``main`` branch, please switch to the corresponding
unstable :docbuildfor:`main`.

You can also specify a commit hash instead of a branch if you want to
install a specific commit. For example, the command below will install
the commit this doc was built from:

.. parsed-literal::

   pip install |cli_pip_install_gh_commit_curr|

.. warning:: There are no doc builds for specific commits!

             You'll be on your own, although you could try to build
             doc locally.


.. _install_user_instructions_test:

Testing More Thoroughly
-----------------------

.. _tom_thumb_dl_page: https://robey.lag.net/2010/01/23/tiny-monospace-font.html#back

The following steps should make sure your install works correctly:

#. Download ``tom-thumb.bdf`` from the bottom of
   `this page <tom_thumb_dl_page>`_
#. Run ``fontknife convert -p tom-thumb.bdf sheet.png``
#. The resulting file should be identical to the one below:

   .. figure:: ./../tom-thumb.png
      :alt: The image file which font knife should generate.
      :target: ../_images/tom_thumb.png

It's tiny (64 x 72 px) because the input data is a 3 x 5 pixel font.
