
.. _glossary_page:

Glossary Page
*************

.. glossary::

   ASCII
    A 7-bit standard extended (and mostly replaced) by :term:`unicode`.

    It's still worth learning about today, especially for |project_name|
    users. In addition to sharing :term:`code points <code point>` with
    :term:`unicode`, ASCII is often used in all of the following:

    * Pixel fonts
    * File formats
    * Retro & fantasy consoles

    If you don't already have a good understanding of ASCII, that's
    okay. Keep the following around will help you develop one:

    * Python's :py:func:`ord` and :py:func:`chr` functions
    * An ASCII reference table

    See the following to learn more:

    * :term:`BDF`
    * :simplewiki-long:`ASCII`
    * :simplewiki-long:`Simple Wikipedia's Binary Number Article<Binary_number>`

   bitmap
   raster
    **Bitmap** or **raster** data specifies values for pixels.

    This includes many types of file formats:

    * Most image files, such as :simplewiki:`PNG`
    * Older font formats, including :term:`BDF`

   BDF
   Glyph Bitmap Distribution Format
    The **Glyph Bitmap Distribution Format** (**BDF** for short) is a
    :term:`raster` font format.

    For multiple reasons, many excellent pixel fonts use this format:

    * Adobe developed both the format and tools for working with it
    * The :simplewiki:`X Window System <X Window System>`
      declared **BDF** an officially supported format in 1988
    * It's text-based, so it's readable to humans as well as computers

    See the following to learn more:

    * `BDF v2.1 Specification (PDF) <https://www.x.org/docs/BDF/bdf.pdf>`_
    * `X11's Release 3 change notes <https://www.x.org/wiki/X11R3/>`_

   character

    This has multiple meanings depending on the context.

   code point
    An identifier that a standard has agreed to mean a certain thing.

    In digital fonts, this is usually a positive
    :simplewiki:`integer <Integer>` assigned to mean a specific
    :term:`character`.

    For example, the :term:`ASCII` standard agrees on ``65`` to mean a
    capital ``"A"`` character. Since :term:`Unicode` extends
    :term:`ASCII`, it shares many code point values.

    See the following to learn more:

    * :term:`ASCII`
    * :term:`Unicode`
    * :simplewiki-long:`Unicode`
    * :simplewiki-long:`ASCII`
    * Python's :py:func:`ord` and :py:func:`chr` functions


   dingbat
    In digital fonts, dingbats tend to refer to any :term:`glyph` other
    than the standard characters for written languages. If a font offers
    dingbats instead of the expected :term:`glyphs <glyph>` for a
    :term:`character`, it is called a :term:`dingbat font`.

    See the following to learn more:

    * :term:`dingbat font`
    * :wikipedia-long:`Dingbat`


   dingbat font
    A digital font which provides :term:`dingbats <dingbat>` instead of
    expected :term:`glyphs <glyph>` for :term:`characters <character>`.

    See |project_name|'s Usage Guide Page on :ref:`font_kinds-dingbat_fonts`


   glyph
    A specific graphical shape used represent a :term:`character`.

    In :term:`unicode`, it mostly doesn't matter what kind
    of :term:`character` it is. Pretty much everything uses
    **glyphs** to represent their characters:

    * Western letter-based writing systems
    * Eastern systems such as Chinese Hanzi
    * Numerals
    * Punctuation
    * Emoji

   PCF
    Old X format.

   OpenType
   OpenType Font
   OTF
    A :term:`vector` font format which is a variant of :term:`TTF`.

    The file extensions for these fonts can be ``.otf`` or ``.ttf``.

   tofu
    A placeholder box displayed when a character can't be rendered.

    This usually appears when:

    * A font lacks a :term:`glyph` for a :term:`character`
    * Software cannot recognize a character for some reason

   TTF
   TrueType
    **TrueType** fonts (**TTF** for short or ``.ttf`` as a file
    extension) are a :term:`vector` font format.

    These fonts are very complex compared to :term:`bitmap` font formats
    such as :term:`BDF`. **TTF** font features include:

    * Alternate :term:`glyph` and :simplewiki:`ligatures <Ligature>`
    * Conditional & iteration logic to help render them smoothly
    * In more recent fonts, there are multiple different

   unicode
    A standard which covers most writing systems & more.

    Although :term:`code point` values ``0`` through ``128`` are
    identical to :term:`ASCII`'s, the standard also covers things other
    than writing systems for spoken languages. This includes emoji,
    math, music, and various other symbols.

    As a general rule, any symbol that's very popular or useful has a
    good chance of being added to the unicode standard.

    .. important:: Fonts, software, and devices can lack support for
                   the latest unicode features!

    To learn more, please see :term:`unicode code point`

   unicode code point
    A :term:`code point` in the :term:`Unicode` standard.

    Since these are added in new revision of the standard, anything made
    before a revision will lack support for its features unless updated
    to do so. This includes:

    * Fonts
    * Software, including Python 3's standard library
    * Devices

    Python's partial support for unicode mostly extends to emoji.
    |project_name| tries to make up for this, but not even the
    powerful ``regex`` replacement for the built-in :py:mod:`re`
    module is fully up to date on all emoji combinations!

    To learn more, please see:

    * |project_name|'s :ref:`Usage Guide page on Emoji fonts <Emoji fonts>`
    * The 3rd party :pypi-dep-page:`regex` module on PyPI

   vector
    In digital fonts and graphics formats, **vector** formats specify
    shapes to draw with math instead of :term:`bitmap` pixels.

    Many recent font formats are :term:`vector`-based because it makes
    scaling eais, these
    are awful for pixel fonts.

