.. _library-install-choosing_dependency-approach:

Choosing a Dependency Approach
------------------------------

.. _TOML: https://toml.io/en/
.. _The pyproject.toml specification: https://packaging.python.org/en/latest/specifications/pyproject-toml/

It's okay if you haven't chosen a dependency management approach yet.

This page will help you choose one.

A Text File: the Simplest Option
""""""""""""""""""""""""""""""""

.. tip:: Pick this if the other sections seem overwhelming

To start using a ``requirements.txt`` to manage dependencies:

#. Go to your project's top-level folder
#. Save an empty file to it with the name ``requirements.txt``
#. Copy-and-paste a line from
   :ref:`library-install-requirements.txt`

If everything works after ``pip install -r requirements.txt``, then add
the new file to any version control you're using. That's it. You're
done!

You can always upgrade to another approach if you end up needing
more features.


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

* The Python Packaging User Guide's doc on `guide to writing a pyproject.toml`_
* The Python Packaging Authority's `sample project`_
* The `tomli <https://github.com/hukkin/tomli>`_ library
* `The pyproject.toml specification`_
* `The TOML specification <TOML>`_

.. tip:: If you like examples, skip to the `sample project`_ !

         Its ``pyproject.toml`` is very thoroughly commented!


I Want Only The Hippest Tools
"""""""""""""""""""""""""""""

For the latest in heavy-duty automation, check out one of the following:

* `Poetry`_
* `Rye`_

Remember, they aren't covered by the |project_name| doc. You'll have to
consult their documentation on how to manage dependencies instead.
