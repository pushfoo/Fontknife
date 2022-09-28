import re
from collections import deque, Mapping as MappingABC
from functools import cache
from typing import Optional, Tuple, Iterable, Union, Mapping, Callable, Any

from octofont3.custom_types import TextIOBaseSubclass


PairTypeStr = Tuple[type, str]
IterablePairTypeStrs = Iterable[PairTypeStr]


NEWLINE_REGEX = re.compile('\n')




class OutputHelper:
    """
    Encapsulate common operations on source output streams

    Subclasses should be made for specific formats & languages.
    """
    def __init__(self, stream: TextIOBaseSubclass, comment_prefix: str = "# "):
        super().__init__()
        self._stream = stream
        self._comment_prefix = comment_prefix
        self._indent_level = 0
        self._line_index = 0
        self._column_index = 0

    def write(self, s: str) -> None:
        if s == '':
            return

        self._stream.write(s)

        line_increment = 0
        last_occurence_end = None
        it = NEWLINE_REGEX.finditer(s)
        for match in NEWLINE_REGEX.finditer(s):
            _, last_occurence_end = match.span()
            line_increment += 1

        if last_occurence_end is None:  # No newlines, so move right
            self._column_index += len(s)

        else:  # Move to the end of the current line
            self._column_index = len(s) - last_occurence_end
            self._line_index += line_increment

    def newline(self):
        self.write("\n")

    def print(self, *objects, sep: str = ' ', end: str = '\n') -> None:
        first = True

        for object_ in objects:

            if first:
                first = False
            else:
                self.write(sep)

            self.write(str(object_))

        self.write(end)

    def comment(self, *objects, comment_prefix: Optional[str] = None, sep=' ', end='\n') -> None:
        comment_prefix = comment_prefix or self._comment_prefix
        self.print(f"{comment_prefix}{sep.join(str(ob) for ob in objects)}", end=end)

    def write_iterable_data(
        self,
        data: Iterable,
        data_transform: Optional[Callable] = repr,
        line_prefix: str = "",
        sep=", ",
        end="\n",
        max_line_length: int = 80
    ) -> None:
        """
        Write a long iterable to the stream, wrapping when hitting line length.

        :param data:
        :param data_transform:
        :param line_prefix:
        :param sep:
        :param max_line_length:
        :return:
        """

        sep_len = len(sep)
        max_line_index = max_line_length - 1

        queue = deque(data)

        while queue:
            if self._column_index == 0:
                self.write(line_prefix)

            raw_data = queue.popleft()
            if data_transform is None:
                transformed = raw_data
            else:
                transformed = data_transform(raw_data)

            transformed_len = len(transformed)

            addition_len = transformed_len
            queue_len = len(queue)
            if queue_len > 1:
                addition_len += sep_len

            if self._column_index + addition_len > max_line_index:
                self.write(end)
                self.write(line_prefix)

            self.print(transformed, end=sep if queue_len else '')

        self.write(end)


class InputHelper:
    """
    Encapsulate common input operations on streams.

    Can be subclassed to make parsing formats easier.
    """
    def __init__(self, stream: TextIOBaseSubclass, comment_prefix: str = '#'):
        self._comment_prefix = comment_prefix
        self._stream = stream
        self._line_index = -1
        self._next_line: Optional[str] = None
        self.readline()

    @property
    def raw(self):
        return self._stream

    def lineno(self) -> int:
        return self._line_index + 1

    def peekline(self) -> str:
        return self._next_line

    def readline(self, discard_comment_lines: bool = True):
        out = self._next_line
        # Handle the stream already being at EOF

        new_line = self._stream.readline()
        self._line_index += 1

        if discard_comment_lines:
            while new_line.startswith(self._comment_prefix):
                new_line = self._stream.readline()
                self._line_index += 1

                # The stream is finished.
                if not new_line:
                    self._next_line = new_line
                    return new_line

        self._next_line = new_line

        return out


def strip_end_comments(line: str, comment_start: str = "#") -> str:
    index = line.rfind(comment_start)

    if index < 0:
        return line

    return line[:index]


def strip_end_comments_and_space(line: str, comment_start: str = '#') -> str:
    return strip_end_comments(line, comment_start=comment_start).rstrip()


def padded_hex(
    value: int, num_digits: int = 2,
    number_prefix="0x", upper: bool = True
) -> str:
    value = hex(value)[2:].zfill(num_digits)

    if upper:
        value = value.upper()

    return f"{number_prefix}{value}"


# Keeping this as a tuple silences linter warnings about mutability
REGEX_TYPE_MAP = (
    (int, r'0x[\da-fA-F]+|\d+'),  # Decimal ints or hex ints prefixed with '0x'.
    (str, r'\"(?:[^\"\\]|\\.)*\"'),  # Quoted strings, with escapes
    (None, r'\S+')  # Unspecified types match anything that isn't whitespace
)


@cache
def mapping_dict_from_sequence(pairs: Tuple[PairTypeStr]):
    """
    Generate a dict for a given set of pairs.

    This is cached in case of library use of this function.
    :param pairs:
    :return:
    """
    return dict(pairs)


@cache
def header_regex(
    title: Optional[str] = None,
    regex_start_of_line: bool = True,
    regex_type_map: Union[IterablePairTypeStrs, Mapping[type, str]] = REGEX_TYPE_MAP,
    regex_accepted_whitespace: str = ' ',
    **header_fields: Optional[Union[type, str]]
):
    """
    Make a regex object matching the header pattern described by kwargs.

    Header patterns generally follow this pattern::

        HEADER: "string" 1 0x04

    The name of each keyword argument will be used to create a named
    matching group in the returned regex. The value for each keyword
    can be any of the following:

        * A type in the passed template collection, ``regex_type_map``.
        * ``None``, in which case any non-whitespace will be matched.
        * A regex sub-expression compatible with being placed in
          a named group.

    :param title: The title of the header
    :param regex_start_of_line: Whether to match the start of a line.
    :param regex_type_map: A mapping of types to detection regexes.
    :param header_fields: each kwarg name should pass a type in the type
                          map or a regex literal.
    :param regex_accepted_whitespace: a literal or regex expression
                                      describing acceptable spacing
                                      between fields.
    :return: A regex object matching the requested header structure.
    """

    # Convert the type mapping to a dict if needed
    if not isinstance(regex_type_map, MappingABC):
        regex_type_map = mapping_dict_from_sequence(tuple(regex_type_map))

    # A place to store regex components before compilation
    regex_parts = []

    # Generate the header
    if not title:
       title = r"\w+"
    regex_parts.append(f"(?P<header_title>{title}):")

    # Generate a named group expression for each field of the header
    for header_field, type_or_regex_string in header_fields.items():

        if isinstance(type_or_regex_string, str):
            field_regex = type_or_regex_string

        elif type_or_regex_string not in regex_type_map:
            raise KeyError(
                f"No group template in type map for {type_or_regex_string}")
        else:
            field_regex = regex_type_map[type_or_regex_string]

        field_group_regex = f"(?P<{header_field}>{field_regex})"
        regex_parts.append(field_group_regex)

    # Finish the regex & return it, including the start of line marker if requested
    whitespace = f"{regex_accepted_whitespace}+"
    regex_string = f"{'^' if regex_start_of_line else ''}{whitespace.join(regex_parts)}"
    regex = re.compile(regex_string)
    return regex



