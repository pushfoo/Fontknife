.. _library-install-choosing_dependency-approach:

Help! What's Dependency Management?!
------------------------------------

.. _TOML: https://toml.io/en/
.. _writing_toml: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
.. _pypa_sampleproject: https://github.com/pypa/sampleproject/blob/main/pyproject.toml
.. _The pyproject.toml specification: https://packaging.python.org/en/latest/specifications/pyproject-toml/

It's okay if you haven't chosen a dependency management approach yet.

This page will help you get started by going from simplest to most
complicated. Skim the page, then pick whatever option appeals to you.

A Text File: the Simplest Option
""""""""""""""""""""""""""""""""

If you feel intimidated or overwhelmed, remember that even a simple
``requirements.txt`` is better than nothing!

The TOML: Power Without Too Much Magic
""""""""""""""""""""""""""""""""""""""

Do you want...

* something just a bit fancier?
* without too much magic or complex automation?

The TOML route is a solid choice. Although it's more complicated than
``requirements.txt``, the added features make better for most projects.

The TOML configuration language:

* Will be familiar if you've ever seen an :wikipedia:`INI file <INI_file>`
* Loads neatly into a Python :py:class:`dict`
* Tends to be far easier to read than :py:mod:`JSON <json>`

To learn more, please see:

* The Python Packaging User Guide's doc on
  `writing your pyproject.toml <writing_toml>`_
* `The Python Packaging Authority's Sample Project <pypa_sampleproject>`_
* The `tomli <https://github.com/hukkin/tomli>`_ library
* `The pyproject.toml specification`_
* `The TOML specification <TOML>`_

.. tip:: If you like examples, skip to the
         `sample project <pypa_sampleproject>`_!

         Its ``pyproject.toml`` is very thoroughly commented!


I Want Only The Hippest Tools
"""""""""""""""""""""""""""""

For the latest in heavy-duty automation, check out one of the following:

* `Poetry`_
* `Rye`_

Remember, they aren't covered by the |project_name| doc. You'll have to
consult their documentation on how to manage dependencies instead.
