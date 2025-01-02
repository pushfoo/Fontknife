import math
from typing import Optional, Iterable

import PIL.Image
import PIL.ImageDraw

from fontknife.colors import RGBA_WHITE, RGBA_BLACK
from fontknife.custom_types import PathLikeOrHasWrite, GlyphSequence
from fontknife.formats import RasterFont, FormatWriter
from fontknife.formats.common.spritesheet import GridMapper
from fontknife.graphemes import parse_graphemes


class SpriteSheetGridWriter(FormatWriter):

    format_name = 'spritesheet-grid'
    file_extensions = ('png', 'jpg', 'tga', 'bmp')

    def write_output(
        self,
        font: RasterFont,
        destination: PathLikeOrHasWrite,
        glyph_sequence: Optional[GlyphSequence] = None,
        mode: str = 'RGBA',
        sheet_scale: int = 1,
        foreground_color=RGBA_WHITE,
        background_color=RGBA_BLACK,
        **kwargs
    ) -> None:
        max_glyph_size = font.max_glyph_size

        if isinstance(glyph_sequence, str):
            raise TypeError("Expected a grapheme sequence as a non-string iterable.")
        elif not glyph_sequence:
            glyph_sequence = font.provided_glyphs

        # Get our initial un-overridden number of columns
        num_glyphs = len(glyph_sequence)
        default_columns = min(16, num_glyphs)
        default_rows = int(math.ceil(num_glyphs / default_columns))

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

        # Draw all glyphs into the sprite sheet
        dest_image = PIL.Image.new(mode, grid_mapper.sheet_bounds_px[2:], color=background_color)
        dest_draw = PIL.ImageDraw.Draw(dest_image)

        for index, glyph in enumerate(glyph_sequence):
            paste_bbox = grid_mapper.bbox_for_sheet_index(index)
            dest_draw.text(paste_bbox[:2], glyph, fill=foreground_color, font=font)

        if not isinstance(sheet_scale, int):
            raise TypeError('Sheet scale must be an integer with value 1 or greater')
        elif sheet_scale < 1:
            raise ValueError('Sheet scale must be an integer with value 1 or greater')
        elif sheet_scale != 1:
            dest_image = dest_image.resize(
                (
                    dest_image.size[0] * sheet_scale,
                    dest_image.size[1] * sheet_scale
                ))

        dest_image.save(destination)
