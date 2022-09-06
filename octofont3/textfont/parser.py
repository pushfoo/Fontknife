from fileinput import FileInput
from io import TextIOBase
from typing import Optional, List, Tuple, TypeVar

from octofont3.textfont import FONT_HEADER, GLYPH_HEADER
from octofont3 import FontData


class FontParseError(BaseException):

    def __init__(self, message, filename: str, lineno: int):
        super().__init__(f"{filename}, line {lineno}: {message}")
        self.raw_message = message
        self.filename = filename
        self.lineno = lineno

    @classmethod
    def from_stream_state(cls, message, stream):
        return cls(message, stream.filename(), stream.lineno())


def split_tokens(line: str) -> Optional[List[str]]:

    if line == '':
        return None

    return line.rstrip().split(' ')


def strip_end_comments(line: str) -> str:
    comment_start_index = line.find("#")

    if comment_start_index < 0:
        return line

    return line[:comment_start_index]


def readline_and_split(stream, skip_comment_lines=True) -> Optional[List[str]]:

    if skip_comment_lines:
        raw_line = "#"
        while raw_line and (raw_line.startswith("#") or raw_line[0] == "\n"):
            raw_line = stream.readline()
    else:
        raw_line = stream.readline()
    line = strip_end_comments(raw_line)

    return split_tokens(line)


def parse_header_and_values(stream, expected_header: str = None) -> Optional[Tuple[str, Tuple[int, ...]]]:
    """
    Return None if empty line, otherwise a string + ints after it

    :param stream:
    :param expected_header:
    :return:
    """
    values = readline_and_split(stream)

    # exit early because we reached the end of the file
    if values is None:
        return None

    header = values[0]

    if expected_header is not None and header != f"{expected_header}:":
        raise FontParseError.from_stream_state(
            f"Expected header {expected_header}, but got {header}", stream
        )

    int_values = tuple(map(int, values[1:]))
    return header, int_values


def parse_glyph(stream: FileInput, glyph_width, glyph_height):
    """

    Extract the data for this glyph from the font

    :param stream: a FileInput-like object that provides filename() and lineno()
    :param glyph_width:
    :param glyph_height:
    :return:
    """
    raw_font_data = []

    for i in range(glyph_height):
        row_chars = stream.readline().rstrip()
        row_len = len(row_chars)
        if row_len != glyph_width:
            raise FontParseError.from_stream_state(
                f"Expected glyph row of width {glyph_width}, but got {row_len}",
                stream
            )
        raw_font_data.append(row_chars)

    return ''.join(raw_font_data)


def parse_textfont_file(stream) -> FontData:
    file_header, bounds = parse_header_and_values(stream, FONT_HEADER)

    font_data = FontData(*bounds)

    first_glyph = 255
    last_glyph = 0

    while glyph_header := parse_header_and_values(stream, GLYPH_HEADER):
        ascii_code, glyph_width, glyph_height = glyph_header[1]
        font_data.glyphs[ascii_code] = parse_glyph(stream, glyph_width, glyph_height)

        first_glyph = min(ascii_code, first_glyph)
        last_glyph = max(ascii_code, last_glyph)

    font_data.first_glyph = first_glyph
    font_data.last_glyph = last_glyph

    return font_data


S = TypeVar("S", bound=TextIOBase)
