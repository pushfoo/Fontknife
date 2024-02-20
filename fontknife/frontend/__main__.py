import argparse
import sys
from typing import Optional

from fontknife.frontend.arg_parsing import (
    add_named_subcommand,
    get_source_path_and_args,
    get_output_path_and_args
)
from fontknife.frontend.commands.convert import main as convert
from fontknife.frontend.commands.emit_code import main as emit_code
from fontknife.formats import (
    FormatWriter,
    load_font,
    UnclearSourceFontFormat,
    PipingFromStdinRequiresFontFormat
)
from fontknife.formats.common.exceptions import FontFormatError
from fontknife.iohelpers import exit_error

base_parser = argparse.ArgumentParser(
    description="A utility with multiple sub-commands for manipulating fonts."
)

# Important, setting dest='command' allows subcommand detection to work.
subparsers = base_parser.add_subparsers(dest='command')


# Template the converter subcommand
convert_parser = add_named_subcommand(
    subparsers, 'convert', convert,
    description="Convert fonts between different font representation formats.",
    changes={
        'out-format': {'choices': list(FormatWriter.by_format_name.keys())},
        'out-sheet-bounds-px': {
            'short_flag': '-b', 'default': None, 'type': int, 'nargs': 4,
            'help': '''\
                A subsection of the image to use, as left top right bottom.

                If not specified, the whole image will be assumed to be valid
                sprite sheet data.
                '''
        },
        'out-sheet-size-tiles': {
            'short_flag': '-c', 'default': None, 'type': int, 'nargs': 2,
            'help': '''\
                The size of the sheet as width height in rows and columns.

                If no sheet size is specified, it will be calculated from
                the tile size if it was provided.
                '''
        },
        'out-sheet-scale': {
            'short_flag': '-m', 'default': 1, 'type': int,
            'help': '''\
                The scale multiplier for the sprite sheet. Must be an integer
                value of 1 or greater.

                If it is greater than 1, the sheet will be scaled up using
                the provided multiplier via nearest neighbor scaling.
            '''
        },
        'out-tile-size-px': {
            'short_flag': '-t', 'default': None, 'type': int, 'nargs': 2,
            'help': '''\
                Output sheet's size per tile as width height in pixels.

                Does not account for inter-tile spacing. If no tile size is
                specified, it will be calculated from the other provided
                sheet dimensions if possible.
                '''
        },
        'out-tile-spacing-px': {
            'short_flag': '-s', 'default': [0, 0], 'type': int, 'nargs': 2,
            'help': '''\
                Spacing between spritesheet tiles as a pair of pixel lengths.

                Leaving this unspecified is equivalent to -s 0 0
            '''
        },
    })


emit_code_parser = add_named_subcommand(
    subparsers, 'emit-code', emit_code,
    changes={'out-format': {'choices': ['octo-chip8']}},
    description="Emit a font's data as code in a programming language.")


def main() -> int:

    # Print help if called without args
    if len(sys.argv) == 1:
        base_parser.print_help()
        return 2

    args = base_parser.parse_args()

    command = args.command
    raw_args_dict = vars(args)  # Need a dict for remap to work

    # Load the font data
    source_path, source_kwargs = get_source_path_and_args(raw_args_dict)
    font = None
    help_callback = subparsers.choices[command].print_usage
    try:
        font = load_font(source_path, **source_kwargs)

    # Handle only reasonably expected exception types
    except (UnclearSourceFontFormat, PipingFromStdinRequiresFontFormat) as e:
        exit_error(e, before_message=help_callback)
    except (FontFormatError, FileNotFoundError) as e:
        exit_error(e)

    # Generate requested output
    output_path, output_kwargs = get_output_path_and_args(raw_args_dict)
    args.callback(font, output_path, output_kwargs)

    return 0


if __name__ == "__main__":
    main()
