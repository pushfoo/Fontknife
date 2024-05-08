.. _font_kinds:

Kinds of Font
*************

.. this is a duplicate of the table below

.. toctree::
   :hidden:

   symbol_fonts
   custom_code_point_ranges

This chapter covers major relevant ways to classify fonts.

Hold On, Why The Funny Chapter Name?
====================================

.. _gfonts_intro_type: https://fonts.google.com/knowledge/introducing_type

The word "type" can mean at least five different things depending on the context:

* The idea of
  `digital type (link to Google Fonts) <gfonts_intro_type>`_
  and related stylistic choices
* A specific :gfonts-gloss:`typeface`
* A Python :py:class:`type`
* The act of typing on a device or computer
* Pre-digital :wikipedia:`movable type (link to Wikipedia) <Movable_type>`

Font Kinds: Overview
====================

.. rubric:: 0. License

TL;DR: Ideally, you want the OFL or Public Domain (CC0).

The OFL and Public Domain have the least complications.

.. rubric:: 1. Symbol Fonts vs Everything Else

* For text sprite sheets, you usually want a regular text font
* For filler graphics, :ref:`font_kinds-symbol_fonts` are best:

  * :ref:`Dingbat fonts <font_kinds-dingbat_fonts>` and
    :ref`Emoji fonts` are best
  * :ref:`Math fonts` and `Music fonts` can be good too

.. rubric:: 2. File Formats

* :term:`bitmap` formats (spritesheets, :term:`BDF`, :term:`PCF`, etc)
* :term:`vector` formats

 * Mostly :term:`TTF` and :term:`OTF`
 * If you know about the others, you might be a wizard who doesn't
   need this tool

.. rubric:: 3. The Code Points Covered

* Many encodings things have dedicated or de-facto
  :ref:`font_kinds-custom_code_pages`.
* Traditionally, :ref:`Dingbat fonts <font_kinds-dingbat_fonts>`
  don't care:

  * They often hijack :term:`code points <code point>` usually
    meant for other :term:`characters <character>`
  * This makes it easier to type their :term:`glyphs <glyph>`

.. rubric:: 4. Styles

Fonts can come in different weight and style variants if they aren't
cutting edge variable fonts. Some also have built-in color, a feature
which |project_name| doesn't support yet.

.. tip:: For low-res use, you're usually better off with a pixel
         font in a :term:`bitmap` format sucvh as:

         * :term:`BDF`
         * :term:`PCF`
         * A sprite sheet
