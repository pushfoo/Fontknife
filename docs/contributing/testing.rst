.. _contributing-testing-tests_and_docs:

Testing the Code & Building Docs
================================

.. _contributing-testing-unit_tests:

Running the Unit Tests
----------------------

Run ``pytest`` to make sure:

* The dev depenencies were set up correctly
* The code isn't broken on your system / architecture

Running and writing these tests is also a key step for writing new
features or changing existing ones.

.. _contributing-testing-building_docs:

Building the Doc
----------------

These steps assume you're at the root of the repo.

#. ``cd docs`` to switch into the docs dir
#. ``make html`` to build the doc HTML
#. ``python -m http.server -d _build/html`` to launch a local web server
#. Open https://localhost:8000/ in your browser
#. You should have a version of the documentation browsable locally

To shut off the server, press ``Ctrl-C`` in the terminal.


Why the Warnings & Strange Version String?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are an intentional choice tp help contributors.

They make sure you don't forget which build you're looking at:

* Stable automated builds
* Unstable automated builds
* Local builds

The default stable ``latest`` build on readthedocs is the only one which
leaves out the warnings by default. For testing purposes, a way to tell
the doc build to "pretend" it's stable is outlined below.

Local & Unstable Doc Builds
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There will be a warning at the top of the pages on these builds.
On local builds, there will also be additional changes:

* The browser window will prefix values to the page's HTML title
* The version in the sidebar will be replaced by a string which
  looks like ``[LOCAL] main 46009791``

The version replacement string consists of:

* A local prefix
* The current git branch's name
* A shortened commit hash


Building as Stable
^^^^^^^^^^^^^^^^^^

You can fake a stable release build to test the stability detection.

Run ``./fake_stable.sh`` from the root of the ``docs`` directory. It
will:

#. Set environment variables readthedocs provides for build scripts
#. Use values which normally tell the the build script it's on the
   latest stable release