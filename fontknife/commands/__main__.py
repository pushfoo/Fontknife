import argparse
import re
import sys
import textwrap
from collections import ChainMap
from typing import Optional, Callable, Any, Mapping, Dict, Union, Tuple, Pattern, Iterable

from fontknife.commands.convert import main as convert
from fontknife.commands.emit_code import main as emit_code
from fontknife.formats import FormatReader, FormatWriter, load_font, UnclearSourceFontFormat, \
    PipingFromStdinRequiresFontFormat
from fontknife.formats.common.exceptions import FontFormatError
from fontknife.graphemes import cli_grapheme_arg
from fontknife.iohelpers import exit_error
from fontknife.utils import remap_prefixed_keys, extract_matching_keys, tuplemap


base_parser = argparse.ArgumentParser(
    description="A utility with multiple sub-commands for manipulating fonts."
)

# Important, setting dest='command' allows subcommand detection to work.
subparsers = base_parser.add_subparsers(dest='command')


# Used with a builder function to reliably display help on subcommands
COMMON_COMMAND_TEMPLATE = {
    'src_path': {
        # This is a string rather than using argparse.FileType because
        # the latter mandates involvement with subclassing a protected
        # class on Python < 3.9. The documentation warns that class
        # could change at any time. Deferring processing this to the
        # callback is easier and guarantees compatibility with more
        # python versions.
        'type': str, 'default': None,
        'help': '''\
            Either of the following:
              1. A path to a font in a supported font format
              2. - to pipe data from stdin. This option makes input type mandatory.

            '''
    },
    'src-format': {
        'short_flag': '-F',
        'type': str, 'default': None, 'choices': list(FormatReader.by_format_name.keys()),
        'help': 'Use the specified source type instead of auto-detecting it.'
    },
    'src-glyph-sequence': {
        'short_flag': '-G',
        'type': cli_grapheme_arg, 'default': None,
        'help': '''\
            Manually specify the glyphs provided by the source font.

            Strongly recommended for TTFs and sprite sheets. The default
            sequence generated by loaders may not apply to a given file.
        '''
    },
    'src-font-size-points': {
        'short_flag': '-P',
        'type': int, 'default': 16,
        'help': '''\
            If the font is scalable (TTF), rasterize it with this point size.

            Has no effect for non-scalable fonts.
        '''
    },
    'src-sheet-bounds-px': {
        'short_flag': '-B', 'default': None, 'type': int, 'nargs': 4,
        'help': '''\
            The subsection of the image to use, as left top right bottom.

            If not specified, the whole image will be assumed to be valid
            sprite sheet data.
        '''
    },
    'src-sheet-size-tiles': {
        'short_flag': '-C', 'default': None, 'type': int, 'nargs': 2,
        'help': '''\
            Source tile sheet width x height in tiles / cells.

            If no sheet size is specified, it will be calculated from
            the tile size if it was provided.
            '''
    },
    'src-tile-size-px': {
        'short_flag': '-T', 'default': None, 'type': int, 'nargs': 2,
        'help': '''\
            Source sheet's tile size as width height, measured in pixels.

            If no tile size is specified, it will be calculated from
            the the sheet size if it was provided.
            '''
    },
    'src-tile-spacing-px': {
        'short_flag': '-S', 'default': [0, 0], 'type': int, 'nargs': 2,
        'help': '''\
            Spacing between spritesheet tiles as a pair of pixel lengths.

            Leaving this unspecified is equivalent to -s 0 0
        '''
    },
    'out_path': {
        # Intentionally a string rather than a filetype. See input_file
        # at the top of this template for more information.
        'type': str, 'default': None,
        'help': '''\
            Either of the following:
              1. a path ending in the extension of a supported format.
              2. - to write to stdout. This option makes output type mandatory.
        '''
    },
    'out-format': {
        'short_flag': '-f',
        'type': str,
        'default': None,
        'choices': None,
        'help': "Use the specified output type instead of auto-detecting from path."
    },
    'out-glyph-sequence': {
        'short_flag': '-g',
        'type': cli_grapheme_arg, 'default': None,
        'help': '''\
            Manually override the order of the emitted glyphs.

            Be careful when using this.
        '''
    },
}


def make_prefix_regex(prefix: str) -> Pattern:
    return re.compile('^' + prefix + r'[-_]')


SOURCE_PREFIX = 'src'
SOURCE_PREFIX_REGEX = make_prefix_regex(SOURCE_PREFIX)
OUTPUT_PREFIX = 'out'
OUTPUT_PREFIX_REGEX = make_prefix_regex(OUTPUT_PREFIX)


def dashes_to_underscores(s: str) -> str:
    return s.replace('-', '_')


def extract_arg_names(source: Dict[str, Any], pattern: Union[str, Pattern]) -> Tuple[str, ...]:
    raw = extract_matching_keys(source, pattern)
    dash_fixed = tuplemap(lambda s: dashes_to_underscores(s[4:]), raw)
    return dash_fixed


def _add_argument_specification_to_parser(
    parser: argparse.ArgumentParser,
    argument_specification: Dict[str, Dict[str, Any]],
) -> None:
    """
    Add every argument in the specification to the passed parser.

    Positional arguments should use these rules:

        1. Underscores in their names instead of dashes
        2. No 'short_flag' key in their template

    Any multi-line text in a kwarg value will have a dedent operation
    applied.

    :param parser: The parser to add this argument spec to
    :param argument_specification: A valid specification for an argument.
    :returnarg_options:
    """
    for arg_long_name, argument_options in argument_specification.items():

        # Remove short flag from the template
        short_flag = argument_options.pop('short_flag', None)

        # Compute the positionals for add_argument
        if '_' in arg_long_name:
            add_argument_positionals = (arg_long_name,)
        elif short_flag:
            add_argument_positionals = (short_flag, f"--{arg_long_name}")
        else:
            raise ValueError(
                f"Non-underscore (positional) defaults must provide a short flag: "
                f"{arg_long_name} : {argument_options}"
            )

        # Dedent any multi-line string values in kwargs_dict, such as help
        for key, value in argument_options.items():
            if isinstance(value, str) and value.find('\n'):
                argument_options[key] = textwrap.dedent(value)

        parser.add_argument(*add_argument_positionals, **argument_options)


def merge_configs(*configs: Mapping[str, Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Merge passed configs into one

    Earlier entries have higher priority than later ones.

    :param configs: The command configs to merge.
    :return: A dict of dicts as the merged entry.
    """
    all_keys = tuple(ChainMap(*configs).keys())
    merged = {}
    for key in all_keys:
        raw_merged_entry = ChainMap(*(c.get(key, {}) for c in configs))
        merged[key] = dict(raw_merged_entry)

    return merged


# Store command details to help pass
_source_arg_names_for_command = {}
_output_arg_names_for_command = {}


def add_named_subcommand(
        subparsers_object,
        name: str,
        callback: Callable,
        changes: Optional[Mapping[str, Mapping[str, Any]]] = None,
        description: Optional[str] = None,
        base_command_template: Optional[Mapping[str, Mapping[str, Any]]] = None
):
    """
    Build a subparser which has a callback.

    The inner mappings for ``base_command_template`` must consist of
    valid argument names and values for ``argparser.add_argument``,
    except for the optional ``short_flag`` key. This key is used to
    provide a short flag option for non-positional command arguments.

    :param subparsers_object: A subparsers object for a root parser
    :param name: The name of the new parser on the subparsers collection
    :param callback: A callable that takes args and a subparser.
                            It acts like a main method.
    :param changes: A dict args to add or update
    :param description: A description for this sub-command
    :param base_command_template: Override using COMMON_COMMAND_TEMPLATE
                                  as the base.
    :return:
    """
    base_command_template = base_command_template or COMMON_COMMAND_TEMPLATE

    subparser = subparsers_object.add_parser(
        name, description=description, formatter_class=argparse.RawTextHelpFormatter)
    if changes:
        final_options = merge_configs(changes, base_command_template)
    else:
        final_options = base_command_template

    _add_argument_specification_to_parser(subparser, final_options)

    _source_arg_names_for_command[name] = extract_arg_names(final_options, SOURCE_PREFIX_REGEX)
    _output_arg_names_for_command[name] = extract_arg_names(final_options, OUTPUT_PREFIX_REGEX)

    subparser.set_defaults(callback=callback)
    return subparser


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


def general_help_and_exit_if_code(exit_code: Optional[int] = None):
    """
    Print the list of commands, then exit if exit_code is not None

    :param exit_code: An exit code to use
    :return:
    """
    print("The following commands are available:\n")
    for command_name in subparsers.choices.keys():
        print("  ", command_name)
    print("\nPlease use -h or --help with any command for more information.")

    if exit_code is not None:
        sys.exit(exit_code)


def get_endpoint_path_and_args(
    raw_args_dict: Dict[str, Any],
    prefix: str,
    names_to_remap: Iterable[str]
) -> Tuple[str, Dict[str, Any]]:
    remapped = remap_prefixed_keys(raw_args_dict, prefix, names_to_remap)
    path = remapped.pop('path')
    return path, remapped


def main():
    args = base_parser.parse_args()
    command = args.command

    if command is None:
        general_help_and_exit_if_code(exit_code=2)

    if len(sys.argv) == 2:
        if command:
            subparser = subparsers.choices[args.command]
            subparser.print_help()
            exit(1)

        else:
            general_help_and_exit_if_code(exit_code=2)

    # Translate to a dict that works with remap
    raw_args_dict = vars(args)

    # Load the font data
    source_path, source_kwargs = get_endpoint_path_and_args(
        raw_args_dict, 'src_', _source_arg_names_for_command[command])

    font = None
    help_callback = subparsers.choices[args.command].print_usage
    try:
        font = load_font(source_path, **source_kwargs)

    # Handle only reasonably expected exception types
    except (UnclearSourceFontFormat, PipingFromStdinRequiresFontFormat) as e:
        exit_error(e, before_message=help_callback)
    except (FontFormatError, FileNotFoundError) as e:
        exit_error(e)

    # Generate requested output
    output_path, output_kwargs = get_endpoint_path_and_args(
        raw_args_dict, 'out_', _output_arg_names_for_command[command])

    args.callback(font, output_path, output_kwargs)


if __name__ == "__main__":
    main()
