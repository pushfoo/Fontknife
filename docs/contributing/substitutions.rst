..
    WARNING: Line numbers might not match the output!

    This is because Jinja templates part of it:

    1. This help keeps conf.py cleaner
    2. It's nicer than the alternatives considered so far

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

**TL;DR: These are mini-templates Sphinx fills in for you**


.. # This definition is local to this page per the global
.. # vs local section covered further down in this file.

.. |example_rule| replace:: "Actual Value Here"


Each ``|rule_name|`` gets replaced with the value after ``replace::``.
For example, let's consider this rule:

.. code-block:: rst

   .. |example_rule| replace:: "Actual Value Here"

It looks like this when used:

|example_rule|


.. note:: This substitution is unique in |project_name|'s doc.

          This one is the only
          :ref:`local <contributing-substitutions-local_vs_global>`
          substitution.


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

.. _contributing-substitutions-local_vs_global:

The Local, the Global, and the Ugly
"""""""""""""""""""""""""""""""""""

Substitutions exist in the same spaces as other Sphinx reST objects.

**Local Substitutions**

You can define local substitutions limited to a specific file.

The example at the :ref:`top of this page <contributing-substitutions>`
is one of these. Like all local substitutions, it:

* can only be used in the ``.rst`` file they're defined in
* was carefully considered to avoid conflicts with other substitution
  rules

**Global Substitutions**

|project_name|'s other substitutions are available in every ``.rst``
file.

For the moment, the details of how that happens aren't important. You
can think of it as copying and pasting before the source code of every
``.rst`` file, both hand-written and generated API doc.

**The Ugly Part: Conflicts**

You can define a substitution rule **once and only once!**

Trying to redefine one anyway causes a build error which looks
like the one below:

.. code-block:: console

   /home/user/Projects/Fontknife/docs/install/substitutions.rst:10: WARNING: Duplicate explicit target name: "intro".


This applies:

* Per file
* Globally
* Any combination of the two


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


Now you need to make sure the doc works. Do so by building it locally:

#. Switch to your terminal
#. Make sure you're in the ``docs`` directory
#. Follow the guide to :ref:`contributing-testing-building_docs`

Fixing Whitespace Problems
""""""""""""""""""""""""""

**TL;DR: Sphinx is even pickier about whitepsace than Python!**

Did ``make html`` log a cryptic error like the one below?

.. code-block:: console

   /home/user/Projects/Fontknife/docs/contributing/substitutions.rst:184: WARNING: Definition list ends without a blank line; unexpected unindent.

This often happens when you've accidentally added whitespace. The most
common places are also some of the most frustrating ones:

* Lines which look blank
* At the ends of certain non-blank lines

Others can be wherever you've accidentally pasted it due to mouse or keyboard
hotkey accidents.

There may be future git configuration tricks which may fix it automatically.
For the moment, see if your editor has a way to enable whitespace visualization.

If not, the following steps may help:

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

.. warning:: These details may change in the near future.

The project's `conf.py`_ has a custom ``substitution_rules``
variable containing all our rules.

Sphinx doesn't use it directly. Instead, we use it to help set one of
its configuration variables. The current approach is inelegant, but it
gets the job done. Continue reading to learn more.

Generating a Prolog
"""""""""""""""""""

#. Our `conf.py`_'s ``substitution_rules`` is templated from various
   data sources:

   * `pyproject.toml`
   * git's HEAD
   * a few API calls

#. We build a number of other values
#. We :py:func:`~str.join` them together to set a final
   value for Sphinx's `rst_prolog`_ configuration variable

How Sphinx Uses It
""""""""""""""""""

As Sphinx loads each ``.rst`` file into memory, it:

#. Allocates a buffer to read source into
#. Writes the `rst_prolog`_ into the buffer
#. Copies the file's raw contents into the buffer
#. Applies any plugin transformations bound to the `source-read`_ event
#. Continues to the next file

Once it has processed all files to build its index, it then generates final
HTML from the full data. Note that it caches these unless you run ``make clean``.
