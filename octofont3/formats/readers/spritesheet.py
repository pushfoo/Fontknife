from typing import Iterable, Optional, Union, cast

from PIL import Image

from octofont3.custom_types import PathLikeOrHasRead, BytesLike, Size, BoundingBox, BboxFancy
from octofont3.formats import RasterFont
from octofont3.formats.common import BinaryReader
from octofont3.formats.common.spritesheet import GridMapper, DEFAULT_SHEET_GLYPHS


class SpritesheetGridReader(BinaryReader):
    format_name = 'spritesheet-grid'
    file_extensions = ('png', 'jpg', 'gif', 'tga', 'bmp')

    def load_source(
        self,
        source: PathLikeOrHasRead[BytesLike],
        font_size: int = 16,
        glyph_sequence: Optional[Iterable[str]] = None,
        bounds_px: Optional[Union[Size, BoundingBox]] = None,
        sheet_size_tiles: Optional[Size] = None,
        tile_size_px: Optional[Size] = None,
        tile_spacing_px: Size = (0, 0),
        **kwargs
    ) -> RasterFont:
        source_image = Image.open(source)
        source_image.load()

        glyph_sequence = glyph_sequence or DEFAULT_SHEET_GLYPHS
        if bounds_px is None:
            bounds_px = BboxFancy(source_image.size)

        grid_mapper = GridMapper(
            sheet_bounds_px=bounds_px,
            sheet_size_tiles=sheet_size_tiles,
            tile_size_px=tile_size_px,
        )

        # Build the glyph table
        glyph_table = {}
        for index, glyph in enumerate(glyph_sequence):
            glyph_image = source_image.crop(cast(tuple, grid_mapper[index]))
            glyph_table[glyph] = glyph_image

        raster_font = RasterFont(glyph_table)
        return raster_font

