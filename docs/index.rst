|project_name|
##############

.. ifconfig:: unstable_branch is not None

   .. warning:: This doc is a preview of the unstable |branch_github_link|!

                If you need a safer doc version, please check the
                :docbuildfor:`stable`. If you're feeling very
                adventurous, you can proceed with caution. Just be aware
                things may change unexpectedly!


Remember that weird font?
*************************

.. raw:: html

   <style>
   .nearest-neighbor {
      -ms-interpolation-mode: nearest-neighbor;
      image-rendering: pixelated;
   }
   </style>


.. _home_sprite_sheet:

Make it a sprite sheet!
-----------------------

``fontknife convert tom-thumb.bdf sheet.png``


.. figure:: ./tom-thumb.png
   :class: nearest-neighbor
   :width: 200
   :height: 200
   :alt: The contents of tom-thumb.bdf converted to a sprites sheet

   *(Shown at 200% size)*


.. _home_filler_assets:

Make Filler Assets!
-------------------

``fontknife convert -P 48 -G "💪😎" NotoEmoji-Regular.ttf sheet.png``

.. figure:: ./flex_cool.png
   :alt: The cool sunglasses and flexed bicep emoji as a png


Contents
********

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :glob:

   install/index
   usage/index

.. this is a comment, and it wraps everything below
   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

