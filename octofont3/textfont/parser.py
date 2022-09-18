from collections import defaultdict
from fileinput import FileInput
from typing import Optional, List, Tuple, Union

from PIL import Image

from octofont3.custom_types import BoundingBox, Size
from octofont3.iohelpers import TextIOBaseSubclass
from octofont3.textfont import FONT_HEADER, GLYPH_HEADER


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


class TextFontFile:
    """
    A font-like class for parsing human-editable TextFonts.

    It implements some ImageFont functionality as well as bits of
    FreeTypeFont's API such as the size property.

    Advanced options are not supported at present. Only the following
    are currently supported:

      * left-to-right text
      * single lines for functions
    """

    def _parse_glyph(
        self,
        stream: Union[TextIOBaseSubclass, FileInput],
        max_width: int = 8,
        height: int = 8,
        empty_char: str = ".",
        full_char: str = "X"
    ) -> Image:
        """
        Parse a single glyph from the stream.

        The actual with of the glyph will be set by the first line of
        input for the glyph.

        :param stream: the source stream to read from
        :param max_width: Maximum expected width; overriden by 1st line
        :param height: How many lines tall the glyph is expected to be.
        :param empty_char: What counts as an empty pixel.
        :param full_char: What counts as a filled pixel.
        :return:
        """

        # Get first line & set row length expectations from it
        raw_font_data = [stream.readline().rstrip()]
        expected_width = len(raw_font_data[0])

        # Extract the raw image data, raising an error if needed
        for row_index in range(height - 1):
            raw_line = stream.readline().rstrip()
            if len(raw_line) != expected_width:
                raise FontParseError.from_stream_state(
                    f"Mismatched line length: expected line of length,"
                    f" {expected_width}, but got {raw_line!r}",
                    stream
                )
            for char in raw_line:
                if char not in (full_char, empty_char):
                    raise FontParseError.from_stream_state(
                        f"Unexpected character: {char!r}",
                        stream
                    )
            raw_font_data.append(raw_line)

        # Create a zeroed buffer of the needed length
        data_buffer = bytearray(max_width * height)

        # Convert the parsed row data and fill the buffer with it
        for row_index, row in enumerate(raw_font_data):
            start_index = row_index * max_width
            end_index = start_index + len(raw_font_data[row_index])
            data_buffer[start_index:end_index] = map(
                lambda c: 255 if c == full_char else 0, row)

        # Create a greyscale version of the glyph data
        image = Image.frombytes("L", (max_width, height), bytes(data_buffer))
        # Convert the glyph into a 1-bit mask expected
        # by pillow for binary font drawing.
        return image.convert("1").im

    def _parse_textfont_file(self, stream: Union[TextIOBaseSubclass, FileInput]) -> None:
        """

        Extract all glyphs to the internal table from the stream

        :param stream: The stream object to use as a source
        :return:
        """
        # Not currently used, but nice to have for debugging
        file_header, bounds = parse_header_and_values(stream, FONT_HEADER)
        self.max_width, self.max_height = bounds

        # Temp local variables for faster access
        glyph_table = self.glyph

        # Parse each glyph in the file & update internal storage
        while glyph_header := parse_header_and_values(stream, GLYPH_HEADER):
            code_point, glyph_width, glyph_height = glyph_header[1]

            glyph_table[code_point] = self._parse_glyph(
                stream, max_width=glyph_width, height=glyph_height)

    def __init__(self, file_stream: Optional[Union[FileInput, TextIOBaseSubclass]] = None, kerning: int = 1):
        super().__init__()

        # Partially backward compatible glyph table, theoretically
        # supporting more than the original boring 255 characters.
        self.glyph: defaultdict[int, Optional[Image.Image]] = defaultdict(lambda: None)

        # these should really be recalculated from the font itself instead of the header
        self.max_width: Optional[int] = None
        self.max_height: Optional[int] = None

        # expected in octo emissions
        first_glyph: Optional[int] = None
        last_glyph: Optional[int] = None

        # imitate the FreeType point size property
        self._size: Optional[int] = None

        # ugly 1 pixel flat kerning option to start with, should ideally be a dict
        self.kerning: int = kerning

        if file_stream:
            self._parse_textfont_file(file_stream)

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
        for char_index, char_code in enumerate(map(ord, text)):
            char_image = self.glyph[char_code]
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
        size = self.getsize(text)
        mask_image = Image.new("1", size)

        current_x, current_y = 0, 0
        for char_code in map(ord, text):
            char_image = self.glyph[char_code]
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

    except FontParseError as e:
        print(f"ERROR: Bad font: {e!r}")
        exit(1)

    image_size = text_font_file.getsize(test_text)
    image = Image.new("RGB", image_size)

    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    draw.text((0,0), test_text, font=text_font_file)
    image.show()
