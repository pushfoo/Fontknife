.. _linux-alt-python:

Non-Standard Python on Linux
============================

.. _DontBreakDebian: https://wiki.debian.org/DontBreakDebian

Under Linux, some distros or versions don't have the Python version you
need in their package repositories.

You have two options in this case:

.. list-table::
   :header-rows: 1

   * - Option
     - TL;DR

   * - 3rd party repos (PPAs, etc)
     - Can be okay on Ubuntu, but they can also
       `break things <DontBreakDebian>`_

   * - Building from source
     - Safe if you **only** use the ``altinstall`` option


Alternate Package Sources
-------------------------

.. _PPA_StackOverflow: https://askubuntu.com/a/35636
.. _deadsnakes PPA: https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa

On ``.deb``-based distros,
`Personal Package Archives (PPAs) <PPA_StackOverflow>`_ are 3rd-party
package repos which can provide software not found in the base repos.

PPAs are known to cause enough issues for Debian's official
`DontBreakDebian` page to warn against using them. Despite this, Ubuntu
users sometimes use the `deadsnakes PPA`_ to get Python versions not offered
in the distro's repos. The name is a pun on Python:

* "dead" refers to outdated versions
* "snakes" refers to Python


Building Python From Source
---------------------------

.. warning:: **Only** use ``make altinstall`` for this!

             The top way to break many Linux distros is replacing or
             altering the system Python version!

It's possible to use the compile and install a specific Python version
alongside a system Python version. This is may seem intimidating, but
it's easier than it sounds.

.. _Install Python's build dependencies: https://devguide.python.org/getting-started/setup-building/#install-dependencies

Check Out the Repo and Version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try running ``git`` from the command line. If it tells you the command
isn't found, you can usually install it via your distro's package
manager.

Once you have git working, open your terminal. We'll check out the repo
for cpython, Python's official interpreter.

#. Open a terminal window
#. ``cd`` into a directory you'd like to check out to
#. ``git clone git@github.com:python/cpython.git``
#. ``cd cpython``


Check out a Version Tag
^^^^^^^^^^^^^^^^^^^^^^^

For the cpython repo, tags take one of two forms:

.. list-table::
   :header-rows: 1

   * - Tag type
     - Example

   * - ``vMajor.Minor.Point``
       per `semantic versioning <https://semver.org/>`_

     - |min_py_git_tag_v|

   * - Latest point release of a minor version
     - |min_py_git_tag_latest|


If you're comfortable with the terminal,  you can browse a full list of
tags by running ``git tag -l``. If you prefer the GUI, you can browse
tags by following the steps below:

#. Go to the cpython GitHub repo at https://github.com/python/cpython
#. Click the ``main`` box near the top left of the screen beneath **cpython**
#. Click the **tags** tab
#. Scroll or type into the search box

Once you've selected a tag, use ``git checkout`` to switch to it. For
example, |min_py_git_tag_latest_example|.

Building Python
^^^^^^^^^^^^^^^

First, `Install Python's build dependencies`_. The details will vary
since package managers and package names vary between Linux distros.

Then, you'll want to:

#. ``make regen-configure``
#. Use ``make`` to build

Controlling Resource Usage
""""""""""""""""""""""""""

Running ``make`` alone may hog your RAM and CPU.

The ``-j`` option specifies how many threads to use when compiling.
However, the number of cores isn't the only factor affecting how many
threads can actively run at once. :wikipedia:`Hyper-threading` is a CPU
feature which effectively doubles the number of threads which can run at
once. For example, on a CPU with 4 cores and hyper-threading enabled,
you can have 8 active threads.

To check whether you have hyperthreading enabled, run the following:

.. code-block:: console

   cat /sys/devices/system/cpu/smt/active

If it shows the following output, hyper-threading is enabled:

.. code-block:: console

   e
   1

On a CPU like the one described above, you might want to compile
in the background while you work on other tasks. Running
``make -j 6`` will:

* run build on 6 threads
* leave breathing room as Python builds in the background

You can use a lower ``-j`` to tax your system if you'd like, but
the build will take longer.



Running & Testing an Alt-Install
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: **Only use altinstall!**

             Otherwise, you may break your Linux install.

Once you've compiled Python, you can use ``make test`` to test it. This
may take a while, so you can skip it if you're impatient.


Run ``sudo make altinstall`` to set up your Python version alongside your
system version.

Once it finishes, try running it. For example, if you built tag
|min_py_git_tag_latest|, try running |min_py_cli_command|.

You should see a Python prompt which looks something like this:

.. code-block:: console

   Python 3.8.19+ (remotes/origin/3.8:f5bd65ed37, Apr  9 2024, 23:37:52)
   [GCC 10.2.1 20210110] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>>
