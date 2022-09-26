from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Iterable

from PIL import ImageFont

from octofont3.custom_types import PathLike
from octofont3.font_adapter import CachingFontAdapter
from octofont3.formats.bdf import load_bdf
from octofont3.formats.caching import get_cache, load_and_cache_bitmap_font


from octofont3.formats.pcf import load_pcf
from octofont3.formats.textfont.parser import TextFontFile
from octofont3.utils import generate_glyph_sequence


class FontLoadingError(Exception, ABC):

    def __init__(self, path: PathLike, message: str = None):
        super().__init__(message or self._gen_message(path))
        self.path = path

    @abstractmethod
    def _gen_message(self, path) -> str:
        ...


class MissingExtension(FontLoadingError):

    def _gen_message(self, path) -> str:
        return f"Could not find a file extension on {str(path)}"


class UnrecognizedExtension(FontLoadingError):
    def _gen_message(self, path) -> str:
        return f"Could not recognize file extension on {str(path)}."


class FormatRequiresGlyphSequence(FontLoadingError):
    def _gen_message(self, path) -> str:
        return f"Loading a font of this format makes specifying glyph sequence mandatory: {str(path)}"


def load_font(
    path: PathLike,
    font_size: Optional[int] = None,
    cache_dir: Optional[PathLike] = None,
    # only usable with TTFs
    force_provides: Iterable[str] = None,
    force_type: Optional[str] = None
) -> CachingFontAdapter:


    if not isinstance(path, Path):
        str_path = path
        path = Path(path)
    else:
        str_path = str(path)
        path = path

    if force_type:
        file_type = force_type
    elif not path.suffix:
        raise MissingExtension(path)
    else:
        file_type = path.suffix[1:]

    cache = get_cache(cache_directory=cache_dir)


    if file_type == "ttf":
        raw_font = ImageFont.truetype(str_path, font_size)
        # temp fix for being unable to probe TTF sequences
        provided_glyphs = tuple(force_provides) or generate_glyph_sequence()

    elif file_type == 'bdf':
        with open(path, "rb") as raw_file:
            raw_font = load_and_cache_bitmap_font(
                str_path,
                load_bdf,
                cache=cache
            )
            provided_glyphs = cache[path].provided_glyphs
    elif file_type == 'pcf':
        with open(path, "rb") as raw_file:
            raw_font = load_and_cache_bitmap_font(
                str_path,
                load_pcf,
                cache=cache
            )
            provided_glyphs = cache[path].provided_glyphs

    elif file_type == "textfont":
        with open(path, "r") as raw_file:
            raw_font = TextFontFile(raw_file)
        provided_glyphs = raw_font.provided_glyphs

    else:
        raise UnrecognizedExtension(path)

    #if not hasattr(raw_font, 'glyph') and required_glyphs is None:
    #    raise FormatRequiresGlyphSequence(path)

    return CachingFontAdapter(raw_font, provided_glyphs=provided_glyphs)
