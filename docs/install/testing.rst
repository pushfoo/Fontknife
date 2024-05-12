.. _install_user_instructions_test:

Testing Your Install
--------------------

These steps are recommended but not required. You can skip them if
you'd like.

Checking if it Runs
^^^^^^^^^^^^^^^^^^^
Run ``fontknife convert --help`` to see if help options print.

This lets you be reasonably sure |project_name| installed, but not
help options, you can be reasonably sure the install worked.

A Test Spritesheet
^^^^^^^^^^^^^^^^^^
.. _tom_thumb_dl_page: https://robey.lag.net/2010/01/23/tiny-monospace-font.html#back

#. Download ``tom-thumb.bdf`` from the bottom of
   `this page <tom_thumb_dl_page>`_
#. Run ``fontknife convert -p tom-thumb.bdf sheet.png``
#. The output file should be identical to the one below:

   .. figure:: ./../tom-thumb.png
      :alt: The image file which font knife should generate.
      :target: ../_images/tom_thumb.png

It's tiny (64 x 72 px) because the input data is a 3 x 5 pixel font.
