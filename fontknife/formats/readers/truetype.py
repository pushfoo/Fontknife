from typing import Union, Optional, Iterable, Tuple, cast

from PIL import ImageFont, ImageDraw, Image

from fontknife.custom_types import PathLike, HasRead, BoundingBox, ImageCoreLike, Size
from fontknife.formats import RasterFont, rasterize_font_to_tables
from fontknife.formats.common import BinaryReader
from fontknife.formats.common.raster_font import GlyphRasterizerCallable
from fontknife.iohelpers import StdOrFile, get_resource_filesystem_path
from fontknife.utils import generate_glyph_sequence


def ttf_bbox_and_mask_getter(
    font: ImageFont.FreeTypeFont,
    glyph: str,
    mode: str = '1',
    topleft_offset: Size = (10, 10),
    scratch_image_size: Size = (100, 100)
) -> Tuple[BoundingBox, ImageCoreLike]:
    """
    TTF-specific getter that works around broken functions in ImageFont.

    The getbbox function reports nonsensical negative values for some
    TTF fonts, so this uses a newer function for handling bounding boxes.

    :param font: Which TTF font to pull from.
    :param glyph: A string for a glyph in the font. May be more than 1
                  character, such as an emoji.
    :param mode: A valid PIL image mode.
    :param topleft_offset: How far from the top left to draw. This must
                           be greater than 0,0 to ensure enough room to
                           account for negative offset reports for some
                           TTF files.
    :param scratch_image_size: How big the uncropped draw area should be
    :return:
    """
    image = Image.new(mode, tuple(scratch_image_size), 0)
    draw = ImageDraw.ImageDraw(image)
    offset_tuple = tuple(topleft_offset)

    # Draw text and crop to text bounding box.
    draw.text(offset_tuple, glyph, fill=255, font=font)
    bbox = draw.textbbox(offset_tuple, glyph, font=font)
    glyph_cropped = image.crop(bbox)

    return bbox, glyph_cropped.im


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

        raw_glyph_data = rasterize_font_to_tables(
            raw_font, glyph_sequence,
            glyph_rasterizer=cast(GlyphRasterizerCallable, ttf_bbox_and_mask_getter)
        )
        raster_font = RasterFont(
            **raw_glyph_data,
            size_points=font_size_points,
            path=path
        )
        return raster_font
