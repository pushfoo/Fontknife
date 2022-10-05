"""
Convert between formats.
"""
from contextlib import ExitStack

from octofont3.formats.loader import load_font, FontLoadingError
from octofont3.formats.textfont.writer import FontRenderer
from octofont3.iohelpers import guess_path_type, StdOrFile, exit_error


def main(parsed_args, parser):
    """
    Run the converter.

    This function is not intended to be run outside of an argparser
    context. It is used in __main__.py as a callback.

    :param parsed_args: The namespace object parsed by argparse
    :param parser: Only passed so that help can be printed
    :return:
    """

    input_path = parsed_args.input_path
    output_path = parsed_args.output_path

    input_path_type = parsed_args.input_type or guess_path_type(input_path)
    output_path_type = parsed_args.output_type or guess_path_type(output_path)

    if output_path_type is None:
        exit_error(
           "Ambiguous output type. Please specify the output type when piping to stdout.",
           before_message=lambda: parser.print_usage())

    try:
        font = load_font(input_path, font_size=parsed_args.font_size_points, source_type=input_path_type)
    except FontLoadingError as e:
        exit_error(e)
    except FileNotFoundError as e:
        exit_error(e)

    glyph_sequence = getattr(parsed_args, 'glyph_sequence', font.provided_glyphs)

    with ExitStack() as output_streams:
        output_stream = output_streams.enter_context(StdOrFile(output_path, 'w')).raw
        renderer = FontRenderer(output_stream, verbose=False)
        renderer.emit_textfont(font, glyph_sequence, actual_source_path=input_path)