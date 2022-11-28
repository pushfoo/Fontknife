from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Dict, Optional, KeysView, Union, Mapping, Tuple, Protocol

from PIL import Image, ImageDraw

from fontknife.custom_types import ImageFontLike, ImageCoreLike, BboxFancy, PathLike, \
    Size, BoundingBox, SizeFancy


@dataclass
class GlyphMetadata:
    """
    Keep track of bounding box information about glyphs.

    Glyphs can have empty actual data despite having a bounding box. In
    this case, bitmap_bbox will be None.

    This class does not store the PIL.Image.core object itself because
    doing so causes issues with dataclass library internals.
    """
    bitmap_bbox: Optional[BboxFancy]
    glyph_bbox: BboxFancy
    bitmap_size: Size
    bitmap_len_bytes: int

    @classmethod
    def from_font_glyph(cls, glyph_bbox: BoundingBox, bitmap: ImageCoreLike) -> GlyphMetadata:

        # get the stated values
        glyph_bbox = BboxFancy(*glyph_bbox)
        bitmap_bbox = None

        if bitmap is not None:
            bitmap_bbox = bitmap.getbbox()
            if bitmap_bbox is not None:
                bitmap_bbox = BboxFancy(*bitmap_bbox)

        return cls(
            glyph_bbox=glyph_bbox,
            bitmap_bbox=bitmap_bbox,
            bitmap_size=SizeFancy(*bitmap.size),
            bitmap_len_bytes=len(bitmap)
        )


GlyphMaskMapping = Mapping[str, ImageCoreLike]
GlyphMetadataMapping = Mapping[str, GlyphMetadata]


class GlyphRasterizerCallable(Protocol):
    def __call__(self, font: ImageFontLike, glyph: str, mode: str = '1') -> Tuple[BoundingBox, ImageCoreLike]:
        ...


def copy_glyph_data_from_bitmap_format(
    font: ImageFontLike, glyph: str, mode: str = '1'
) -> Tuple[BoundingBox, ImageCoreLike]:
    """
    Copy bitmap font data from non-TTF fonts.

    TTFs report incorrect offsets with this function. The underlying
    cause may be bugs in Pillow's TTF handling, or a quirk of the
    TTF format. A TTF-specific rasterizer function exists in the
    TTF format reader module as an alternative to this function.

    :param font: The font object to extract glyph data from
    :param glyph: A string corresponding to a glyph in the font
    :param mode: A valid PIL color mode
    :return:
    """
    return font.getbbox(glyph), font.getmask(glyph, mode=mode)


def rasterize_font_to_tables(
    source_font: ImageFontLike,
    glyphs: Iterable[str],
    mode: str = '1',
    glyph_rasterizer: GlyphRasterizerCallable = copy_glyph_data_from_bitmap_format
) -> Dict[str, Union[GlyphMetadataMapping, GlyphMaskMapping]]:
    """
    Copy glyph data from a source font to mask and metadata tables.

    Glyph strings can consist of multiple characters to account for
    emoji and other unicode constructs that may be useful to include
    in exported data.

    :param source_font: A font-like object to copy from
    :param glyphs: Which glyphs to copy from it.
    :param mode: Which PIL color mode to rasterize in.
    :param glyph_rasterizer: A callable which turns glyphs into
                             bboxes and masks.
    :return:
    """
    glyph_masks = {}
    glyph_metadata = {}

    for glyph in glyphs:
        glyph_bbox, mask = glyph_rasterizer(source_font, glyph, mode=mode)
        metadata = GlyphMetadata.from_font_glyph(glyph_bbox, mask)

        glyph_masks[glyph] = mask
        glyph_metadata[glyph] = metadata

    return {'glyph_metadata_table': glyph_metadata, 'glyph_table': glyph_masks}


def optional_mapping_to_dict(optional: Optional[Mapping]) -> Dict:
    if optional is None:
        return dict()
    return dict(optional)


def generate_missing_character_core(
    image_size: Size,
    rectangle_bbox: Optional[BoundingBox] = None,
    mode: str = '1',
    rectangle_margins_px: int = 1,
    color=255,
    background=0
) -> ImageCoreLike:
    """
    Generate a missing glyph "tofu" square as an image core object.

    :param image_size: How big the tofu bitmap should be
    :param rectangle_bbox: Force a rectangle size and override margins.
    :param mode: A valid PIL color mode
    :param rectangle_margins_px: How much smaller than the image the
                                 tofu should be.
    :param color: A valid PIL color for the tofu rectangle line.
    :param background: A valid PIL color for the image background.
    :return:
    """
    # Calculate rectangle dimensions if not provided
    image_size = SizeFancy(*image_size)
    if rectangle_bbox is None:
        rectangle_bbox = (
            rectangle_margins_px,
            rectangle_margins_px,
            image_size.width - (1 + rectangle_margins_px),
            image_size.height - (1 + rectangle_margins_px)
        )

    # Draw the rectangle on the image
    image = Image.new(mode, image_size, color=background)
    draw = ImageDraw.Draw(image, mode)
    draw.rectangle(rectangle_bbox, outline=color)

    # Return the core for use as a mask
    return image.im


class RasterFont:

    def __init__(
        self,
        glyph_table: Optional[GlyphMaskMapping] = None,
        glyph_metadata_table: Optional[GlyphMetadataMapping] = None,
        text_tracking_px: int = 0,
        size_points: Optional[int] = None,
        **font_metadata
    ):
        """
        The common interchange structure all fonts are loaded to.

        Compatible with PIL drawing functions, so it can be used to render
        previews or perform other tasks.

        This class is not intended to be loaded from fonts directly.
        FormatReader subclasses are expected to return rasterized copies
        of source fonts instead.

        :param glyph_table: An raw table of glyph bitmaps.
        :param text_tracking_px: The space added between glyph tiles.
        :param size_points: The size in points, if any.
        :param font_metadata: Additional metadata to store on the font.
        """
        self._font_metadata = font_metadata
        self._text_tracking_px = text_tracking_px
        self._size_points: Optional[int] = size_points

        self._glyph_bitmaps: Dict[str, ImageCoreLike] = optional_mapping_to_dict(glyph_table)
        self._glyph_metadata: Dict[str, GlyphMetadata] = optional_mapping_to_dict(glyph_metadata_table)

        if self._glyph_metadata.keys() != self._glyph_bitmaps.keys():
            raise ValueError('Bitmap and metadata tables should cover the same glyphs!')

        self._max_tile_bbox: Optional[BboxFancy] = None
        self._max_bitmap_bbox: Optional[BboxFancy] = None
        self._notdef_glyph: Optional[ImageCoreLike] = None

        if self._glyph_metadata:
            self._update_max_tile_size_and_tofu()

    def _update_max_tile_size_and_tofu(self) -> None:
        """
        Calculate maximum size and the filler glyph for the font.

        Does nothing if there are no glyphs in the bitmap table.

        Otherwise, it will do the following:
            1. Update glyph-specific metadata
            2. Update ``self._max_tile_bbox``.
            3. Update ``self._notdef_glyph`` to be slightly smaller than
               the tile size of the font.

        You can limit recalculation of glyph-specific metadata to only
        changed glyphs by passing an iterable of glyph strings via
        ``updated_glyphs``.
        """

        if not self._glyph_bitmaps:
            return  # Exit early, nothing to do

        # Brute force the maximum tile bounding box.
        # It doesn't seem worth optimizing right now given the following:
        #  1. RasterFont objects will not change frequently
        #  2. This tool is designed for converting retro bitmap fonts
        #     and generating filler assets.
        tile_max_bbox = None
        for glyph, metadata in self._glyph_metadata.items():
            current = metadata.glyph_bbox
            if tile_max_bbox is None:
                tile_max_bbox = current
            else:
                tile_max_bbox |= current

        self._max_tile_bbox: BboxFancy = BboxFancy(*tile_max_bbox)
        self._notdef_glyph = generate_missing_character_core(self._max_tile_bbox[:2])
        self._notdef_glyph_metadata = GlyphMetadata.from_font_glyph(self._max_tile_bbox, self._notdef_glyph)

    def get_glyph_metadata(self, glyph: str) -> GlyphMetadata:
        return self._glyph_metadata.get(glyph, self._notdef_glyph_metadata)

    @property
    def font_metadata(self) -> MappingProxyType:
        return MappingProxyType(self._font_metadata)

    @property
    def path(self) -> Optional[PathLike]:
        return self._font_metadata.get('path', None)

    @property
    def max_glyph_size(self) -> Size:
        return self._max_tile_bbox.size

    @property
    def provided_glyphs(self) -> KeysView[str]:
        return self._glyph_bitmaps.keys()

    @property
    def glyph_table(self) -> MappingProxyType:
        return MappingProxyType(self._glyph_bitmaps)

    def get_glyph(self, value: str, strict=False) -> ImageCoreLike:
        if value in self._glyph_bitmaps:
            return self._glyph_bitmaps[value]
        elif not strict:
            return self._notdef_glyph
        raise KeyError(f'Could not find glyph data for {value!r}')

    @property
    def size(self) -> Optional[int]:
        """
        Return any known point size for the font.

        This can return None because some font formats do not provide
        this information.

        :return:
        """
        return self._size_points

    def getsize(self, text: str) -> Size:
        total_width = 0
        total_height = 0

        last_index = len(text) - 1
        for char_index, char_code in enumerate(text):

            char_image = self.get_glyph(text)

            width, height = char_image.size

            total_height = max(total_height, height)
            total_width += width

            if char_index < last_index:
                total_width += self._text_tracking_px

        return total_width, total_height

    def getmask(self, text: str, mode: str = '') -> ImageCoreLike:
        """
        Get an imaging core object to use as a drawing mask.

        Breaks PEP naming conventions for pillow compatibility.

        :param text: The text to get a mask for.
        :param mode: Attempt to force the image mode.
        :return:
        """
        size = self.getsize(text)
        mode = mode or '1'
        mask_image = Image.new(mode, size)
        last_index = len(text) - 1
        current_x, current_y = 0, 0
        for i, char in enumerate(text):
            char_image = self.get_glyph(char)
            width, height = char_image.size

            mask_image.paste(
                char_image,
                (current_x, current_y, current_x + width, current_y + height))
            current_x += width
            if i < last_index:
                current_x += self._text_tracking_px

        return mask_image.im

    def getbbox(self, text: str) -> BoundingBox:
        """
        Get a bounding box for the specified text.

        Breaks PEP naming conventions for pillow compatibility.

        :param text: The text to get a bounding box for.
        :return:
        """
        width, height = self.getsize(text)
        return BboxFancy(0, 0, width, height)

