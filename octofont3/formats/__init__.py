from abc import ABC, abstractmethod
from inspect import isabstract
from pathlib import Path
from types import MappingProxyType
from typing import Optional, Iterable, Union, Callable, Dict, Set, Type, Mapping, KeysView

from PIL import ImageFont, Image
from PIL.BdfFontFile import BdfFontFile
from PIL.PcfFontFile import PcfFontFile

from octofont3.custom_types import HasRead, PathLike, PathLikeOrHasRead, ImageCoreLike, GlyphMetadata, Size, \
    BoundingBox, BboxFancy, ImageFontLike
from octofont3.formats.caching import get_cache, load_and_cache_bitmap_font
from octofont3.formats.textfont.parser import TextFontFile
from octofont3.iohelpers import SeekableBinaryFileCopy, get_source_filesystem_path, StdOrFile
from octofont3.utils import generate_missing_character_core, BboxEnclosingAll, generate_glyph_sequence


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
        glyph_table: Optional[Mapping[str, ImageCoreLike]] = None,
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

        :param glyph_table: A raw table of glyphs, if any.
        :param text_tracking_px: The space added between glyph tiles.
        :param size_points: The size in points, if any.
        :param font_metadata: Can be accessed via
        """
        self._font_metadata = font_metadata
        self._text_tracking_px = text_tracking_px
        self._size_points: Optional[int] = size_points

        self._glyph_bitmaps: Dict[str, ImageCoreLike] = dict(glyph_table) if glyph_table else {}
        self._glyph_metadata: Dict[str, GlyphMetadata] = {}

        self._max_tile_bbox: Optional[BoundingBox] = None
        self._max_bitmap_bbox: Optional[BoundingBox] = None
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

        :param updated_glyphs: Limit metadata update to these glyph keys
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
        tile_max_bbox = BboxEnclosingAll()
        for metadata in self._glyph_metadata.values():
            tile_max_bbox.update(metadata.glyph_bbox)
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

    def get_glyph(self, value: str, strict=False):
        if value in self._glyph_bitmaps:
            return self._glyph_bitmaps[value]
        elif not strict:
            return self._notdef_glyph
        raise KeyError(f'Could not find glyph data for {value!r}')

    @property
    def size(self) -> Optional[int]:
        """
        Return the size in points for the font if it's known property of the original ImageFont.

        This can return None because pillow does not provide a way to
        recover
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

    def getmask(self, text: str, mode: str = ''):
        """
        Get an imaging core object to use as a drawing mask.

        Crucial for drawing text.

        :param text:
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
        width, height = self.getsize(text)
        return BboxFancy(0, 0, width, height)


class FormatReader(ABC):

    # Track valid readers in subclasses
    by_format_name: Dict[str, Type["FormatReader"]] = {}
    by_file_extension: Dict[str, Type["FormatReader"]] = {}
    file_extension_to_format_name: Dict[str, str] = {}
    file_extensions_for_class: Dict[type, Set[str]] = {}

    def __init__(self, caching_strategy: Callable = get_cache):
        """
        Baseclass for all format readers.

        These classes handle loading
        :param caching_strategy:
        """
        self.cache = caching_strategy()

    def __init_subclass__(cls):
        """
        Register every non-abstract subclass for easy access.

        This uses the attributes of subclasses instead of
        __init_subclass__ arguments because ABC appears to be
        incompatible in current python versions.

        The following subclass attributes are supported:
            1. ``wrapped_creation_func`` Mandatory for registration,
               optional for ABCs. A creation function or type wrapped
               by the subclass.
            1. ``format_name`` overrides auto-generation of format name
            2. ``file_extension`` overrides auto-generation of file
                extensions.

        If ``format_name`` is None or empty, it will be generated by:

            1. Converting the class name to lower case
            2. Removing 'reader' from the end of the name if present

        ``file_extensions`` will be handled as follows:

            1. Use the ``file_extensions`` class attribute if it
               exists, otherwise use the format name.
            2. If the current candidate is a string, use it to create
               a 1-length set. Otherwise, convert the iterable to a
               set.
            3. Use the set to fill ``by_file_extension`` and
               ``file_extensions_for_class``.

        The reader classes can then be retrieved by their associated
        format names and file extensions.
       """

        # Don't register abstract classes
        if isabstract(cls):
            return

        # Return if a wrapped_creation_func was not specified
        wrapped = getattr(cls, 'wrapped_creation_func', None)
        if not wrapped:
            return
        elif not callable(wrapped):
            raise TypeError('wrapped_creation_func must be a type or factory method for non-abstract classes!')

        format_name = getattr(cls, 'format_name', None)
        if not format_name:
            format_name = cls.__name__.lower().replace('reader', '')

        cls.by_format_name[format_name] = cls

        file_extensions = getattr(cls, 'file_extensions', None)
        if not file_extensions:
            file_extensions = (format_name,)
        if isinstance(file_extensions, str):
            file_extensions = (file_extensions,)
        file_extensions = set(file_extensions)

        cls.file_extensions_for_class[cls] = file_extensions
        for extension in file_extensions:
            cls.by_file_extension[extension] = cls
            cls.file_extension_to_format_name[extension] = format_name


    @abstractmethod
    def load_source(
            self, source: Union[PathLike, HasRead],
            force_provided_glyphs: Optional[Iterable[str]] = None
    ) -> RasterFont:
        pass


def guess_path_type(path: Optional[PathLike]) -> Optional[str]:
    if path is None:
        return None

    path = Path(path)
    if not path.suffix:
        return 'spritedir' if path.is_dir() else None

    extension = path.suffix[1:]
    path_type = FormatReader.file_extension_to_format_name.get(extension, None)
    return path_type


def guess_source_path_type(source: PathLikeOrHasRead) -> Optional[str]:
    source_path = get_source_filesystem_path(source)
    source_type = guess_path_type(source_path)
    return source_type


class BinaryReader(FormatReader, ABC):
    # This must be specified by subclasses
    wrapped_creation_func: Optional[type] = None


class CachingReader(BinaryReader, ABC):

    def load_source(
            self,
            source: Union[PathLike, HasRead],
            font_size: int = 16,
            provided_glyphs: Optional[Iterable[str]] = None
    ) -> RasterFont:
        stream = SeekableBinaryFileCopy.copy(source)
        original_path = stream.filename

        raw_font = load_and_cache_bitmap_font(
            source, self.wrapped_creation_func, cache=self.cache)
        actual_path = getattr(raw_font, 'file')
        provided_glyphs = self.cache[original_path].provided_glyphs
        raw_glyphs = copy_glyphs(raw_font, provided_glyphs)
        result = RasterFont(raw_glyphs, size_points=font_size,path=actual_path)
        return result


class TextFontReader(FormatReader):
    wrapped_creation_func = TextFontFile

    def load_source(
        self, source: Union[PathLike, HasRead],
        font_size: int = 16,
        force_provided_glyphs: Optional[Iterable[str]] = None
    ) -> RasterFont:
        with StdOrFile(source, 'r') as file:
            raw_font = TextFontFile(file.raw)

        path = get_source_filesystem_path(source)
        provided_glyphs = raw_font.provided_glyphs
        raw_glyphs = copy_glyphs(raw_font, provided_glyphs)

        return RasterFont(raw_glyphs, path=path)


class TrueTypeReader(BinaryReader):
    format_name = 'truetype'
    file_extensions = ['ttf']
    wrapped_creation_func = ImageFont.truetype

    def load_source(
            self, source: Union[PathLike, HasRead],
            font_size: int = 16,
            force_provided_glyphs: Optional[Iterable[str]] = None
    ) -> RasterFont:
        if force_provided_glyphs is None:
            force_provided_glyphs = generate_glyph_sequence()
        with StdOrFile(source, 'rb') as wrapped:
            raw_font = self.__class__.wrapped_creation_func(wrapped.raw)
            path = get_source_filesystem_path(source)

        raw_glyph_table = copy_glyphs(raw_font, glyphs=force_provided_glyphs)
        raster_font = RasterFont(
            glyph_table=raw_glyph_table,
            size_points=font_size,
            path=path
        )
        return raster_font


class BDFReader(CachingReader):
    format_name = 'bdf'
    wrapped_creation_func = BdfFontFile


class PCFReader(CachingReader):
    format_name = 'pcf'
    wrapped_creation_func = PcfFontFile
