from abc import ABC, abstractmethod
from typing import Optional, Iterable, Union, Any


from octofont3.custom_types import PathLike, HasRead
from octofont3.formats import guess_source_path_type, FormatReader, RasterFont
from octofont3.formats.caching import get_cache


class FontLoadingError(Exception, ABC):

    def __init__(self, path: PathLike = None, source_type: Any = None, message: str = None):
        super().__init__(message or self._gen_message(path, source_type))
        self.path = path

    @abstractmethod
    def _gen_message(self, path, source_type) -> str:
        ...


class UnclearSourceType(FontLoadingError):

    def _gen_message(self, path, source_type) -> str:
        return f"Could not resolve a source type for {path!r}. Please specify it directly."


class SourceTypeRequiredWhenPiping(UnclearSourceType):

    def _gen_message(self, path, source_type) -> str:
        return "You must specify an source type when piping from stdin."


class FormatRequiresGlyphSequence(FontLoadingError):

    def _gen_message(self, path, source_type) -> str:
        return f"Specifying glyphs sequence is mandatory for {source_type!r}"


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
