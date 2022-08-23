# octofont


```ttf-to-textfont``` will convert a TrueType font into a 'textfont' file, which is a simple text file describing a bitmapped font.

```textfont-to-octo``` will convert the textfont file into [Octo](http://johnearnest.github.io/Octo/) assembly code.

An intermediate file is used so that the font can be hand edited before the final conversion.

Requirements:
 - Python 3.6+
 - [pillow](https://pillow.readthedocs.io/en/stable/) to read TTF fonts
 
*Note: Although 3.4 and 3.5 are end-of-life, it may still be possible to run on them using
 [future-fstrings](https://pypi.org/project/future-fstrings/).*


This is a hacked-up work in progress. To get full functionality, you will need to edit the source code. ```textfont-to-octo``` is
especially rough. Currently limited to 8x8px or smaller glyphs.

Many improvements could be made:
 - Handling of larger glyphs, using multiple sprite ops and/or 16-bit SuperChip sprites
 - A sparse mode with a glyph location lookup table to avoid lots of 0s
 - A fixed width mode without a width table
 - Variable height glyphs
 - Optional output of sample test code
 - Additional functions, such as drawing a string
 - Advanced kerning rules
 - Optional guards for out-of-bounds inputs
 - Better handling of vertical alignment and the font baseline. Clipping the glyphs with a bounding box is not helping with this.
 - Use of register aliases
