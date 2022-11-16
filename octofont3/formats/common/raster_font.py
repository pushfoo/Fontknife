from types import MappingProxyType
from typing import Iterable, Dict, Optional, KeysView

from PIL import Image

from octofont3.custom_types import ImageFontLike, ImageCoreLike, GlyphMapping, GlyphMetadata, BboxFancy, PathLike, Size, \
    BoundingBox
from octofont3.utils import generate_missing_character_core


def copy_glyphs(source_font: ImageFontLike, glyphs: Iterable[str]) -> Dict[str, ImageCoreLike]:
    """
    Working stub version of glyph rasterization.

    Glyph strings can consist of multiple characters to account for
    emoji and other unicode constructs that may be useful to include
    in exported data.

    :param source_font: a font-like object to copy from
    :param glyphs: which glyphs to copy from it.
    :return:
    """
    return {glyph: source_font.getmask(glyph, mode='1') for glyph in glyphs}


class RasterFont:

    def __init__(
        self,
        glyph_table: Optional[GlyphMapping] = None,
        text_tracking_px: int = 0,
        size_points: Optional[int] = None,
        **font_metadata
    ):
        """
        The common interchange structure all fonts are loaded to.

        Compatible with PIL drawing functions, so it can be used to render
        previews.

        This class cannot be loaded from fonts directly. FormatReader
        subclasses are expected to return rasterized copies of source fonts
        instead.

        :param glyph_table: An raw table of glyph bitmaps.
        :param text_tracking_px: The space added between glyph tiles.
        :param size_points: The size in points, if any.
        :param font_metadata: Can be accessed via
        """
        self._font_metadata = font_metadata
        self._text_tracking_px = text_tracking_px
        self._size_points: Optional[int] = size_points

        self._glyph_bitmaps: Dict[str, ImageCoreLike] = dict(glyph_table) if glyph_table else {}
        self._glyph_metadata: Dict[str, GlyphMetadata] = {}

        self._max_tile_bbox: Optional[BboxFancy] = None
        self._max_bitmap_bbox: Optional[BboxFancy] = None
        self._notdef_glyph: Optional[ImageCoreLike] = None

        self._update_metadata()

    def _update_metadata(self, updated_glyphs: Optional[Iterable[str]] = None) -> None:
        """
        Calculate metadata & the filler glyph for the font.

        Does nothing if there are no glyphs in the bitmap table.

        Otherwise, it will do the following:
            1. Update glyph-specific metadata
            2. Update ``self._max_tile_bbox``.
            3. Update ``self._notdef_glyph`` to be slightly smaller than
               the tile size of the font.

        You can limit recalculation of glyph-specific metadata to only
        changed glyphs by passing an iterable of glyph strings via
        ``updated_glyphs``.

        :param updated_glyphs: Limit metadata update to these glyphs
        """

        # Exit early if there are no valid glyphs in the table.
        if not self._glyph_bitmaps:
            return

        if not updated_glyphs:
            updated_glyphs = self._glyph_bitmaps.keys()

        for glyph in updated_glyphs:
            glyph_bbox = self.getbbox(glyph)
            glyph_bitmap = self.getmask(glyph) if glyph_bbox else self._notdef_glyph

            self._glyph_metadata[glyph] = GlyphMetadata.from_font_glyph(glyph_bitmap, glyph_bbox)

        # Brute force the maximum tile bounding box.
        # It doesn't seem worth optimizing given present expectations:
        #  1. Fonts will not change frequently
        #  2. Fonts will not frequently exceed 256 glyphs
        tile_max_bbox = None
        for metadata in self._glyph_metadata.values():
            current = metadata.glyph_bbox
            if tile_max_bbox is None:
                tile_max_bbox = current
            else:
                tile_max_bbox |= current
            # bitmap_max_bbox .update(metadata.bitmap_bbox)

        self._max_tile_bbox: BboxFancy = BboxFancy(*tile_max_bbox)
        # self._max_bitmap_bbox = BboxFancy(*bitmap_max_bbox)
        self._notdef_glyph = generate_missing_character_core(self._max_tile_bbox[:2])
        self._notdef_glyph_metadata = GlyphMetadata.from_font_glyph(self._notdef_glyph, self._max_tile_bbox)

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
