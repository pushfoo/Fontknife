from ast import literal_eval
from contextlib import ExitStack
from pathlib import Path
from typing import Union, Optional, Iterable, List

from PIL import Image

from fontknife.custom_types import PathLike, HasRead, HasReadline, Size
from fontknife.formats.common.raster_font import GlyphMaskMapping
from fontknife.formats import RasterFont
from fontknife.formats.common import FormatReader
from fontknife.formats.common.textfont import GLYPH_HEADER, FULL_PIXEL, EMPTY_PIXEL
from fontknife.iohelpers import StdOrFile, get_resource_filesystem_path, header_regex, InputHelper, \
    strip_end_comments_and_space
from fontknife.utils import empty_core


class TextFontParseError(BaseException):

    def __init__(self, message: str, filename: str, lineno: int):
        super().__init__(f"{filename}, line {lineno}: {message}")
        self.raw_message = message
        self.filename = filename
        self.lineno = lineno

    @classmethod
    def from_stream_state(cls, message, stream):
        return cls(message, get_resource_filesystem_path(stream), stream.lineno())


class TextFontParser:
    """
    PIL-compatible parser for a human-editable text-based font format

    You can use it with pillow's ImageDraw functions.

    Advanced options are not supported at present. It has the following
    restrictions:

      * Left-to-right text only
      * For drawing, only single lines of text are currently allowed

    """

    # Use regexes for now because metaclasses are overkill for this format
    glyph_header_regex = header_regex(GLYPH_HEADER, glyph=str)

    def _read_glyph_raw_pixels(
        self,
        stream: InputHelper,
        glyph: str,
    ) -> List[str]:
        """
        Return a list of validated pixel rows for the current glyph

        The first line is used to determine the expected width of the
        data block. Whitespace and comments will be stripped from the
        end of the line before processing it.

        This method raises an exception if the stripped line meets any
        of the following conditions:

            * It contains invalid characters
            * It is wider than the maximum allowed line length
            * Its length does not match that of the first line
            * It would make the glyph taller than the maximum allowed
              height

        :param stream: The stream-like object to read from
        :param glyph: the glyph string
        :return: A list of validated lines
        """
        max_valid_width, max_valid_height = self._max_allowed_glyph_size

        y_index = 0
        glyph_width = None
        raw_glyph_lines = []

        while True:
            raw_line = stream.peekline()

            # Abandon parsing on end of pixel data or file
            if not raw_line or raw_line[0] not in self._allowed_pixel_chars:
                break

            # Clean the pixel data of any whitespace & comments
            pixel_row = strip_end_comments_and_space(raw_line)
            pixel_row_len = len(pixel_row)

            if pixel_row_len != glyph_width:
                if glyph_width is None:
                    glyph_width = pixel_row_len

                elif pixel_row_len > max_valid_width:
                    raise TextFontParseError.from_stream_state(
                        f"Glyph {repr(glyph)} exceeds specified maximum width "
                        f"({pixel_row_len + 1} > {max_valid_width})",
                        stream)
                else:
                    raise TextFontParseError.from_stream_state(
                        f"Glyph: {glyph!r}: Mismatched line length", stream)

            elif y_index >= max_valid_height:
                raise TextFontParseError.from_stream_state(
                    f"Glyph {repr(glyph)} exceeds specified maximum height ({y_index + 1} > {max_valid_height})",
                    stream)

            for pixel_char in pixel_row:
                if pixel_char not in self._allowed_pixel_chars:
                    raise TextFontParseError.from_stream_state(
                        f"Unexpected character: {pixel_char!r}", stream)

            # Load the next line into peekability
            raw_glyph_lines.append(pixel_row)
            y_index += 1
            stream.readline()

        return raw_glyph_lines

    def _parse_glyph(
        self,
        stream: InputHelper,
        glyph: str,
    ) -> Image:
        """
        Parse a single glyph from the stream & return its pixel data

        The pixel data will be returned as an image core object.

        :param stream: the source stream to read from
        :param glyph: the glyph string the data will be for
        :return: A pillow image core
        """
        # Get line data
        glyph_data = self._read_glyph_raw_pixels(stream, glyph)

        # Calculate image data dimensions
        glyph_height = len(glyph_data)
        if glyph_height:
            glyph_width = len(glyph_data[0])
        else:
            glyph_width = 0
        glyph_size = glyph_width, glyph_height

        # Exit early on anomalous glyph data
        if glyph_size == (0, 0):
            return empty_core(0, 0)

        # Create a zeroed buffer of the needed length
        data_buffer = bytearray(glyph_width * glyph_height)

        # Convert the parsed row data and fill the buffer with it
        for row_index, pixel_row in enumerate(glyph_data):
            start_index = row_index * glyph_width
            end_index = start_index + glyph_width
            data_buffer[start_index:end_index] = map(
                lambda c: 255 * int(c == self._full_char), pixel_row)

        # Create a greyscale version of the glyph data
        image = Image.frombytes("L", glyph_size, bytes(data_buffer))
        # Return a 1-bit mask expected by font drawing
        return image.convert("1").im

    def parse(
        self,
        source: HasReadline[str]
    ) -> GlyphMaskMapping:
        """
        Load all glyphs in the file to the internal glyph table.

        You can use FileInput objects to merge multiple TextFont files
        into one.

        :param source: A file to open or a stream to use as a source
        :return:
        """
        if not source:
            raise TypeError('Got {file}, but file must be a path stream-like object')

        glyph_table: GlyphMaskMapping = {}

        # Set up a context to clean up any files opened
        with ExitStack() as close_at_end:
            # Open any raw path as a stream the context will close afterward
            if isinstance(source, (Path, str)):
                temp_stream = close_at_end.enter_context(open(source, 'r'))
                stream = InputHelper(temp_stream)

            # Handle pre-existing input helpers and streams
            elif isinstance(source, InputHelper):
                stream = source
            else:
                stream = InputHelper(source)

            # Dictionary that will be returned

            # Parse each glyph in the file & update internal storage
            while True:
                # Assumes the InputHelper already skipped comments
                line = stream.peekline()

                # Stop iteration at end of file
                if not line:
                    break

                match = self.glyph_header_regex.match(line)
                if match is None:
                    raise TextFontParseError.from_stream_state("Malformed glyph header", stream)

                groups = match.groupdict()
                glyph = literal_eval(groups['glyph'])

                if not self.allow_duplicates and glyph in glyph_table:
                    raise TextFontParseError.from_stream_state(f"Glyph already in font table {glyph!r}", stream)

                # Discard the header line and parse the pixel data
                stream.readline()
                glyph_table[glyph] = self._parse_glyph(stream, glyph)

        return glyph_table

    def __init__(
        self,
        allow_duplicates: bool = True,
        max_allowed_glyph_size: Size = (64, 64),
        empty_char: str = EMPTY_PIXEL,
        full_char: str = FULL_PIXEL,
    ):
        """
        Create a TextFontParser object that can load Textfonts.

        Loading returns a dict of glyphs.

        The default loading behavior is to allow duplicates in the
        input. This makes it easier to override the files if a
        series of files are loaded.

        :param allow_duplicates: Whether to allow duplicates in the
                                 input stream.
        :param max_allowed_glyph_size: Maximum glyph width and height
        :param empty_char: What character counts as a blank pixel
        :param full_char: What character counts as a filled pixel
        """
        super().__init__()
        self._empty_char = empty_char
        self._full_char = full_char
        self._allowed_pixel_chars = frozenset((empty_char, full_char))
        self._max_allowed_glyph_size = max_allowed_glyph_size
        self.allow_duplicates: bool = allow_duplicates


class TextFontReader(FormatReader):
    wrapped_creation_func = TextFontParser

    def load_source(
        self, source: Union[PathLike, HasRead],
        **kwargs
    ) -> RasterFont:
        parser = TextFontParser()

        with StdOrFile(source, 'r') as file:
            raw_data = parser.parse(file.raw)

        path = get_resource_filesystem_path(source)
        font = RasterFont(glyph_table=raw_data, path=path)

        return font