from contextlib import ExitStack
from typing import Optional, Callable

from octofont3.formats import load_font
from octofont3.formats.common.exceptions import (
    FontFormatError, UnclearSourceFontFormat, PipingFromStdinRequiresFontFormat
)
from octofont3.iohelpers import exit_error, StdOrFile
from octofont3.octo import emit_octo


def main(parsed_args, help_callback: Optional[Callable] = None):
    """
    Generate code from a font.

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

    # Set glyph sequence and attempt to output code
    glyph_sequence = getattr(parsed_args, 'glyph_sequence', font.provided_glyphs)
    with ExitStack() as output_streams:
        output_stream = output_streams.enter_context(StdOrFile(parsed_args.output_path, 'w')).raw
        emit_octo(output_stream, font, glyph_sequence=glyph_sequence)
