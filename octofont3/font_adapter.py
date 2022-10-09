from dataclasses import dataclass
from functools import cache
from typing import Optional, Iterable, Dict, Sequence, Tuple

from PIL import ImageFont, Image

from octofont3 import calculate_alignments
from octofont3.custom_types import BoundingBox, BboxFancy, Size, ImageFontLike, SizeFancy, PathLike, ImageCoreLike
from octofont3.utils import find_max_dimensions, generate_missing_character_core, value_of_first_attribute_present


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
    def from_font_glyph(
        cls,
        bitmap: ImageCoreLike,
        glyph_bbox: BoundingBox
    ) -> "GlyphMetadata":

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


class MissingGlyphError(Exception):
    """
    1 or more required glyphs were not found.

    Does not subclass Key or Index errors because the underlying
    representation below may be either.
    """
    def __init__(self, message_header, missing_glyph_codes: Sequence[int]):
        super().__init__(f"{message_header} : {missing_glyph_codes}")
        self.missing_glyph_codes = missing_glyph_codes

    @classmethod
    def default_msg(cls, missing_glyph_codes: Sequence[int]):
        cls(
            "One or more required glyphs was found to be missing",
            missing_glyph_codes)


class CachingFontAdapter(ImageFontLike):
    """
    Ease of access wrapper around PIL font types with added features.

    It can be used with ImageDraw or other pillow features like normal
    Pillow fonts.

    .. warning:: Only raster fonts support glyph membership checking!

                 You should preview fonts to make sure they have the
                 right characters.

    This class stores metadata about rasterized glyphs for all types
    of fonts using the metadata dataclass above. For FreeType / TTF
    fonts, this class pre-renders glyphs and stores them in a local
    table.

    This should probably be split apart and refactored further, maybe
    with lazy rendering for TTF files.
    """

    def __init__(
        self,
        font: ImageFontLike,
        provided_glyphs: Iterable[str],
        alignments: Optional[Dict] = None,
        path: Optional[PathLike] = None,
        autodetect_path_if_none: bool = True
    ):
        """
        ``provided_glyphs`` is mandatory. It needs to be probed outside
        of this class and passed in. It is excluded from the constructor
        to keep this class simple.

        :param font: The font object wrapped
        :param provided_glyphs: The glyphs probed as provided for this font.
        :param alignments: Overriding alignment data, if any
        :param path: The path the file should be recorded as loaded from
        :return:
        """

        self._font = font

        if autodetect_path_if_none:
            self._path = path or value_of_first_attribute_present(font, ('file', 'path', 'filename'), missing_ok=True)
        else:
            self._path = path

        self._provided_glyphs = tuple(provided_glyphs)
        self._provided_glyph_set = frozenset(self._provided_glyphs)

        # Provide places to store rendered glyph image cores & metadata
        self._local_raster_table: Dict[str, ImageCoreLike] = {}
        self._local_metadata_table: Dict[str, GlyphMetadata] = {}

        # Pre-render glyphs & calculate important metadata
        self.max_glyph_size: SizeFancy = find_max_dimensions(self._font, self._provided_glyphs)
        self._dummy_glyph = generate_missing_character_core(self.max_glyph_size)
        self._dummy_glyph_metadata = GlyphMetadata.from_font_glyph(
            self._dummy_glyph, BboxFancy(1, 1, *self.max_glyph_size))

        self._prerender_glyphs_and_calculate_metadata()
        self.max_bitmap_size = find_max_dimensions(
            self, self._provided_glyphs, lambda f, g: f.get_bitmap_bbox(g))

        # todo: replace this with pixel-based offsets
        if alignments is not None:
            self._alignments = alignments
        else:
            self._alignments = calculate_alignments()

    @property
    def fakes_raster_table(self) -> bool:
        return self._local_raster_table is not None

    def _prerender_glyphs_and_calculate_metadata(self):

        # todo: optimize this to be cleaner? duplicates work on missing glyphs?
        for glyph in self._provided_glyphs:
            glyph_bbox = self.getbbox(glyph)

            # On well-behaved fonts, this should be a core instead of
            # None. This check may be removable in the future once font
            # behavior is better understood.
            raw_mask = self.getmask(glyph)
            if raw_mask is None:
                glyph_bitmap = self._dummy_glyph
            else:
                glyph_bitmap = raw_mask

            self._local_raster_table[glyph] = glyph_bitmap
            self._local_metadata_table[glyph] = GlyphMetadata.from_font_glyph(
                glyph_bitmap, glyph_bbox or (0, 0, *self.max_glyph_size))
            pass
        pass

    def items(self):
        return self._local_raster_table.items()

    @property
    def glyph(self):
        """
        Provides semi-compatibility with Imagefont-like classes.

        Uses a dict instead of a list internally to gain some
        flexibility at the price of breaking strict compatibility.

        This should probably use an immutable mapping in the future,
        but pillow's classes don't either.
        :return:
        """
        #if self.fakes_raster_table:
        #    return self._local_raster_table
        return self._local_raster_table

    @property
    def path(self):
        return self._path

    @property
    def provided_glyphs(self) -> Tuple[str, ...]:
        return tuple(self._provided_glyphs)

    @property
    def provided_glyph_set(self) -> frozenset:
        return self._provided_glyph_set

    @property
    def size(self):
        return getattr(self._font, 'size', None)

    @property
    def alignments(self) -> Dict:
        return self._alignments

    @property
    def font(self) -> ImageFontLike:
        return self._font

    def getmask(self, text: str) -> ImageCoreLike:
        if text in self._local_raster_table:
            return self._local_raster_table[text]

        return self._font.getmask(text)

    def getbbox(self, text: str) -> BboxFancy:
        if text in self._local_raster_table:
            return self._local_metadata_table[text].glyph_bbox

        return BboxFancy(*self._font.getbbox(text))

    @cache
    def get_bitmap_bbox(self, text: str) -> Optional[BboxFancy]:
        """
        Get the bounding box of the image data for the passed text.

        This may be a single character or multiple characters. This can
        theoretically be used to return emoji glyphs for multi-character
        sequences such as regional indicators, although the parsing for
        this is not yet implemented.

        The returned bbox can be None sometimes, but this not an
        indicator for any specific condition.  It is a good idea
        to use previewing to make sure a glyph is actually in the font.

        For TTFs, it is unlikely that a glyph can be distinguished
        from the data as a missing or non-missing glyph, as the data
        is not guaranteed to be an empty rectangle:
        https://typedrawers.com/discussion/4199/best-practices-for-null-and-notdef

        For other types of wrapped font, the bbox may be None or all 0s
        depending on implementation. This may happen when the image core
        has no actual data, such as when:

            1. The character is a natural blank such as space
            2. The character is missing from the font

        :param text:
        :return:
        """

        if text in self._local_raster_table:
            return self._local_metadata_table[text].bitmap_bbox

        mask = self._font.getmask(text)
        if mask is None:
            return None

        bbox = mask.getbbox()
        if bbox is not None:
            bbox = BboxFancy(*bbox)
        return bbox

    def get_glyph_metadata(self, text: str) -> GlyphMetadata:
        return self._local_metadata_table[text]