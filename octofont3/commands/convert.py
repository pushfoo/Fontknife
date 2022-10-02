"""
Convert between formats.
"""
from contextlib import ExitStack
from pathlib import Path

from octofont3.formats.loader import load_font
from octofont3.formats.textfont.writer import FontRenderer
from octofont3.iohelpers import guess_path_type, StdOrFile, exit_error, SeekableBinaryFileCopy
from octofont3.utils import generate_glyph_sequence


def main(parsed_args, parser):
    """
    Run the converter.

    This function is not intended to be run outside of an argparser
    context. It is used in __main__.py as a callback.

    :param parsed_args: The namespace object parsed by argparse
    :param parser: Only passed so that help can be printed
    :return:
    """

    font_points = 8

    input_path = parsed_args.input_path
    output_path = parsed_args.output_path

    input_path_type = parsed_args.input_type or guess_path_type(input_path)
    output_path_type = parsed_args.output_type or guess_path_type(output_path)

    if output_path_type not in ('textfont', ):
        if output_path == "-":
            message = "Ambiguous output type. Please specify the output type when piping to stdout."
        else:
            message = f"Unrecognized output type {output_path_type!r}\n"
        exit_error(message, lambda: parser.print_usage())

    # Load the file to a seekable copy
    with ExitStack() as input_streams:
        input_stream = input_streams.enter_context(StdOrFile(input_path, 'r')).raw
        seekable_bytes_copy = SeekableBinaryFileCopy.copy(input_stream)
        font = load_font(seekable_bytes_copy, font_size=8, source_type=input_path_type)

    # Use any glyph sequence to reorder the output emission order
    local_sequence = getattr(parsed_args, 'glyph_sequence', font.provided_glyphs)

    with ExitStack() as output_streams:
        output_stream = output_streams.enter_context(StdOrFile(output_path, 'w')).raw

        renderer = FontRenderer(output_stream, verbose=False)
        renderer.emit_textfont(font, local_sequence, actual_source_path=input_path)