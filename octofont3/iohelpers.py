import re
import sys
from collections import deque
from collections.abc import Mapping as MappingABC
from contextlib import ExitStack
from functools import cache
from io import IOBase, BytesIO, TextIOWrapper
from pathlib import Path
from typing import Optional, Tuple, Iterable, Union, Mapping, Callable, Any, BinaryIO, TypeVar, TextIO

from octofont3.custom_types import TextIOBaseSubclass, PathLike, StreamOrPathLike, HasReadline, HasTextReadline
from octofont3.utils import has_all_methods, value_of_first_attribute_present


PairTypeStr = Tuple[type, str]
IterablePairTypeStrs = Iterable[PairTypeStr]


NEWLINE_REGEX = re.compile('\n')
VALID_FILE_MODE_REGEX = re.compile(r"^([wra]b?\+?)|x$")


def valid_mode(mode: Optional[str]) -> bool:
    return mode is not None and VALID_FILE_MODE_REGEX.fullmatch(mode)


def stderr(*objects, sep=' ', end='\n') -> None:
    print(*objects, sep=sep, end=end, file=sys.stderr)


def exit_error(message: str, before_exit: Optional[Union[str, Callable]] = None, code=2) -> None:
    """
    Helper for exiting with an error

    :param message:
    :param before_exit:
    :param code:
    :return:
    """
    stderr(f"ERROR: {message}")
    if help:
        stderr(help)

    if before_exit is not None:
        if callable(before_exit):
            before_exit()
        else:
            stderr(before_exit)

    sys.exit(code)


class StdOrFile:
    """
    A context manager that helps with input piping.

    If it is asked to open '-' as a file path, it attempts to use one of
    the following based on the mode string:

        * sys.stdin if 'r' is in the mode string
        * sys.stdout if 'w' is in the mode string

    This is somewhat like ``fileinput.FileInput`` in the standard
    library. Unlike FileInput, it allows opening in read mode and
    does not support any proxying of stream methods.

    The use of IOBase for typing is intentional in case some objects
    require a binary mode instead of a textmode.

    In some circumstances, it appears that stdin and stdout can be None.
    Most users probably won't encounter this.
    """
    def __init__(self, stream_or_path: PathLike, mode: str):
        raw = None
        self._using_filesystem_stream = False

        # Handle stdin/stdout requests
        if stream_or_path == '-':
            if 'r' in mode:
                raw = sys.stdin
            elif 'w' in mode:
                raw = sys.stdout

        # Attempt to open the requested path as a file system path
        elif isinstance(stream_or_path, (str, Path)):
            path = Path(stream_or_path).expanduser().resolve()
            raw = open(path, mode)
            self._using_filesystem_stream = True
        else:
            raise TypeError(
                f"Got {stream_or_path} for stream_or_path, but it must"
                f" be either '-' or a path in the form of a string or a Path")

        self._raw = raw

    @property
    def name(self) -> Optional[str]:
        """
        A filesystem path, or None when the stream is stdin & stdout.

        :return:
        """
        if self._using_filesystem_stream:
            return self._raw.name
        return None

    @property
    def raw(self) -> Optional[IOBase]:
        """
        The raw stream this object wraps.
        :return:
        """
        return self._raw

    def __enter__(self) -> "StdOrFile":
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Close the stream if it is not None and it is on the file system.

        :param exception_type:
        :param exception_value:
        :param exception_traceback:
        :return:
        """
        if self._raw is not None and self._using_filesystem_stream:
            self._raw.close()


LoadedType = TypeVar('LoadedType')
def load_binary_source(
    source: StreamOrPathLike,
    loader_func: Callable[[BinaryIO], LoadedType]
) -> LoadedType:
    """
    Attempt to get a binary stream and use it to call ``loader_func``

    This function is very opinionated and makes assumptions.

    ``loader_func`` should copy the data or transform it. This
    helps minimize unfinished context by closing files when no
    longer needed.

    It is assumed this will be used with raw built-in binary
    streams. Custom types should be handled in one of the following
    ways, ranked from best to worst:

        1. Pass their raw streams to this function
        2. Implement them as subclasses of the base streams
        3. Duck-type and ignore any typing warnings

    :param source: The object to get a binary stream for
    :param loader_func: A function that will process the stream's data.
    :return:
    """
    with ExitStack() as es:
        if isinstance(source, (str, Path)):
            raw_file = es.enter_context(open(source, "rb"))
        elif hasattr(source, 'mode') and 'rb' not in source.mode:
            raw_file = source.buffer
        else:
            raw_file = source
        result = loader_func(raw_file)

    return result


class OutputHelper:
    """
    Encapsulate common operations on output streams

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
    def __init__(
        self,
        stream: HasReadline,
        comment_prefix: str = '#',
    ):
        if not isinstance(stream, HasReadline):
            raise TypeError(f"Expected a stream with readline support, but got {stream}")
        elif isinstance(stream, HasTextReadline):
            self._stream = stream
        else:
            self._stream = TextIOWrapper(stream)

        self._comment_prefix = comment_prefix
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

    def readline(self, discard_comment_lines: bool = True) -> Union[str, bytes]:
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


def ensure_folder_exists(folder_path: PathLike) -> None:
    folder_path = Path(folder_path)
    folder_path.mkdir(exist_ok=True)


def absolute_path(path: Union[str, Path, bytes]) -> str:
    return str(Path(path).expanduser().resolve())


def guess_path_type(path: Optional[PathLike]) -> Optional[str]:

    if path is None:
        return None

    path = Path(path)

    if not path.suffix:
        if path.is_dir():
            return "spritedir"
        else:
            return None

    return path.suffix[1:]


def get_stream_filesystem_path(stream: Any) -> Optional[str]:
    """
    Attempt to return a string path for stream's underlying path

    Returns None If the stream is stdin, stdout, or stderr. Although
    these may have file system representations on unix-like systems,
    those representations are not in scope for this tool.

    Otherwise, a series of names will be tried to resolve a file system
    path. For objects that have a ``raw`` attribute, that value will be
    used as the attribute resolution stream instead.

    :param stream: The stream to get a filesystem path for.
    :return:
    """
    if stream in (sys.stdin, sys.stdout, sys.stderr):
        return None

    # Get the wrapped stream if the stream is a wrapper object
    target = getattr(stream, 'raw', None) or stream

    # If there is a non-None name, resolve it into an absolute path
    name = value_of_first_attribute_present(
        target, ('file', 'path', 'name', 'filename'), missing_ok=True)
    name = name() if callable(name) else name
    path = None if name is None else absolute_path(name)

    return path


def get_source_filesystem_path(source: StreamOrPathLike):
    if isinstance(source, (str, Path, bytes)):
        return absolute_path(source)
    return get_stream_filesystem_path(source)


class SeekableBinaryFileCopy(BytesIO):
    """
    Copy file streams into a seekable form, preserving mode and filename

    Intended to be used in places where data must be repeatedly queried,
    such as PILFont queries and no-disk caching modes.
    """
    def __init__(
        self,
        source: Union[bytes, BinaryIO],
        source_path: Optional[PathLike] = None,
        mode: Optional[str] = None
    ):
        if mode is not None and VALID_FILE_MODE_REGEX.fullmatch(mode) is None:
            raise ValueError(f"Invalid file opening mode {mode}")

        # Handle the source as a stream
        if hasattr(source, 'read'):
            # allow forcing of modes on files
            if 'b' in source.mode:
                bin_stream = source
            else:
                bin_stream = source.buffer
            data = bin_stream.read()
            mode = mode or bin_stream.mode
        # Treat it as a readable and writable binary file
        else:
            data = source
            mode = mode or 'rb+'

        super(SeekableBinaryFileCopy, self).__init__(data)

        fetched_path = source_path or get_stream_filesystem_path(source)
        self.filename = Path(fetched_path) if fetched_path else None
        self._mode = mode

        # Return to the start of the stream
        self.seek(0)

    @property
    def mode(self) -> str:
        return self._mode

    @classmethod
    def copy(cls, source: StreamOrPathLike) -> "SeekableBinaryFileCopy":
        """
        Return a seekable copy of the original binary data.

        This is convenient for files that may need to be accessed multiple
        times, such as PIL fonts.

        :param source:
        :return:
        """
        copy = load_binary_source(source, lambda s: cls(s))
        return copy


def looks_like_stream_with_read_support(
        obj: Any,
        required_attributes: Iterable[str] = ('read', 'readline'),
        error_on_missing: bool = False
) -> bool:
    """
    True if the given stream has all the required attributes to be readable

    Checking if the attributes are callable ensures that
    :param obj:
    :param required_attributes:
    :return:
    """
    return has_all_methods(obj, required_attributes)
