import argparse
import sys
from typing import Iterable, Optional, Callable

from octofont3.commands.convert import main as convert
from octofont3.commands.emit_code import main as emit_code


base_parser = argparse.ArgumentParser(
    description="A utility with multiple sub-commands for manipulating fonts."
)


# Important, allows subcommand detection to work later.
subparsers = base_parser.add_subparsers(dest='command')


# Used with a builder function to reliably display help on subcommands
COMMAND_OPTIONS = {
    'input_path': (tuple(), {
        'type': str,# 'default': None,
         'help': "Either a path to load glyph data from, or - for stdin. The latter option is only supported for some"
                 "combinations of source and destination."
    }),
    'input-type': (('-I',), {
        'type': str, 'default': None, 'choices': ['textfont', 'bdf', 'pcf', 'ttf'],
        'help': 'Override input file type(s) detected from path(s)'
    }),
   'glyph-sequence': (('-g',), {
        'type': str, 'default': None,
        'help': 'The glyph sequence to use. Mandatory for TTFs,'
                ' but other types can omit it to dump all glyphs in the file.'
    }),
    'font-size-points': (('-p',), {
        'type' : int, 'default': 16,
        'help': 'The font size in points to use. Currently only relevant for truetype fonts.'
    }),
    'output_path': (tuple(), {
        'type': str, 'default': None,
        'help': 'Either a path to write output to, or - for stdout. The latter option is only available for some'
                 'combinations of source and destination.'})
}


def add_template_args_to_parser(parser, arg_names: Iterable[str]):
    for arg_name in arg_names:
        base_args, kwargs = COMMAND_OPTIONS[arg_name]

        if '_' in arg_name:
            final_args = (arg_name,)
        else:
            final_args = base_args + (f"--{arg_name}",)

        parser.add_argument(*final_args, **kwargs)


def build_subparser_args(parser, requested_args: Optional[Iterable[str]] = None):

    if requested_args is None:
        requested_args = COMMAND_OPTIONS.keys()

    add_template_args_to_parser(parser, requested_args)


def add_named_subcommand(
    subparser_object,
    name: str,
    parser_callback: Callable,
    description: Optional[str] = None,
    template_arg_names: Optional[Iterable[str]] = None
):
    """
    Build a parser that automatically calls a function if successful.

    :param name: The name for this parser.
    :param parser_callback: A callable. These should be like main()
    :param template_arg_names: A list of templated args to include.
    :return:
    """
    subparser = subparser_object.add_parser(name, description=description)
    build_subparser_args(subparser, template_arg_names)
    subparser.set_defaults(func=parser_callback)
    return subparser


convert_parser = add_named_subcommand(
    subparsers, 'convert', convert,
    description="Convert between different fonts representations.")
convert_parser.add_argument(
    '-O', '--output-type', type=str, default=None,
    choices=['textfont'],
    help="Directly specify the output format, overriding automatic detection from path")


emit_code_parser = add_named_subcommand(
    subparsers, 'emit-code', emit_code,
    description="Emit code for statically including the font data in various programming languages")
emit_code_parser.add_argument(
    '-O', '--output-language', type=str, default=None,
    choices=['octo-chip8'],
    help="Directly specify the output format, overriding automatic detection from path")


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


def main():

    args = base_parser.parse_args()

    if args.command is None:
        general_help_and_exit_if_code(exit_code=2)

    if len(sys.argv) == 2:
        if args.command:
            subparser = subparsers.choices[args.command]
            subparser.print_help()
        else:
            general_help_and_exit_if_code(exit_code=2)

    else:  # Actually run the command
        args.func(args, subparsers.choices[args.command])


if __name__ == "__main__":
    main()
