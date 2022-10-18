"""
Convert between formats.
"""
from typing import Callable, Optional

from octofont3.formats import load_font, write_font
from octofont3.formats.common import FontFormatError, UnclearSourceFontFormat, PipingFromStdinRequiresFontFormat
from octofont3.iohelpers import exit_error


def main(parsed_args, help_callback: Optional[Callable] = None):
    """
    Convert between font formats.

    This function is not intended to be run outside an argparser
    context. It is used in __main__.py as a callback.

    :param parsed_args: The namespace object parsed by argparse
    :param help_callback: A callable that prints help info.
    :return:
    """

    # Attempt to load the raw font data
    font = None
    try:
        font = load_font(
            parsed_args.input_path,
            font_size=parsed_args.font_size_points,
            format_name=parsed_args.input_type)

    # Handle only reasonably expected exception types
    except (UnclearSourceFontFormat, PipingFromStdinRequiresFontFormat) as e:
        exit_error(e, before_message=help_callback)
    except (FontFormatError, FileNotFoundError) as e:
        exit_error(e)

    # Set glyph sequence and attempt conversion
    glyph_sequence = getattr(parsed_args, 'glyph_sequence', font.provided_glyphs)
    write_font(font, parsed_args.output_path, format_name=parsed_args.output_type, glyph_sequence=glyph_sequence)
