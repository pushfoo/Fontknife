from typing import Iterable, Optional, Union, cast

from PIL import Image

from fontknife.custom_types import PathLikeOrHasRead, BytesLike, Size, BoundingBox, BboxFancy
from fontknife.formats.common.raster_font import GlyphMetadata
from fontknife.formats import RasterFont
from fontknife.formats.common import BinaryReader
from fontknife.formats.common.spritesheet import GridMapper, DEFAULT_SHEET_GLYPHS


class SpritesheetGridReader(BinaryReader):
    format_name = 'spritesheet-grid'
    file_extensions = ('png', 'jpg', 'tga', 'bmp')

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
        glyph_masks = {}
        glyph_metadata = {}

        for index, glyph in enumerate(glyph_sequence):
            glyph_image = source_image.crop(cast(tuple, grid_mapper[index]))
            glyph_bbox = BboxFancy(glyph_image.size)
            glyph_mask = glyph_image.im

            glyph_masks[glyph] = glyph_mask
            glyph_metadata[glyph] = GlyphMetadata.from_font_glyph(glyph_bbox, glyph_mask)

        raster_font = RasterFont(
            glyph_table=glyph_masks,
            glyph_metadata=glyph_metadata
        )
        return raster_font

