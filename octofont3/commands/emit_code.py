from contextlib import ExitStack
from typing import Optional, Callable

from octofont3.formats.loader import load_font, FontLoadingError
from octofont3.iohelpers import guess_path_type, exit_error, StdOrFile
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
    input_path = parsed_args.input_path
    output_path = parsed_args.output_path

    input_type = parsed_args.input_type or guess_path_type(input_path)
    output_type = parsed_args.output_type or guess_path_type(output_path)

    if input_type is None:
        exit_error(
            "You must specify the input type when piping from stdin.",
            before_message=help_callback)
    if output_type is None:
        exit_error(
            "You must specify the output type when piping to stdout.",
            before_message=help_callback)

    # Attempt to load the raw font data
    font = None
    try:
        font = load_font(input_path, font_size=parsed_args.font_size_points, source_type=input_type)
    except FontLoadingError as e:
        exit_error(e)
    except FileNotFoundError as e:
        exit_error(e)
    if font is None:
        exit_error(
            "Font is None despite lack of exceptions."
            " Please file a bug report."
        )

    # Set glyph sequence and attempt to output code
    glyph_sequence = getattr(parsed_args, 'glyph_sequence', font.provided_glyphs)

    with ExitStack() as output_streams:
        output_stream = output_streams.enter_context(StdOrFile(output_path, 'w')).raw
        emit_octo(output_stream, font, glyph_sequence=glyph_sequence)
