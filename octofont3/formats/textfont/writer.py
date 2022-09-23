from typing import Iterable

from octofont3.font_adapter import CachingFontAdapter
from octofont3.iohelpers import OutputHelper, TextIOBaseSubclass
from octofont3.utils import print_dataclass_info, find_max_dimensions


class TextfontStream(OutputHelper):

    def __init__(self, stream):
        super().__init__(stream)

    def header(self, header: str, *objects, sep=" ", end="\n"):
        self.print(f"{header}: ", end="")
        self.print(*objects, sep=sep, end=end)


class FontRenderer:

    def __init__(
        self,
        stream: TextIOBaseSubclass,
        include_padding: bool = True,
        verbose: int = 0,
        fill_character: str = 'X',
        empty_character: str = '.',
    ):
        if not isinstance(stream, TextfontStream):
            stream = TextfontStream(stream)

        self.fill_character = fill_character
        self.empty_character = empty_character
        self.stream = stream
        self.include_padding: bool = include_padding
        self.verbose = verbose

    def emit_character(self, font: CachingFontAdapter, glyph):

        bitmap = font.getmask(glyph)
        metadata = font.get_glyph_metadata(glyph)
        glyph_bbox = metadata.glyph_bbox
        bitmap_bbox = metadata.bitmap_bbox

        comment = [f"# {glyph} (ASCII: {ord(glyph)})"]

        if bitmap_bbox is None:
            self.stream.print(comment[0], "skipping empty glyph")

        padding_above = glyph_bbox.top

        if bitmap_bbox is not None:
            data_width, data_height = bitmap_bbox[2:]
        else:
            data_width, data_height = 0, 0
        padding_below = glyph_bbox.bottom - (padding_above + data_height)

        if bitmap_bbox is not None:
            self.stream.header("GLYPH", ord(glyph), data_width, data_height, ''.join(comment))

        if self.verbose:
            print(f"# metadata:")
            print_dataclass_info(metadata)
            # print()

        if bitmap_bbox is None:
            return

        pad_line = self.empty_character * glyph_bbox.width

        for i in range(padding_above):
            self.stream.print(pad_line)

        line_raw = []
        for y in range(data_height):
            line_raw.clear()
            for x in range(data_width):
                #print("bitmap_bbox coord: ", x, y, file=sys.stderr)
                line_raw.append(self.fill_character if bitmap.getpixel((x, y)) > 0 else self.empty_character)

            line_raw.extend((self.empty_character for i in range(glyph_bbox.width - data_width)))
            self.stream.print(''.join(line_raw))

        for i in range(padding_below):
            self.stream.print(pad_line)

    def emit_textfont(self, font: CachingFontAdapter, glyph_sequence: Iterable[str]):
        s = self.stream
        max_width, max_height = find_max_dimensions(font, glyph_sequence)
        s.comment(f"{font.path}, {font.size} points, height {max_height} px, widest {max_width} px")
        s.comment(f"Exporting: {glyph_sequence}")
        s.header("FONT", max_width, max_height)

        for glyph in glyph_sequence:
            self.emit_character(font, glyph)
