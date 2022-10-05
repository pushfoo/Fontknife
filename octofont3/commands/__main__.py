import argparse
import sys
import textwrap
from collections import ChainMap
from typing import Optional, Callable, Any, Mapping, Dict

from octofont3.commands.convert import main as convert
from octofont3.commands.emit_code import main as emit_code


base_parser = argparse.ArgumentParser(
    description="A utility with multiple sub-commands for manipulating fonts."
)


# Important, setting dest='command' allows subcommand detection to work.
subparsers = base_parser.add_subparsers(dest='command')


# Used with a builder function to reliably display help on subcommands
COMMON_COMMAND_TEMPLATE = {
    'input_path': {
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
    'input-type': {
        'short_flag': '-I',
        'type': str, 'default': None, 'choices': ['textfont', 'bdf', 'pcf', 'ttf'],
        'help': 'Use the specified input type instead of auto-detecting it.'
    },
    'glyph-sequence': {
        'short_flag': '-g',
        'type': str, 'default': None,
        'help': 'Restrict emitted glyphs to a subset. Mandatory for TTFs.'
    },
    'font-size-points': {
        'short_flag': '-p',
        'type': int, 'default': 16,
        'help': 'If the font is scalable (TTF), rasterize it with this point size.'
    },
    'output_path': {
        # Intentionally a string rather than a filetype. See input_file
        # at the top of this template for more information.
        'type': str, 'default': None,
        'help': '''\
            Either of the following:
              1. a path ending in the extension of a supported format.
              2. - to write to stdout. This option makes output type mandatory.
            '''
    },
    'output-type': {
        'short_flag': '-O',
        'type': str,
        'default': None,
        'choices': None,
        'help': "Use the specified output type instead of auto-detecting from path."
    }
}


def _add_argument_specification_to_parser(
    parser: argparse.ArgumentParser,
    argument_specification: Dict[str, Dict[str, Any]],
) -> None:
    """
    Add every argument in the specification to the passed parser.

    Positional arguments should use these rules:

        1. underscores in their names instead of dashes
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
            add_argument_positionals = (short_flag,  f"--{arg_long_name}")
        else:
            raise ValueError('Non-underscore (positional) defaults must provide a short flag')

        # Dedent any multi-line string values in kwargs_dict, such as help
        for key, value in argument_options.items():
            if isinstance(value, str) and value.find('\n'):
                argument_options[key] = textwrap.dedent(value)

        parser.add_argument(*add_argument_positionals, **argument_options)


def add_named_subcommand(
    subparsers_object,
    name: str,
    callback: Callable,
    changes: Optional[Mapping[str, Mapping[str, Any]]] = None,
    description: Optional[str] = None,
    custom_command_template: Optional[Mapping[str, Mapping[str, Any]]] = None
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
    :param custom_command_template: A mapping of name strings to
                                    mappings of strings to any.
    :return:
    """
    base_command_template = custom_command_template or COMMON_COMMAND_TEMPLATE
    changes = changes or {}

    subparser = subparsers_object.add_parser(
        name, description=description, formatter_class=argparse.RawTextHelpFormatter)

    # Merge any changes onto the base command template
    all_keys = tuple(ChainMap(changes, base_command_template).keys())
    command_options = {}
    for key in all_keys:
        changes_value = changes.get(key, {})
        template_value = base_command_template.get(key, {})
        command_options[key] = dict(ChainMap(changes_value, template_value))

    _add_argument_specification_to_parser(subparser, command_options)
    subparser.set_defaults(callback=callback)
    return subparser


convert_parser = add_named_subcommand(
    subparsers, 'convert', convert,
    changes={'output-type': {'choices': ['textfont']}},
    description="Convert fonts between different font representation formats.")


emit_code_parser = add_named_subcommand(
    subparsers, 'emit-code', emit_code,
    changes={'output-type': {'choices': ['octo-chip8']}},
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
        args.callback(args, subparsers.choices[args.command].print_usage)


if __name__ == "__main__":
    main()
