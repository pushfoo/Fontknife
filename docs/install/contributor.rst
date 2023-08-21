
.. _install_contributor:

Contributor Install Instructions
================================

These instructions are for readers who want to improve ``fontknife`` by

#. Fixing bugs
#. Adding new features
#. Testing or reviewing the above

See :ref:`install_user` if you only want to convert files.


.. _install_contributor_requirements:

Requirements
------------

First, make sure you have the following:

#. A GitHub account
#. |min_python_version_plus|
#. At least 5 MB of disk space to install dependencies


.. _install_contributor_instructions_venv:


Install Instructions
--------------------

.. _how_to_fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo?tool=webui#forking-a-repository
.. _how_to_clone_fork: https://docs.github.com/en/get-started/quickstart/fork-a-repo?tool=webui#cloning-your-forked-repository
.. _creating_venvs: https://docs.python.org/3/library/venv.html#creating-virtual-environments
.. _how_venvs_work: https://docs.python.org/3/library/venv.html#how-venvs-work

#. `Fork the fontknife repo on GitHub <how_to_fork_>`_
#. `Clone your fork <how_to_clone_fork_>`_
#. ``cd fontknife`` to enter the directory
#. `Create a virtual environment <creating_venvs_>`_
#. `Activate the virtual environment <how_venvs_work_>`_
#. Run ``pip install fontknife -e .[dev]`` to install the project and dependencies in editable mode.
#. Run ``fontknife convert --help`` to make sure it runs.
#. Run ``pytest`` to run all unit tests.