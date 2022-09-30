from ast import literal_eval
from fileinput import FileInput
from io import TextIOBase
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image

from octofont3.custom_types import BoundingBox, Size, PathLike
from octofont3.formats.textfont import TEXTFONT_GLYPH_HEADER
from octofont3.iohelpers import InputHelper, header_regex, strip_end_comments_and_space
from octofont3.utils import empty_core, find_max_dimensions, generate_missing_character_core, get_stream_file


class TextFontParseError(BaseException):

    def __init__(self, message: str, filename: str, lineno: int):
        super().__init__(f"{filename}, line {lineno}: {message}")
        self.raw_message = message
        self.filename = filename
        self.lineno = lineno

    @classmethod
    def from_stream_state(cls, message, stream):
        return cls(message, get_stream_file(stream), stream.lineno())



class TextFontFile:
    """
    PIL-compatible reader for a human-editable text-based font format

    You can use it with pillow's ImageDraw functions.

    Advanced options are not supported at present. It has the following
    restrictions:

      * Left-to-right text only
      * For drawing, only single lines of text are currently allowed

    """

    # Use regexes for now because metaclasses are overkill for this format
    glyph_header_regex = header_regex(TEXTFONT_GLYPH_HEADER, glyph=str)

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

    def load_textfont_file(
        self,
        file: Union[PathLike, TextIOBase, FileInput, InputHelper],
    ) -> None:
        """
        Load all glyphs in the file to the internal glyph table.

        You can use FileInput objects to merge multiple TextFont files
        into one.

        :param file: A file to open or a stream to use as a source
        :return:
        """
        file_to_close_at_end = None

        # Make sure we have a stream & convert it to an InputHelper
        if isinstance(file, (Path, str)):
            file_to_close_at_end = open(file, 'r')
            stream = InputHelper(file_to_close_at_end)
            self.filename = str(file)
        elif isinstance(file, InputHelper):
            stream = file
        else:
            stream = InputHelper(file)

        if not self.filename:
            self.filename = get_stream_file(file)

        # Temp local variable for readability
        glyph_table = self.glyph

        # Parse each glyph in the file & update internal storage
        line = True
        try:
            while line:
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

        finally:
            if file_to_close_at_end:
                file_to_close_at_end.close()

        # Update local metadata & helpers
        self.max_width, self.max_height = find_max_dimensions(self, self.provided_glyphs)
        self.dummy_glyph = generate_missing_character_core((self.max_width, self.max_height))

    def __init__(
        self,
        file: Optional[Union[PathLike, FileInput, TextIOBase]] = None,
        allow_duplicates: bool = True,
        kerning: int = 0,
        max_allowed_glyph_size: Size = (64, 64),
        empty_char: str = '.',
        full_char: str = 'X',
    ):
        """
        Create a TextFontFile object that can load Textfonts.

        It has an internal glyph table that accepts arbitrary strings as
        keys. This allows loading and storing unicode characters.

        The default loading behavior is to allow duplicates in the
        input. This makes it easier to override the files if a
        FileInput or series of files are loaded.

        :param file: A file to load TextFonts from.
        :param allow_duplicates: Whether to allow duplicates in the
                                 input stream.
        :param kerning: How many pixels to put after each character
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

        # Dictionary glyph table that allows support for multi-byte
        # sequences and unicode.
        self.glyph: Dict[str, Optional[Image.Image]] = {}
        self.filename: Optional[str] = None

        self.kerning: int = kerning

        # These will be set by loading font data
        self.max_width: int = 0
        self.max_height: int = 0
        self.dummy_glyph = empty_core(0,0)

        # Imitate the FreeType point size property
        self._size: Optional[int] = None

        if file:
            self.load_textfont_file(file)

    @property
    def provided_glyphs(self) -> Tuple[str, ...]:
        """
        A tuple of the glyphs provided
        :return:
        """
        return tuple(self.glyph.keys())

    def get_glyph(self, value, strict=False):

        if value in self.glyph:
            return self.glyph[value]
        elif not strict:
            return self.dummy_glyph
        raise KeyError(f"Could not find glyph data for sequence {value!r}")

    @property
    def size(self) -> Optional[int]:
        """
        Imitate the size property of the original ImageFont font object.

        This can return None for the time being because pillow does not
        provide a way to recover that data from a pilfont, and there is
        no way to indicate that in a TextFont at present.

        It may be implemented in the future.

        :return:
        """
        return self._size

    def getsize(self, text: str) -> Size:
        """
        Return the bounding box of a given piece of text as a tuple.

        For binary fonts, this seems to treat each tile as its own entry.
        :param text:
        :return:
        """
        total_width = 0
        total_height = 0

        end_index = len(text) - 1
        for char_index, char_code in enumerate(text):

            char_image = self.get_glyph(text)

            width, height = char_image.size

            total_height = max(total_height, height)
            total_width += width

            if char_index < end_index:
                total_width += self.kerning

        return total_width, total_height

    def getmask(self, text: str):
        """
        Get a 1-bit imaging core object to use as a drawing mask.

        Crucial for drawing text.

        :param text:
        :return:
        """
        #if len(text) == 1:
        #    return self.glyph[text]

        size = self.getsize(text)
        mask_image = Image.new("1", size)

        current_x, current_y = 0, 0
        for char in text:
            char_image = self.get_glyph(char)
            width, height = char_image.size

            mask_image.paste(
                char_image,
                (current_x, current_y, current_x + width, current_y + height))
            current_x += width
            current_x += self.kerning

        return mask_image.im

    def getbbox(self, text: str) -> BoundingBox:
        width, height = self.getsize(text)
        return 0, 0, width, height


if __name__ == "__main__":
    import sys
    name, *argv = sys.argv

    if len(argv) != 2:
        print(f"ERROR: usage is {name} \"Text to print\" textfont/file/path.txt")
        exit(1)

    test_text, file_path = argv
    text_font_file = None

    try:
        file_input = FileInput(files=argv[1])
        text_font_file = TextFontFile(file_input)

    except TextFontParseError as e:
        print(f"ERROR: Bad font: {e!r}")
        exit(1)

    image_size = text_font_file.getsize(test_text)
    image = Image.new("RGB", image_size)

    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    draw.text((0,0), test_text, font=text_font_file)
    image.show()
