import importlib.util
import pkgutil
import re

from pathlib import Path
from typing import Pattern, Any, Dict, Union, Iterable, Optional

from octofont3.custom_types import PathLike, HasRead
from octofont3.formats.common import RasterFont, get_cache, SourceTypeRequiredWhenPiping, guess_source_path_type, UnclearSourceType, \
    FormatReader
from octofont3.formats.common.raster_font import copy_glyphs, RasterFont
from octofont3.formats.common.caching import get_cache, load_and_cache_bitmap_font
from octofont3.formats.common.raster_font import copy_glyphs, RasterFont


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
    expected to continue working smoothly. Everything might break.

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


_here = Path(__file__).parent


# Load reader plugins
default_readers = load_format_plugins(str(_here / 'readers'))


def load_font(
    source: Union[PathLike, HasRead],
    source_type: Optional[str] = None,
    font_size: int = 10,
    cache_dir: Optional[PathLike] = None,
    # Currently only usable with TTFs
    force_provides: Iterable[str] = None,
) -> RasterFont:

    if not source_type:
        if source == '-':
            raise SourceTypeRequiredWhenPiping()

        source_type = guess_source_path_type(source)
        if source_type is None:
            raise UnclearSourceType(source, source_type)

    reader = FormatReader.by_format_name[source_type](get_cache)
    font = reader.load_source(source)
    return font
