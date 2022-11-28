import json
from collections import deque
from typing import Iterable, Optional, Any

from fontknife.custom_types import PathLike, HasWrite, PathLikeOrHasWrite
from fontknife.formats import RasterFont
from fontknife.formats.common import FormatWriter
from fontknife.formats.common.textfont import GLYPH_HEADER, COMMENT_PREFIX, FULL_PIXEL, EMPTY_PIXEL
from fontknife.iohelpers import OutputHelper, StdOrFile
from fontknife.utils import print_dataclass_info, find_max_dimensions


class TextFontStream(OutputHelper):

    def __init__(self, stream):
        super().__init__(stream)
        self._comment_field_queue = deque()
        self._max_field_label_len: int = 0

    def header(self, header: str, *objects, sep=" ", end="\n"):
        self.print(f"{header}:", *objects, sep=sep, end=end)

    def queue_comment_field(self, label: Any, value: Any):
        self._comment_field_queue.append((str(label), str(value)))
        self._max_field_label_len = max(len(label), self._max_field_label_len)

    def write_comment_field_block(self, sep=" : "):
        """
        Write the queued fields, with the separating
        :return:
        """
        while self._comment_field_queue:
            label, value = self._comment_field_queue.popleft()
            self.comment(label.ljust(self._max_field_label_len), value, sep=sep)
        self._max_field_label_len = 0


class FontRenderer:

    def __init__(
        self,
        stream: HasWrite[str],
        include_padding: bool = True,
        verbose: int = 0,
        fill_character: str = FULL_PIXEL,
        empty_character: str = EMPTY_PIXEL,
    ):
        if not isinstance(stream, TextFontStream):
            stream = TextFontStream(stream)

        self.fill_character = fill_character
        self.empty_character = empty_character
        self.stream = stream
        self.include_padding: bool = include_padding
        self.verbose = verbose

    def emit_character(self, font: RasterFont, glyph: str, comment_raw_glyph: bool = True):

        # Fetch some useful data as locals
        bitmap = font.getmask(glyph)
        metadata = font.get_glyph_metadata(glyph)
        glyph_bbox = metadata.glyph_bbox
        glyph_width, glyph_height = glyph_bbox.size
        bitmap_bbox = metadata.bitmap_bbox
        stream = self.stream

        # Emit the header using an easy to parse format
        end = ' ' if comment_raw_glyph else '\n'
        stream.header(GLYPH_HEADER, json.dumps(glyph), end=end)
        if comment_raw_glyph:
            if glyph == '"':
                quote = "'"
            else:
                quote = '"'
            stream.comment(f"Raw glyph: {quote}{glyph}{quote}")

        # Get dimensions for the glyph with padding and the raw data inside
        if bitmap_bbox is None:
            data_width, data_height = 0, 0
        else:
            data_width, data_height = bitmap_bbox[2:]

        glyph_right = glyph_bbox.right
        if glyph_right < 1:
            stream.comment(f"WARNING! Glyph with abnormal width: {glyph_right}")

        if self.verbose:
            print_dataclass_info(metadata)
        else:
            stream.comment(f"Glyph Size : {glyph_width, glyph_height}")
            stream.comment(f"Data Size  : {data_width, data_height}")

        # Calculate padding values and output padding
        px_empty = self.empty_character
        px_full = self.fill_character
        padding_above = glyph_bbox.top
        padding_below = glyph_bbox.bottom - (padding_above + data_height)
        pad_left = glyph_bbox.left
        pad_right = glyph_right - (pad_left + data_width)
        full_width_padding_line = self.empty_character * glyph_width

        for i in range(padding_above):
            self.stream.print(full_width_padding_line)

        line_raw = []
        for y in range(data_height):
            line_raw.clear()
            line_raw.extend(px_empty * pad_left)
            for x in range(data_width):
                pixel = bitmap.getpixel((x, y))
                line_raw.append(px_full if pixel > 0 else px_empty)

            line_raw.extend(px_empty * pad_right)
            self.stream.print(''.join(line_raw))

        for i in range(padding_below):
            self.stream.print(full_width_padding_line)

    def emit_textfont(
        self,
        font: RasterFont,
        glyph_sequence: Iterable[str] = None,
        actual_source_path: Optional[PathLike] = None,
        max_line_width: int = 80
    ) -> None:
        s = self.stream

        # If not sequence specified, use whatever glyphs the font has, in the order it has them
        glyph_sequence = glyph_sequence or font.provided_glyphs

        max_width, max_height = find_max_dimensions(font, glyph_sequence)

        if max_width > max_line_width:
            raise ValueError(
                f"Maximum glyph width ({max_width} exceeds maximum"
                f" specified line width: {max_line_width}")

        # Provide some data useful to users in comments
        if actual_source_path:
            s.queue_comment_field("Original font", actual_source_path)
        s.queue_comment_field("Data loaded from", font.path)

        if font.size is not None:
            s.queue_comment_field(f"Font size in pts",  font.size)

        s.queue_comment_field("Max dimensions", f"{max_width}x{max_height} px")
        s.queue_comment_field(f"Exported glyphs", '')
        s.write_comment_field_block()

        s.write_iterable_data(glyph_sequence, line_prefix=COMMENT_PREFIX + " ")

        for glyph in glyph_sequence:
            self.emit_character(font, glyph)


class TextFontWriter(FormatWriter):

    def write_output(
        self, font: RasterFont,
        destination: PathLikeOrHasWrite,
        glyph_sequence: Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:

        with StdOrFile(destination, 'w') as file:
            renderer = FontRenderer(file.raw)
            renderer.emit_textfont(font, glyph_sequence=glyph_sequence)
