|project_name|
##############


.. raw:: html

   <style>
   .nearest-neighbor {
      -ms-interpolation-mode: nearest-neighbor;
      image-rendering: pixelated;
   }
   </style>


.. rubric:: TL;DR: Rasterize & export only the :term:`glyphs <glyph>` you need

You can make sprite sheets of entire fonts:

#. ``fontknife convert tom-thumb.bdf sheet.png``
#. Use the resulting image file:

   .. figure:: ./tom-thumb.png
      :class: nearest-neighbor
      :width: 200
      :height: 200
      :alt: The contents of tom-thumb.bdf converted to a sprites sheet

      *(Shown at 200% size)*

Only need some of the glyphs? Sure:

#. ``fontknife convert -P 48 -G "💪😎" NotoEmoji-Regular.ttf sheet.png``
#. Use the sheet in your project:

   .. figure:: ./flex_cool.png
      :alt: The cool sunglasses and flexed bicep emoji as a png

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   install/requirements
   install/user
   install/library
   install/testing

.. toctree::
   :maxdepth: 3
   :caption: Usage Guide

   usage/command_line
   filler_assets/index
   font_kinds/index

.. toctree::
   :maxdepth: 1
   :caption: Theory

   text_rendering_is_really_hard
   glossary

.. toctree::
   :maxdepth: 1
   :caption: Contributing

   contributing/setup
   contributing/testing
   contributing/substitutions
