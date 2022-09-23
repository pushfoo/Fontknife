from pathlib import Path
from typing import Optional

from PIL import ImageFont

from octofont3.custom_types import PathLike
from octofont3.font_adapter import CachingFontAdapter
from octofont3.formats.bdf import load_bdf
from octofont3.formats.caching import get_cache, load_and_cache_bitmap_font


from octofont3.formats.pcf import load_pcf
from octofont3.formats.textfont.parser import TextFontFile


class FontLoadingError(Exception):
    pass


class MissingExtension(FontLoadingError):
    def __init__(self, path: PathLike):
        super().__init__(f"Could not find a file extension on {str(path)}")
        self.path = path

class UnrecognizedExtension(FontLoadingError):
    def __init__(self, path: PathLike):
        super(UnrecognizedExtension, self).__init__(f"Could not recognize file extension on {str(path)}")
        self.path = path


def load_font(
    path: PathLike,
    font_size: int,
    required_glyphs: str,
    cache_dir: Optional[PathLike] = None,
    force_type: Optional[str] = None
) -> CachingFontAdapter:

    if not isinstance(path, Path):
        str_path = path
        path = Path(path)
    else:
        str_path = str(path)
        path = path

    file_type = path.suffix[1:] if force_type is None else force_type
    if file_type == '':
        raise MissingExtension(path)

    if file_type == "ttf":
        raw_font = ImageFont.truetype(str_path, font_size)
    elif file_type == 'bdf':
        with open(path, "rb") as raw_file:
            raw_font = load_and_cache_bitmap_font(
                str_path,
                load_bdf,
                cache=get_cache(cache_directory=cache_dir)
            )
    elif file_type == 'pcf':
        with open(path, "rb") as raw_file:
            raw_font = load_and_cache_bitmap_font(
                str_path,
                load_pcf,
                cache=get_cache(cache_directory=cache_dir)
            )
    elif file_type == "textfont":
        with open(path, "r") as raw_file:
            raw_font = TextFontFile(raw_file)
    else:
        raise UnrecognizedExtension(path)

    return CachingFontAdapter(raw_font, required_glyphs)
