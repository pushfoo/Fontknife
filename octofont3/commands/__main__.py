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
    'input_files': (tuple(), {'type': str, 'nargs': '*', 'help': "The source file(s) to use"}),
    'input-type': (('-I',), {
        'type': str, 'default': None, 'choices': ['textfont', 'bdf', 'pcf', 'ttf', 'textfont-stdin'],
        'help': 'Override input file type(s) detected from path(s)'
    }),
    'glyph-sequence': (('-g',), {
        'type': str, 'default': None,
        'help': 'The glyph sequence to use. Mandatory for TTFs,'
                ' but other types can omit it to dump all glyphs in the file.'
    }),
    'output-path': (('-o',), {'type': str, 'default': None, 'required': True, 'help': 'Where to write the output to'})
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

    elif 'input_files' not in requested_args:
        requested_args = ('input_files',) + tuple(requested_args)

    add_template_args_to_parser(parser, requested_args)


def add_named_subcommand(subparser_object, name: str, parser_callback: Callable, template_arg_names: Optional[Iterable[str]] = None):
    """
    Build a parser that automatically calls a function if successful.

    :param name: The name for this parser.
    :param parser_callback: A callable. These should be like main()
    :param template_arg_names: A list of templated args to include.
    :return:
    """
    subparser = subparser_object.add_parser(name)
    build_subparser_args(subparser, template_arg_names)
    subparser.set_defaults(func=parser_callback)
    return subparser


convert_parser = add_named_subcommand(subparsers, 'convert', convert)
convert_parser.add_argument(
    '-O', '--output-type', type=str, default='textfont',
    choices=['auto', 'textfont'],
    help="Directly specify the output format, overriding automatic detection from path"
)


emit_code_parser = add_named_subcommand(subparsers, 'emit-code', emit_code)
emit_code_parser.add_argument(
    '-O', '--output-language', type=str, default=None,
    choices=['octo', '8o'],
    help="Directly specify the output format, overriding automatic detection from path"
)


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
