import string
from dataclasses import dataclass, field
from functools import cache
from typing import Optional, Union, Callable, Iterable, Dict, Any, Sequence, Tuple

from PIL import ImageFont, Image

from octofont3 import calculate_alignments
from octofont3.custom_types import BoundingBox, BboxFancy, Size, ImageFontLike, SizeFancy, FontWithGlyphTable, \
    GlyphTableEntry
from octofont3.utils import get_bbox_size, find_max_dimensions, filternone


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
        bitmap: Image.core,
        glyph_bbox: BoundingBox
    ) -> "GlyphMetadata":

        # get the stated values
        glyph_bbox = BboxFancy(*glyph_bbox)
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


def pair_iterator_for_font(font: FontWithGlyphTable) -> Iterable[Tuple[int, GlyphTableEntry]]:
    glyph_table = font.glyph
    if isinstance(font.glyph, dict):
        return font.glyph.items()
    return ((code, im) for code, im in enumerate(glyph_table) if im)


def get_provided_codes(font: FontWithGlyphTable) -> Tuple[int, ...]:
    return tuple(map(lambda pair: pair[0], pair_iterator_for_font(font)))


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
        require_glyph_sequence: Optional[Iterable[str]] = None,
        size: Optional[int] = None,
        alignments: Optional[Dict] = None,
    ):
        """

        :param font: The font object wrapped
        :param require_glyph_sequence: The glyphs included in this font.
        :param size: An optional override for storing size in points
        :param alignments: Overriding alignment data, if any
        :return:
        """

        self._font = font
        self._size = size
        self._path = getattr(font, 'source', None)
        # Data for adapting fonts and convenience features

        self._local_metadata_table: Dict[int, GlyphMetadata] = {}

        # setting this to a non-None value means we are faking the raster table
        self._local_raster_table: Optional[Dict[int, Any]] = None
        self._glyph_sequence: Optional[Tuple[int, ...]] = None
        self._provided_glyphs: Optional[Tuple[int, ...]] = None

        # Store any passed glyph sequence
        if require_glyph_sequence:
            self._glyph_sequence = tuple(map(ord, require_glyph_sequence))

        # Handle fonts that come with a readable table
        if isinstance(font, FontWithGlyphTable):
            self._provided_glyphs = get_provided_codes(font)

            if self._glyph_sequence is None:
                self._glyph_sequence = self._provided_glyphs
            else:
                provided_set = set(self._provided_glyphs)
                missing = [code for code in self._glyph_sequence if code not in provided_set]
                if missing:
                    raise MissingGlyphError.default_msg(missing)

        else:  # We have to make a glyph table ourselves
            # Todo: implement actual check for the requested glyphs
            self._local_raster_table = {}

        # Pre-render if needed, and calculate font + per-glyph metadata
        self._prerender_glyphs_and_calculate_metadata()
        _char_sequence = tuple(map(chr, self._glyph_sequence))
        self.max_glyph_size = find_max_dimensions(self, _char_sequence)
        self.max_bitmap_size = find_max_dimensions(
            self, _char_sequence, lambda f, g: f.get_bitmap_bbox(g))

        # todo: replace this with pixel-based offsets
        if alignments is not None:
            self._alignments = alignments
        else:
            self._alignments = calculate_alignments()

    @property
    def fakes_raster_table(self) -> bool:
        return self._local_raster_table is not None

    def _prerender_glyphs_and_calculate_metadata(self):
        fakes_raster_table = self.fakes_raster_table

        for glyph_code in self._glyph_sequence:
            glyph = chr(glyph_code)
            glyph_bbox = self._font.getbbox(glyph)
            glyph_bitmap = self._font.getmask(glyph)

            if fakes_raster_table:
                self._local_raster_table[glyph_code] = glyph_bitmap

            self._local_metadata_table[glyph_code] = GlyphMetadata.from_font_glyph(glyph_bitmap, glyph_bbox)

    @property
    def items(self):
        if self.fakes_raster_table:
            # return an iterator over the cached raster table
            for pair in self._local_raster_table.items():
                yield pair
        elif isinstance(self._font.glyph, dict):
            # handle font objects in the style of this tool
            for pair in self._font.glyph.items():
                yield pair
        else:  # some kind of old-style binary format
            for index in range(len(self._font)):
                yield index, self._font[index]

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
        if self.fakes_raster_table:
            return self._local_raster_table
        return self._font.glyph

    @property
    def path(self):
        return self._path

    @property
    def size(self):
        if self._size:
            return self._size
        return getattr(self._font, 'size', None)

    @property
    def alignments(self) -> Dict:
        return self._alignments

    @property
    def font(self) -> ImageFont:
        return self._font

    def _can_use_local_table(self, text: str) -> bool:
        """
        True if the argument is a single glyph and this
        A helper function for the adapter functions later on.

        :param text:
        :return:
        """
        return self._local_raster_table is not None and len(text) == 1

    @cache
    def getmask(self, text: str):
        if self._can_use_local_table(text):
            return self._local_raster_table[ord(text)]

        return self._font.getmask(text)

    @cache
    def getbbox(self, text: str) -> BboxFancy:
        if self._can_use_local_table(text):
            return self._local_metadata_table[ord(text)].glyph_bbox

        return BboxFancy(*self._font.getbbox(text))

    @cache
    def get_bitmap_bbox(self, text: str) -> Optional[BboxFancy]:
        """
        Get the bounding box of the image data.

        This can be None if the image core has no actual data, which is
        useful to notice for characters with an empty entry in the glyph
        table.

        :param text:
        :return:
        """
        if self._can_use_local_table(text):
            return self._local_metadata_table[ord(text)].bitmap_bbox
        bbox = self._font.getmask(text).getbbox()
        if bbox is not None:
            bbox = BboxFancy(*bbox)
        return bbox

    def get_glyph_metadata(self, text: str) -> GlyphMetadata:
        if len(text) != 1:
            raise ValueError("This method only takes 1-length strings")
        return self._local_metadata_table[ord(text)]