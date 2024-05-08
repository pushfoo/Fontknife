.. _font_kinds-symbol_fonts:

Symbol Fonts
============

.. _Wingdings: https://en.wikipedia.org/wiki/Wingdings
.. _Noto Emoji: https://fonts.google.com/noto/specimen/Noto+Emoji
.. _Noto_Sans_Math: https://fonts.google.com/noto/specimen/Noto+Sans+Math/glyphs
.. _Noto Music: https://fonts.google.com/noto/specimen/Noto+Music
.. _OFL: https://openfontlicense.org/


.. _def_glyph: https://fonts.google.com/knowledge/glossary/glyph

Regular fonts are generally made up of the following:

* The characters of at least one language's writing system
* Punctuation
* Numerals

For our purposes, a **symbol font** differs by providing an entirely
different set of glyphs as their primary focus. The table below
outlines categories relevant to |project_name| users looking to increase
iteration speed. Each category will be covered in greater depth further
down the page.

.. list-table::
   :header-rows: 1
   :widths: 25, 37, 37

   * - Quick Link
     - Glyphs Provided
     - How

   * - :ref:`font_kinds-dingbat_fonts`
     - :term:`Dingbats <dingbat>` (various symbols)
     - Often by hijacking :term:`code points <code point>`

   * - :ref:`Emoji Fonts`
     - Emoji
     - Mostly at proper :term:`code points <code point>`

   * - :ref:`Math fonts`
     - Math operators, arrows, etc
     - Mostly at proper :term:`code points <code point>`

   * - :ref:`Music fonts`
     - Notes and other glyphs
     - Mostly at proper :term:`code points <code point>`


.. _font_kinds-dingbat_fonts:

Dingbat Fonts
-------------

A :term:`dingbat font` provides :term:`dingbats <dingbat>` instead of
the usual :term:`glyphs <glyph>` for characters.

Since the :term:`Unicode` usually adds any widely useful or popular
symbols, today's :term:`dingbat fonts <dingbat font>` each tend to
serve a very specific purpose. They can be useful, decorative, or
both.

.. _symbol_fonts_dingbats_productivity:

Productive Dingbats
^^^^^^^^^^^^^^^^^^^

.. _Unicode 7.0's change log: https://www.unicode.org/versions/Unicode7.0.0/#Database_Changes
.. _Alan Wood's overview of Wingdings vs Unicode: https://www.alanwood.net/demos/wingdings.html

Microsoft's Wingdings Font Series are the some of the most
famous examples of :term:`dingbat` fonts.

However, the first of the Wingdings fonts is now obsolete. In addition
to overlapping with the earlier Zapf Dingbat typeface, the symbols of
both fonts were eventually included into the :term:`Unicode` standard.

To learn more, please see:

* `Alan Wood's overview of Wingdings vs Unicode`_ (Updated in 2018)
* `Unicode 7.0's change log`_ (2014)



.. _symbol_fonts_dingbats_decoration:

Decorative Dingbats
^^^^^^^^^^^^^^^^^^^

.. _Teranoptia: https://www.tunera.xyz/fonts/teranoptia/
.. _Tunera Type Foundry: https://www.tunera.xyz/

Some :term:`dingbat` fonts stick closer to the term's decorative
origins.

For example, `Teranoptia`_ is a font by `Tunera Type Foundry`_'s Ariel
Martin Perez. The font allows you to draw imaginary creatures with
standard :term:`ASCII` characters through custom :term:`glyphs <glyph>`:

.. list-table::
   :header-rows: 1

   * - :term:`Glyphs <glyph>`
     - Characters Replaced

   * - Monster body parts
     - Latin letter characters

   * - Left & right upward burrows
     - ``[``, ``]`` (Square brackets)

   * - Left & right horizontal burrows
     - ``(``, ``)`` (Parentheses)

   * - Left & right downward burrows
     - ``{``, ``}`` (Curly braces)


.. _Emoji Fonts:

Emoji Fonts
-----------

.. _unicode_emoji_list: https://www.unicode.org/emoji/charts/full-emoji-list.html


:term:`TTF` and :term:`OTF` fonts contain a table which allows a
computer to look up :term:`glyph` data for a given
:term:`unicode code point`.

Since emoji have been part of the :term:`unicode` standard for years,
there are now font files dedicated purely to the task of providing
emoji. |project_name| offers decent support for converting emoji fonts
into graphics:

* Single-color emoji fonts like `Noto Emoji`_ tend to mostly work
* No :gfonts-gloss:`color font (Google Fonts link) <color_fonts>`
  characters are known to work

Multi-Character Emoji
^^^^^^^^^^^^^^^^^^^^^

.. _recommended ZWJ sequences: https://unicode.org/emoji/charts/emoji-zwj-sequences.html
.. _unicode_modifiers: https://www.unicode.org/emoji/charts/full-emoji-modifiers.html

For simple emoji like 😊 (:codepoint:`1F60A`), things are exactly as they
seem:

* A single :term:`code point` represents the :term:`character`
* A single :term:`glyph` is chosen based on that code point

However, many emoji aren't simple. Instead, they're composed of
multiple :term:`code point <code point>` which combine in at least
two ways.

.. tip:: It's okay to be overhelmed by this.

         Remember, :ref:`Text Rendering is Really Hard`.


:term:`Unicode`'s list of `recommended ZWJ sequences`_


Note that these sequences aren't limited to only two emoji with a single
**zwj** between them. This is why they're called
**zero width joiner sequences** or **zwj sequences**. A given zwj sequence
can also be the base for another zwj sequence formed by appending to it.

Color Emoji
^^^^^^^^^^^

**TL;DR: Not officially supported due to PIL unreliability.**

Although :gfonts-gloss:`color fonts <color_fonts>` are a recent addition.

.. _Math fonts:

Math Fonts
----------
Filler.

.. _Music fonts:

Music fonts
-----------
Songs and bars.