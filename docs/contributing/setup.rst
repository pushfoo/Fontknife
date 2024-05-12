
.. _contributing-setup:

Contributor Setup
=================

These instructions hlep you improve |project_name| by writing code or
documentation This includes:

#. Fixing bugs and typos
#. Adding new features and information
#. Testing or reviewing any of the above

.. list-table::
   :header-rows: 1

   * - |if_need_to|
     - |may_want|

   * - Convert font data in the terminal
     - |redir_to_use|

   * - ``import fontknife`` in Python code
     - |redir_library|


.. _contributing-requirements:

Requirements
------------

Basic Pre-Reqs
^^^^^^^^^^^^^^
First, make sure you have the following:

#. |min_py_fullname_plus| installed
#. A GitHub account

.. _contributing-fork_and_clone:

Making Sure to Fork & Clone the Repo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _how_to_fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo?tool=webui#forking-a-repository
.. _how_to_clone_fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo?tool=webui#cloning-your-forked-repository

Now you need to make your own copes of the repo to work from.

First, make sure you're logged into GitHub. Then:

#. Create a copy of the |project_name| repo on GitHub by
   `forking it into your account <how_to_fork_>`_
#. Get your fork's code onto your computer by
   `cloning your fork <how_to_clone_fork_>`_

.. _contributing-editable_install:

Editable Install
----------------

.. _creating_venvs: https://docs.python.org/3/library/venv.html#creating-virtual-environments
.. _how_venvs_work: https://docs.python.org/3/library/venv.html#how-venvs-work

After you've forked and cloned the repo, you'll want to make set up
your local environment.

Note that |project_name| does not currently use a tool which heavily
automates the development environment (`Poetry`_, etc). This means
you may have to take a more hands-on approach than you're used to.

Otherwise, the steps will be the same as for most projects:

#. Open a terminal window
#. ``cd fontknife`` to enter the directory
#. `Create a virtual environment <creating_venvs_>`_
#. `Activate the virtual environment <how_venvs_work_>`_
#. Run ``pip install fontknife -e .[dev,docs]`` to install the project
   and its dependencies in editable mode.

Once you're done, remember to take a break. Once you're ready,
you'll want to try :ref:`contributing-testing-tests_and_docs`.


