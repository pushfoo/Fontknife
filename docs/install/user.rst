
.. _install_user:

User Install Instructions
=========================


Overview
--------

These instructions are for people who want to use ``fontknife`` without
changing it. Examples include:

#. Converting assets for a specific Python-based project
#. Use ``fontknife`` as a dependency for one of your projects
#. Try fontknife without installing it for your computer's user
   account

See :ref:`install_contributor` if you'd like to contribute bug fixes or
new features.


.. _install_user_requirements:

Requirements
------------

.. _dep_python: https://python.org/

First, make sure you have |min_python_version_plus| installed:

#. Open your favorite terminal application.
#. Try running ``python``. If it says the command was not found, try ``python3`` instead.
#. At least one of them should show something like the output below:

   .. code-block:: console

      Python 3.9.2 (default, Feb 28 2021, 17:03:44)
      [GCC 10.2.1 20210110] on linux
      Type "help", "copyright", "credits" or "license" for more information.
      >>>

#. If it doesn't, the see :ref:`install_user_python` section below.
#. Otherwise, type ``exit()``, press enter, and skip to
   :ref:`install_user_instructions_venv`.


.. _install_user_python:

Installing Python
-----------------

.. _install_guide_fedora: https://developer.fedoraproject.org/tech/languages/python/python-installation.html


.. list-table::
   :header-rows: 1

   * - Platform
     - Most reliable way to install Python

   * - Windows
     - `From Python's official Windows downloads page <https://www.python.org/downloads/windows/>`_

   * - macOS
     - `From Python's official macOS downloads page <https://www.python.org/downloads/macos/>`_

   * - Linux

     - Your distro's package manager:

       .. list-table::
          :header-rows: 0

          * - Pop!_OS
            - ``sudo apt-get install python3`` or via the Pop Shop

          * - Ubuntu
            - ``sudo apt-get install python3``


          * - Fedora
            - See `Fedora's Python guide <install_guide_fedora_>`_


.. _install_user_instructions_venv:

User Install Steps
------------------

.. _creating_venvs: https://docs.python.org/3/library/venv.html#creating-virtual-environments
.. _how_venvs_work: https://docs.python.org/3/library/venv.html#how-venvs-work
.. _tom_thumb_dl_page: https://robey.lag.net/2010/01/23/tiny-monospace-font.html#back


#. `Create a virtual environment <creating_venvs_>`_ if you haven't
#. `Make sure it's activated <how_venvs_work_>`_
#. ``pip install fontknife`` to install the latest version
#. ``fontknife convert --help`` to make sure it runs.



.. _install_user_instructions_test:

Testing Your Install
--------------------

If you want to make sure your install is working, use the following
steps:

#. Download the Tom Thumb BDF font from
   `the bottom of this page <tom_thumb_dl_page>`_.
#. Run ``fontknife convert -p tom-thumb.bdf sheet.png``
#. The resulting file should be identical to the one below:

   .. figure:: ./../tom-thumb.png
      :alt: The image file which font knife should generate.
      :target: ../_images/tom_thumb.png

   It's tiny (64 x 72 px) because the input data is a 3 x 5 pixel font.
