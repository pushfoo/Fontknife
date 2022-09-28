from ast import literal_eval
from fileinput import FileInput
from typing import Optional, Union, Dict

from PIL import Image

from octofont3.custom_types import BoundingBox, Size, PathLike, TextIOBaseSubclass
from octofont3.iohelpers import InputHelper, header_regex, strip_end_comments_and_space
from octofont3.formats.textfont import TEXTFONT_FILE_HEADER, TEXTFONT_GLYPH_HEADER
from octofont3.utils import get_stream_file, empty_core, generate_missing_character_core, find_max_dimensions


class TextFontParseError(BaseException):

    def __init__(self, message, filename: str, lineno: int):
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
      * Only single lines of text are currently allowed

    """

    # Use regexes for now because metaclasses are overkill for this format
    textfont_header_regex = header_regex(TEXTFONT_FILE_HEADER)
    glyph_header_regex = header_regex(TEXTFONT_GLYPH_HEADER, glyph=str)

    def _read_glyph_pixels(
        self,
        stream: Union[TextIOBaseSubclass, FileInput],
        glyph: str,
        max_parsable_size: Size,
        empty_char: str = ".",
        full_char: str = "X",
    ):
        max_width, max_height = max_parsable_size
        acceptable_chars = (empty_char, full_char)

        y_index = 0
        glyph_width = None
        raw_glyph_lines = []

        while True:

            # End of file, abandon parsing
            raw_line = stream.readline()
            if not raw_line:
                break

            # Get clean data minus end comments
            line = strip_end_comments_and_space(stream.peekline())
            line_len = len(line)

            # Set a width from the first line
            if glyph_width is None:
                glyph_width = line_len

            # Break on end of file and lines starting with non-data chars
            elif not line or line[0] not in acceptable_chars:
                break

            elif line_len != glyph_width:
                raise TextFontParseError.from_stream_state(f"Mismatched line length", stream)

            elif line_len > max_width:
                raise TextFontParseError.from_stream_state(
                    f"Glyph {repr(glyph)} exceeds specified maximum width ({line_len + 1} > {max_width})",
                    stream)

            elif y_index > max_height:
                raise TextFontParseError.from_stream_state(
                    f"Glyph {repr(glyph)} exceeds specified maximum height ({y_index + 1} > {max_height})",
                    stream)

            for char in line:
                if char not in acceptable_chars:
                    raise TextFontParseError.from_stream_state(
                        f"Unexpected character: {char!r}", stream)

            raw_glyph_lines.append(line)
            y_index += 1

        return raw_glyph_lines

    def _parse_glyph(
        self,
        stream: Union[TextIOBaseSubclass, FileInput],
        glyph: str,
        max_parsable_size: Size,
        empty_char: str = ".",
        full_char: str = "X",
    ) -> Image:
        """
        Parse a single glyph from the stream & convert its pixel data

        :param stream: the source stream to read from
        :param empty_char: What character counts as an empty pixel.
        :param full_char: What character counts as a filled pixel.
        :param max_parsable_size: Maximum allowed dimensions for parsing.
        :return: A pillow image core
        """
        # Get line data
        glyph_data = self._read_glyph_pixels(
            stream, glyph, max_parsable_size, empty_char=empty_char, full_char=full_char)

        # Calculate image data dimensions
        glyph_height = len(glyph_data)
        if glyph_height:
            glyph_width = len(glyph_data[0])
        else:
            glyph_width = 0
        glyph_size = glyph_width, glyph_height

        # Handle anomalous glyph data by returning early
        if glyph_size == (0, 0):
            return empty_core(0, 0)

        # Create a zeroed buffer of the needed length
        data_buffer = bytearray(glyph_width * glyph_height)

        # Convert the parsed row data and fill the buffer with it
        for row_index, row in enumerate(glyph_data):
            start_index = row_index * glyph_width
            end_index = start_index + glyph_width
            data_buffer[start_index:end_index] = map(
                lambda c: 255 if c == full_char else 0, row)

        # Create a greyscale version of the glyph data
        image = Image.frombytes("L", glyph_size, bytes(data_buffer))
        # Convert the glyph into a 1-bit mask expected
        # by pillow for binary font drawing.
        return image.convert("1").im

    def _parse_textfont_file(
        self,
        stream: Union[TextIOBaseSubclass, FileInput],
        max_parsable_size: Size
    ) -> None:
        """

        Extract all glyphs to the internal table from the stream

        :param stream: The stream object to use as a source
        :return:
        """
        stream = InputHelper(stream)

        line = stream.readline()
        match = self.textfont_header_regex.match(line)
        if not match:
            raise TextFontParseError.from_stream_state(
                f"Malformed Textfont header, expected \"{TEXTFONT_FILE_HEADER}:\", but got {line!r}", stream)

        # Temp local variables for faster access
        glyph_table = self.glyph

        # Parse each glyph in the file & update internal storage
        line = True
        while line:

            line = stream.peekline()
            if not line:
                break

            match = self.glyph_header_regex.match(line)
            if match is None:
                raise TextFontParseError.from_stream_state("Malformed glyph header", stream)

            groups = match.groupdict()
            glyph = literal_eval(groups['glyph'])
            glyph_table[glyph] = self._parse_glyph(stream, glyph, max_parsable_size)

        pass

    def __init__(
        self,
        file_stream: Optional[Union[PathLike, FileInput, TextIOBaseSubclass]] = None,
        kerning: int = 0,
        max_parsable_glyph_size: Size = (64, 64)
    ):
        super().__init__()

        # Dictionary glyph table that allows support for multi-byte
        # sequences and unicode.
        self.glyph: Dict[str, Optional[Image.Image]] = {}
        self.filename = get_stream_file(file_stream)

        # these should really be recalculated from the font itself instead of the header
        self.max_width: Optional[int] = None
        self.max_height: Optional[int] = None

        # imitate the FreeType point size property
        self._size: Optional[int] = None

        # ugly 1 pixel flat kerning option to start with, should ideally be a dict
        self.kerning: int = kerning

        if file_stream:
            self._parse_textfont_file(file_stream, max_parsable_glyph_size)
        self.max_width, self.max_height = find_max_dimensions(self, self.provided_glyphs)
        self.dummy_glyph = generate_missing_character_core((self.max_width, self.max_height))

    @property
    def provided_glyphs(self):
        return tuple(self.glyph.keys())

    def get_glyph(self, value, strict=False):

        if value in self.glyph:
            return self.glyph[value]
        elif not strict:
            return self.dummy_glyph
        raise KeyError(f"Could not find glyph data for sequence {value!r}")

    @property
    def size(self) -> int:
        """
        Imitate the size property of the original

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

        Crucial for
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
