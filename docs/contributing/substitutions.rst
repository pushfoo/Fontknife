..
    WARNING: Line numbers might not match the output!

    This is because Jinja templates part of it:

    1. This help keeps conf.py cleaner
    2. It's niceer than the alternatives considered so far

    Alternatives considered and rejected include:

    * Trying to get processed substitution rules from Sphinx internals
      ( This will be very painful and waste time )
    * Defining custom OOP abstractions to preprocess ourselves
      ( Duplicates effort )
    * Code golf problems like turning substitution rules into quines
      ( Jinja has the same result with far less pain )

.. _contributing-substitutions:

Substitutions for Doc
=====================

**TL;DR: We have mini-templates Sphinx fills in for you**


.. |example_rule| replace:: "Actual Value Here"

Each ``|rule_name|`` gets replaced with the value after ``replace::``.
For example, let's consdier this rule:

.. code-block:: rst

   .. |example_rule| replace:: "Actual Value Here"

It looks like this when used: |example_rule|.

Why Substitutions?
------------------

.. _conf.py: https://github.com/pushfoo/Fontknife/blob/main/docs/conf.py

**TL;DR: They save time & effort by single-sourcing values.**

For example, we never have to hunt for outdated minimum Python versions
in our doc. Each time our doc builds, our `conf.py`_ will:

#. Read ``pyproject.toml``
#. Parse and compute any necessary values
#. Generate final substitution rules, including:

   * Minimum Python version strings
   * Source install links
   * Branch links

Our Substitutions
-----------------

.. _contributing-substitutions-current:

Our Current Substitutions
^^^^^^^^^^^^^^^^^^^^^^^^^

The only local substitution in the project is one in this file.

The substitutions rules in the source below are **global**. You can use
them anywhere and everywhere in the project's reST source. That includes
docstrings in addition to ``.rst`` files, but it might not always be a
good idea.

.. tip:: Be sure to read the comment at the top!

.. # The curly braces below are Jinja2 templating.

.. code-block:: rst

   {% filter indent(width=3) %}
   {{ substitution_rules }}
   {% endfilter %}


Adding New Substitutions
^^^^^^^^^^^^^^^^^^^^^^^^

#. Do you meet the
   :ref:`contributing prerequisites <contributing-requirements>`?
#. Do you have a :ref:`editable install <contributing-editable_install>`
#. Have you :ref:`tested it <contributing-testing-tests_and_docs>`?
#. Does the project really need the substitution?

   Signs something should be a substitution include:

   * It can be derived from project config or git metadata
   * It's something which is easy to forget to update
   * It's used in multiple places, especially on multiple pages

If you can answer yes to all of the above, you have a new question to
answer: global or local?

The Local, the Global, and the Ugly
"""""""""""""""""""""""""""""""""""

Substitutions exist in the same spaces as other Sphinx reST objects.

**Local Substitutions**

You can define local substitutions in a specific file. The example
at the :ref:`top of this page <contributing-substitutions>` is also an
example of a local substitution rule. Like all local substitutions:

* Can only be used in the ``.rst`` file they're defined in
* Was carefully considered to avoid conflicts with other substitution
  rules

**Global Substitutions**

|project_name|'s other substitutions are available in every ``.rst``
file. This is because they're added to a special config value called
the **rst_prolog**. It gets added before the contents of every ``.rst``
file in the project.

**The Ugly Part: Conflicts**

You can only define a substitution rule **once per given context!** This
can include:

* Per file
* Globally
* Any combination of the two

Trying to redefine one anyway will cause a build error like the one below:

.. code-block:: console

   /home/user/Projects/Fontknife/docs/install/substitutions.rst:10: WARNING: Duplicate explicit target name: "intro".


Adding a Global Substitution Rule
"""""""""""""""""""""""""""""""""

.. warning:: Substitution rules can only be defined
             **once per context**!

             Trying anyway will cause a build error. See the previous
             heading to learn more.

To add a global substitution rule:

#. Open `docs/conf.py <conf.py>`_ in the
#. Find the ``substitution_rules \=`` variable followed by the definition
   block :external+python:ref:`f-string <f-strings>`
#. Add the following:

   #. The new rule itself
   #. Any necessary comments and spacing


Now you need to build your doc locally to make sure it works:

#. Switch to your terminal
#. Make sure you're in the ``docs`` directory
#. Follow the guide to :ref:`contributing-testing-building_docs`

Fixing Whitespace Problems
""""""""""""""""""""""""""

Did ``make html`` log a cryptic error like the one below?

.. code-block:: console

   /home/user/Projects/Fontknife/docs/contributing/substitutions.rst:184: WARNING: Definition list ends without a blank line; unexpected unindent.

**TL;DR: Sphinx is even pickier about whitepsace than Python!**

You can often trigger this error by accidentally leaving extra on:

* Otherwise blank lines
* At the ends of certain non-blank lines
* Accidentally pasting non-whitespace text where Sphinx expected whitespace

There's may be a git trick to fix it automatically. In the meantime, the following
steps often help:

#. run ``git diff``

   * You can start with just ``git diff conf.py``
   * It's worth checking other files too

#. Look for blank lines which:

   #. Starting with a green +
   #. Have nothing but blank redness after

#. Delete all the added whitespace that redness represents

After you eliminate it, try running ``make html`` again.

How Doc Build Works Behind the Scenes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _rst_prolog: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-rst_prolog
.. _Sphinx's conf.py documentation: https://www.sphinx-doc.org/en/master/usage/configuration.html
.. _jinja_my_rst: https://github.com/pushfoo/Fontknife/blob/main/docs/_extensions/jinja_my_rst.py
.. _source-read: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events

The project's `conf.py`_ contains a custom ``substitution_rules``
variable with all our rules. Moving it to a new file without making
templating a headache is on the to-do list, but for now:

#. The `conf.py`_'s ``substitution_rules`` variable contains all our
   substitution rule definitions
#. It's used as the the first part of the `rst_prolog`_ configuration variable
#. As Sphinx loads each ``.rst`` file into memory, it:

   #. Copies the `rst_prolog`_ into the page
   #. Copes the file's raw contents in after the `rst_prolog`_ data
   #. Applies any plugin transformations triggered by the `source-read`_
      event.
