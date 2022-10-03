from abc import ABC, abstractmethod
from contextlib import ExitStack
from io import IOBase
from pathlib import Path
from typing import Optional, Iterable, Union, Any

from PIL import ImageFont
from PIL.BdfFontFile import BdfFontFile
from PIL.PcfFontFile import PcfFontFile

from octofont3.custom_types import PathLike, HasRead
from octofont3.font_adapter import CachingFontAdapter
from octofont3.formats.caching import get_cache, load_and_cache_bitmap_font


from octofont3.formats.textfont.parser import TextFontFile
from octofont3.iohelpers import guess_path_type, get_stream_filesystem_path, StdOrFile, SeekableBinaryFileCopy
from octofont3.utils import generate_glyph_sequence


class FontLoadingError(Exception, ABC):

    def __init__(self, path: PathLike, source_type: Any, message: str = None):
        super().__init__(message or self._gen_message(path, source_type))
        self.path = path

    @abstractmethod
    def _gen_message(self, path, source_type) -> str:
        ...


class UnclearSourceType(FontLoadingError):

    def _gen_message(self, path, source_type) -> str:
        return f"Could not resolve a source type for {path!r}. Please specify it directly."


class InvalidSourceType(FontLoadingError):
    def _gen_message(self, path, source_type) -> str:
        return f"Invalid source type {source_type!r}"


class FormatRequiresGlyphSequence(FontLoadingError):
    def _gen_message(self, path, source_type) -> str:
        return f"Specifying glyphs sequence is mandatory for {source_type!r}"


def load_font(
    source: Union[PathLike, IOBase],
    source_type: Optional[str] = None,
    font_size: int = 10,
    cache_dir: Optional[PathLike] = None,
    # Currently only usable with TTFs
    force_provides: Iterable[str] = None,
) -> CachingFontAdapter:

    # Attempt to copy the font data to memory
    with ExitStack() as es:

         # Load the specified file if needed
         if isinstance(source, (Path, str)):
             input_stream = es.enter_context(StdOrFile(source, 'r')).raw
         else:
             input_stream = source

         source = SeekableBinaryFileCopy.copy(input_stream)

    str_original_path = get_stream_filesystem_path(source)
    original_path = None if str_original_path is None else Path(str_original_path)
    path_actually_loaded_from = original_path

    source_type = source_type or guess_path_type(original_path)
    if source_type is None:
        raise UnclearSourceType(original_path, source_type)

    # Begin loading by checking for different types
    if source_type == "textfont":
        raw_font = TextFontFile(source)
        provided_glyphs = raw_font.provided_glyphs

    elif source_type == "ttf":
        raw_font = ImageFont.truetype(source, font_size)
        # temp fix for being unable to probe TTF sequences
        if force_provides:
            provided_glyphs = tuple(force_provides)
        else:
            provided_glyphs = generate_glyph_sequence()

    else:  # Handle cachable binary fonts

        cache = get_cache(cache_directory=cache_dir)
        if source_type == 'bdf':
            font_type = BdfFontFile
        elif source_type == 'pcf':
            font_type = PcfFontFile
        else:
            raise InvalidSourceType(original_path, source_type)

        raw_font = load_and_cache_bitmap_font(source, font_type, cache=cache)
        path_actually_loaded_from = getattr(raw_font, 'file')
        provided_glyphs = cache[original_path].provided_glyphs

    return CachingFontAdapter(raw_font, provided_glyphs=provided_glyphs, path=path_actually_loaded_from)
