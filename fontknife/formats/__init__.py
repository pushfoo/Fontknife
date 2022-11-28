import importlib.util
import pkgutil
import re
from pathlib import Path
from typing import Pattern, Any, Dict, Union, Iterable, Optional, Type

from fontknife.custom_types import PathLike, HasRead, PathLikeOrHasWrite
from fontknife.formats.common import RasterFont, get_cache, FormatReader, FormatWriter
from fontknife.formats.common.exceptions import (
    UnclearSourceFontFormat, UnclearOutputFontFormat,
    PipingFromStdinRequiresFontFormat, PipingToStdoutRequiresFontFormat
)
from fontknife.formats.common.caching import get_cache, load_and_cache_bitmap_font
from fontknife.formats.common.raster_font import rasterize_font_to_tables, RasterFont
from fontknife.formats.common.raster_font import rasterize_font_to_tables, RasterFont

# Import built-in format handlers, triggering auto-registration
import fontknife.formats.readers
import fontknife.formats.writers

# Matches anything that is approximately a non-dunder python module name.
# Digits are allowed after the first character for convenience.
VALID_FORMAT_NAME_REGEX = re.compile(r'^[a-z][a-z\d]*(_[a-z\d])*$')


def load_format_plugins(
    where: Union[PathLike, Iterable[PathLike]],
    regex: Pattern = VALID_FORMAT_NAME_REGEX
) -> Dict[str, Any]:
    """
    Attempt to import .py files matching ``regex`` in location(s).

    Note: this project is not yet stable enough for plugins to be
    expected to continue working smoothly. Everything might break,
    including this method.

    Since format subclasses are registered by __init_subclass__ on their
    base class, the actual modules do not have to be returned. However,
    you can keep them around for diagnostic convenience or logging.

    :param where: Where to look as a single path or an iterable of them.
    :param regex: A regex specifying valid names.
    :return:
    """
    discovered = {}

    if isinstance(where, PathLike.__args__):
        # Convert single instances to a list of 1 entry
        search_dirs = [str(where)] if isinstance(where, Path) else [where]
    else:
        # Convert iterables to a list for debugging convenience
        search_dirs = list(where)

    # Load all modules matching the regex.
    # Conflict handling for formats should be handled in the
    # __init_subclass__ methods of base readers & writers, not here.
    for finder, name, ispkg in pkgutil.iter_modules(search_dirs):
        if regex.match(name):
            path_str = str(Path(finder.path) / f"{name}.py")
            spec = importlib.util.spec_from_file_location(name, path_str)
            loaded_raw = importlib.util.module_from_spec(spec)
            discovered[name] = loaded_raw
            spec.loader.exec_module(loaded_raw)

    return discovered


def load_font(
    source: Union[PathLike, HasRead],
    format: Optional[str] = None,
    **kwargs
) -> RasterFont:

    if not format:
        if source == '-':
            raise PipingFromStdinRequiresFontFormat()
        format = FormatReader.guess_format_name(source)

    reader_type: Optional[Type[FormatReader]] = FormatReader.by_format_name.get(format, None)
    if reader_type is None:
        raise UnclearSourceFontFormat(source, format)

    reader = reader_type(get_cache)
    font = reader.load_source(source, **kwargs)
    return font


def write_font(
    font: RasterFont,
    output: PathLikeOrHasWrite,
    format: Optional[str] = None,
    **kwargs
) -> None:

    if not format:
        if output == '-':
            raise PipingToStdoutRequiresFontFormat()
        format = FormatWriter.guess_format_name(output)

    writer_type: Optional[Type[FormatWriter]] = FormatWriter.by_format_name.get(format, None)
    if writer_type is None:
        raise UnclearOutputFontFormat(output, format)

    writer = writer_type()
    writer.write_output(font, output, **kwargs)
