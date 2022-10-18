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
            font_size: int = 16,
            force_provided_glyphs: Optional[Iterable[str]] = None
    ) -> RasterFont:
        if force_provided_glyphs is None:
            force_provided_glyphs = generate_glyph_sequence()
        with StdOrFile(source, 'rb') as wrapped:
            raw_font = self.__class__.wrapped_callable(
                wrapped.raw, size=font_size)
            path = get_resource_filesystem_path(source)

        raw_glyph_table = copy_glyphs(raw_font, glyphs=force_provided_glyphs)
        raster_font = RasterFont(
            glyph_table=raw_glyph_table,
            size_points=font_size,
            path=path
        )
        return raster_font
