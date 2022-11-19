from typing import Union, Optional, Iterable

from PIL import ImageFont

from octofont3.custom_types import PathLike, HasRead
from octofont3.formats import RasterFont, copy_glyphs
from octofont3.formats.common import BinaryReader
from octofont3.iohelpers import StdOrFile, get_resource_filesystem_path
from octofont3.utils import generate_glyph_sequence


class TrueTypeReader(BinaryReader):
    format_name = 'truetype'
    file_extensions = ['ttf']
    wrapped_callable = ImageFont.truetype

    def load_source(
            self, source: Union[PathLike, HasRead],
            font_size_points: int = 16,
            glyph_sequence: Optional[Iterable[str]] = None,
            **kwargs
    ) -> RasterFont:
        if glyph_sequence is None:
            glyph_sequence = generate_glyph_sequence()
        with StdOrFile(source, 'rb') as wrapped:
            raw_font = self.__class__.wrapped_callable(
                wrapped.raw, size=font_size_points)
            path = get_resource_filesystem_path(source)

        raw_glyph_table = copy_glyphs(raw_font, glyphs=glyph_sequence)
        raster_font = RasterFont(
            glyph_table=raw_glyph_table,
            size_points=font_size_points,
            path=path
        )
        return raster_font
