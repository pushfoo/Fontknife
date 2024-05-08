.. _install_requirements:

Install Requirements
====================

.. _dep_python: https://python.org/

1. |min_python_version_plus|
----------------------------


Checking Your Python Version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To check if you have a high enough version of Python:

#. Open your favorite terminal application.
#. Try running ``python``
#. If it says the command was not found, try the following:

   #. ``python3``
   #. |min_py_cli_command| or later minor version numbers

At least one of them should show something like the output below:

   .. code-block:: console

      Python 3.9.2 (default, Feb 28 2021, 17:03:44)
      [GCC 10.2.1 20210110] on linux
      Type "help", "copyright", "credits" or "license" for more information.
      >>>

If it doesn't, the see :ref:`install_requirements_python` section below.

If it does, then:

#. type ``exit()``
#. press enter
#. skip to :ref:`install_user_instructions_venv`


.. _install_requirements_python:

Installing Python
^^^^^^^^^^^^^^^^^

.. _install_guide_fedora: https://developer.fedoraproject.org/tech/languages/python/python-installation.html

Windows & Mac
"""""""""""""

On these platforms, it's best to install Python from the official
download pages:

* https://www.python.org/downloads/windows/
* https://www.python.org/downloads/macos/

Linux
"""""

.. _Linux Mint: https://linuxmint.com/
.. _flavors: https://linuxmint-installation-guide.readthedocs.io/en/latest/choose.html
.. _Pop!_OS: https://pop.system76.com/
.. _Pop!_Shop: https://support.system76.com/articles/pop-basics/#pop_shop-app-installation
.. _Ubuntu: https://ubuntu.com/
.. _Debian: https://www.debian.org/
.. _Fedora: https://fedoraproject.org/

Your distro's package manager is usually the best place to look.

.. list-table::  Distros by Approximate Beginner Friendliness
   :header-rows: 0

   * - Distro
     - Best Approach

   * - `Linux Mint`_ (All `flavors`_)
     - ``sudo apt install python3``

   * - `Pop!_OS`_
     - ``sudo apt install python3`` or via the `Pop!_Shop`_

   * - `Fedora`_
     - See `Fedora's Python guide <install_guide_fedora_>`_

   * - `Debian`_
     -  ``sudo apt install python3``

   * - `Ubuntu`_
     - ``sudo apt install python3``

.. _snap_scamware: wallet scam ahttps://arstechnica.com/information-technology/2024/03/ubuntu-will-manually-review-snap-store-after-crypto-wallet-scams/

.. note:: Ubuntu is at the bottom its Snap format has had
          multiple serious issues.

          These include:

          #. Shipping ``.deb`` packages which instead install
             Snap versions
          #. `Marking scam malware as "safe" <snap_scamware>`_
          #. Performance issues compared to ``.deb``


If you don't have |min_python_version| or higher in your distro's
package manager, see :ref:`linux-alt-python`.


.. _install_requirements_venv:

2. Active Virtual Environment
-----------------------------

.. _protect_system:
.. _creating_venvs: https://docs.python.org/3/library/venv.html#creating-virtual-environments
.. _how_venvs_work: https://docs.python.org/3/library/venv.html#how-venvs-work
.. _pipx: https://pipx.pypa.io/stable/

Python's virtual environments (venvs for short) protect your projects
from breaking each other. On operating systems such as Linux, they also
help protect your system Python version.

In most cases, you'll want to do the following:

1. Create a Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you aren't using PyCharm or VSCode, you can create a venv
from the terminal with:

.. code-block:: console

   python -m venv .venv

.. Although this has an entry in the .inv file per the output of
.. inspecting the .inv file, the emdash or something else breaks
.. intersphinx links to it. For now, we'll use a simple direct link.
.. _Creating virtual environments: https://docs.python.org/3/library/venv.html#creating-virtual-environments

This will create a venv named ``.venv`` in the current directory. To
learn more, please see Python's `Creating virtual environments`_.


.. _reqs_activated:

2. Make Sure Your Venv Is Activated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The way you activate a virtual environment varies with your:

* operating system
* development tools

With PyCharm and other heavyweight development environments, your venv
will usually be automatically activated in the terminal windows of the
tool.

If you're using lighter tools, you may need to activate the venv manually
through the terminal. The table of examples below assumes you created a
venv as in the last section:

* In the root directory of your project
* Named ``.venv``

.. list-table::
   :header-rows: 1

   * - OS
     - Example Command

   * - Windows (CMD)
     - ``.venv\bin\activate.bat``

   * - Windows (PowerShell)
     - ``PS .venv\bin\activate.bat``

   * - Mac, Linux, and BSDs
     - ``source .venv/bin/activate``


To learn more, please see Python's :external+python:ref:`venv-explanation`.


Account-Wide Usage Via pipx
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you only need to use |project_name| as a utility instead of an
imported Python module, you can use `pipx`_. It allows running any'
python package which provides runnable named scripts across your entire
user account. It works by creating package-specific virtual environments,
then performing some routing work.

After installing it, you can use `pipx` instead of `pip` when following
install instructions.

.. toctree::
   :hidden:

   linux_alt_python

