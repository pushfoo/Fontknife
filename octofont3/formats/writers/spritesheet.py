import math
from typing import Optional, Iterable

import PIL.Image

from octofont3.custom_types import PathLikeOrHasWrite
from octofont3.formats import RasterFont, FormatWriter
from octofont3.formats.common.spritesheet import GridMapper
from octofont3.utils import image_from_core


class SpriteSheetGridWriter(FormatWriter):
    format_name = 'spritesheet-grid'
    file_extensions = ('png', 'jpg', 'tga', 'bmp')

    def write_output(
        self,
        font: RasterFont,
        destination: PathLikeOrHasWrite,
        glyph_sequence: Optional[Iterable[str]] = None,
        mode='RGB',
        **kwargs
    ) -> None:

        max_glyph_size=font.max_glyph_size
        default_columns = 16
        default_rows = int(math.ceil(len(font.provided_glyphs) / default_columns))

        defaults = {
            'tile_size_px': max_glyph_size,
            'sheet_size_tiles': (default_columns, default_rows),
            'sheet_bounds_px': (
                max_glyph_size[0] * default_columns,
                max_glyph_size[1] * default_rows
            )
        }

        # Current implementations of dict merging and copying in utils
        # treat None as a valid value, so this is a workaround.
        reader_args = {}
        for k, v in defaults.items():
            if k in kwargs and kwargs[k] is not None:
                reader_args[k] = v
            else:
                reader_args[k] = defaults[k]

        grid_mapper = GridMapper(**reader_args)

        if glyph_sequence is None:
            glyph_sequence = font.provided_glyphs

        # Paste all glyphs into new image

        dest_image = PIL.Image.new(mode, grid_mapper.sheet_bounds_px[2:])
        for index, glyph in enumerate(glyph_sequence):
            paste_bbox = grid_mapper.bbox_for_sheet_index(index)
            tile_image = image_from_core(font.getmask(glyph), mode=mode)
            dest_image.paste(tile_image, paste_bbox[:2])

        dest_image.save(destination)

