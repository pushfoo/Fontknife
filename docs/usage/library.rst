
.. _usage_library:


Library Usage
=============

This page is for developers who want to use fontknife as part of a project.



TL;DR
"""""

.. _pin_versions: https://pip.pypa.io/en/stable/topics/repeatable-installs/

`Pin your fontknife version! <pin_versions_>`_


.. _usage_library_why_pin:

Why Pin?
""""""""

Your project won't break when something changes in fontknife. The
project isn't yet stable yet, so you should expect breaking changes.


.. _usage_library_how_pin:

How do I pin it?
""""""""""""""""

.. _requirements_txt: https://pip.pypa.io/en/latest/user_guide/#requirements-files

#. Find out where your package management tool keeps dependencies

#. Copy this text:

   .. parsed-literal::

             |dependency_line|

#. Use this table to find out if & where to paste t:

   .. list-table::
      :header-rows: 1

      * - Where your dependencies are kept
        - Where to put it
        - Example

      * - `requirements.txt <requirements_txt_>`_

        - At the end of ``requirements.txt``

        - .. parsed-literal::

             |dependency_line|


      * - ``pyproject.toml``

        - Under ``[project]`` section in the ``dependencies`` list

        - .. parsed-literal::

            [project]
            dependencies =[
                '|dependency_line|'
            ]


