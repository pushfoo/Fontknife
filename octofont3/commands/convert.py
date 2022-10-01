"""
Convert between formats.
"""
import sys
from pathlib import Path

from octofont3.formats.loader import load_font
from octofont3.formats.textfont.writer import FontRenderer
from octofont3.iohelpers import guess_path_type
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
    glyph_sequence = parsed_args.glyph_sequence
    default_glyphs = generate_glyph_sequence()
    source_file_paths = parsed_args.input_files

    close_after_writing_stream = None
    if parsed_args.output_path is None:
        out_stream = sys.stdout
    else:
        close_after_writing_stream = open(parsed_args.output_path, 'w')
        out_stream = close_after_writing_stream

    try:
        renderer = FontRenderer(out_stream, verbose=False)

        for raw_path in source_file_paths:
            path = Path(raw_path)
            path_type = parsed_args.input_type or guess_path_type(path)
            font = load_font(path, force_type=path_type)

            if path_type == 'ttf' and not glyph_sequence:
                local_sequence = default_glyphs
            else:
                local_sequence = font.provided_glyphs

            renderer.emit_textfont(font, local_sequence, actual_source_path=path)
    finally:
        if close_after_writing_stream:
            close_after_writing_stream.close()