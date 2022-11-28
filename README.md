# Fontknife

Rasterize only the glyphs you need. Cut out everything else.

**Warning: This is alpha-quality software. It is full of bugs and may change drastically!**

Current features:

* Read multiple font formats (TTF, BDF, PCF, 1-bit Sprite sheets)
* Export 1-bit sprite sheets to multiple image formats (PNG, BMP, JPG)
* Guess common formats from file extensions
* Simpler than GUI font editors
* Can be used as a library in custom Python scripts
* Code generation (Partial support for [Octo](https://github.com/JohnEarnest/Octo))

See the end of this file for planned features.

## How do I install it?

### Requirements

1. Python 3.7+
2. Enough disk space to install [pillow](https://pillow.readthedocs.io/en/stable/)
   and its dependencies
3. The ability to [create virtual environments](https://docs.python.org/3/library/venv.html)
   or use [pipx](https://pypa.github.io/pipx/)

### Installation
Create a virtual environment and run the following:

```commandline
pip install fontknife
```

You can use [pipx](https://pypa.github.io/pipx/) instead if you'd like.

If you want to use fontknife as a dependency in your projects, be sure to
[pin a specific version](https://pip.pypa.io/en/stable/topics/repeatable-installs/#pinning-the-package-versions).
Breaking changes are almost guaranteed in the future.

## What does it do?

### 1. Convert Fonts to Sprite Sheets

[Tom thumb](https://robey.lag.net/2010/01/23/tiny-monospace-font.html) is a
public domain pixel font with a common problem: it's shipped in a format
most GUI and game frameworks do not support.

This tool fixes that instantly:

```commandline
fontknife convert tom-thumb.bdf tom_thumb.png
```

![A PNG spritesheet of tom thumb.bdf](https://raw.githubusercontent.com/pushfoo/fontknife/master/doc/tom-thumb.png)

Use your preferred image editor to upscale & adjust the resulting sprite sheet.

*Note: Reading the glyph table for TTF fonts is not yet supported. Unless otherwise
specified, they will be assumed to provide English-focused glyphs. See the next example
for information on how to select specific glyphs.*

### 2. Export Specific Glyphs / Make Game Assets

Imagine you're making a farming game. You need filler assets ASAP.

Use this tool with a
[Noto Emoji Font](https://fonts.google.com/noto/specimen/Noto+Emoji)
variant to rapidly generate filler assets:

```commandline
fontknife convert -P 48 -G "🌽🍇🍎🍏🫐🍓🍒🍐🍅🥕🥔🥒🍑🥑🧅🍈" NotoEmoji-Regular.ttf fruits_and_veggies.png
```

![Fruit and vegetable emoji exported as a PNG sprite sheet](https://raw.githubusercontent.com/pushfoo/fontknife/master/doc/fruits_and_veggies.png)

If you need more color, the outlines created by the command above should be easy
to improve upon with a paint bucket tool in your preferred image editor.

#### Explanation of Flags
| Flag | Long version             | Meaning                                                     |
|------|--------------------------|-------------------------------------------------------------|
| `-P` | `--src-font-size-points` | A point size to render a TTF at. Ignored for non-TTF fonts. |
| `-G` | `--src-glyph-sequence`   | The glyphs to use and the order to render them in.          |

*Note: Although multi-codepoint emoji ( ⛈️ , country and region flags, etc) are not yet supported,
adding support is a high priority due to their usefulness for asset generation and LCD hardware projects.*

### 3. Export Fonts to Octo Code

**Warning: This feature is legacy code inherited from
an earlier project!  Do not rely on the drawing routines it
outputs, only the tables!**

You can generate a width table and sprite data table as valid
[Octo](https://github.com/JohnEarnest/Octo) source
your font meets the following requirements:

1. All glyphs render as 8px x 8px or smaller
2. There are 256 or fewer glyphs in the font

For example, run the following to generate tables of widths and sprite data
for [Tom thumb](https://robey.lag.net/2010/01/23/tiny-monospace-font.html)
as Octo source:

```commandline
fontknife emit-code tom-thumb.bdf tom-thumb.8o
```

You should ignore the prefixed drawing routines in the output. Although this
command's implementation was refactored to increase readability, the underlying
logic is still from before
[Octo's `:stringmode` macro](http://johnearnest.github.io/Octo/docs/Manual.html#strings)
was added. Updating this is on the todo list. See the end of this file for more
information.

## Why did you make this?

tl;dr It helps developers [iterate faster](https://www.youtube.com/watch?v=rDjrOaoHz9s)

If you want a longer history:

1. [I made a PR](https://github.com/jdeeny/octofont/pull/5) for a project
2. After checking back over a year later, I forked the project to start an incremental rewrite
3. Bitmap fonts were repeatedly brought up as a potential future feature for
   two projects I contribute to, [pyglet](https://github.com/pyglet/pyglet)
   and [arcade](https://github.com/pythonarcade/arcade)
4. I started reading up on bitmap fonts to learn more 
5. It became painfully clear that finding and importing assets would become
   even more of a friction point if that feature was added
6. Format conversion proved to be more useful and interesting to solve than
   Octo support

The project began shifting focus and gaining inertia at roughly item 4. I've
been using the project as an opportunity to applying new techniques and Python
features I've learned about when appropriate.

## When will you add X?

When I have time or if I merge a PR.

Features I'd like to add, roughly in order of descending priority:

* Export with a transparent background color
* Upscaling flags to apply during rasterization and after sprite sheet creation
* Image folder export format, 1 glyph per file
* Support for automatically reading TTF glyph tables
* Multi-codepoint emoji (examples: ⛈️ , 🌶️, country/region flags)
* Fix ugly caching behavior
* Regex-like expressions for glyph selection
* C header code generation
* Refactor Octo generation
* Additional font formats, both old
  ([FNT](https://web.archive.org/web/20110513200924/http://support.microsoft.com/kb/65123), etc)
  and new ([UXF](https://wiki.xxiivv.com/site/ufx_format.html), etc).
* Additional color support
* Color TTF support
