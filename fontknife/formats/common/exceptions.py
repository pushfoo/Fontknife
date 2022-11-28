from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any

from fontknife.custom_types import PathLike


class FontFormatError(Exception, ABC):

    def __init__(
        self,
        path: Optional[PathLike] = None,
        format_name: Optional[Any] = None,
        message: Optional[str] = None
    ):
        super().__init__(message or self._gen_message(path, format_name))
        self.path = path

    @abstractmethod
    def _gen_message(self, path, source_type) -> str:
        ...


class FontFormatLoadingError(FontFormatError, ABC):
    pass


class FontFormatWritingError(FontFormatError, ABC):
    pass


class UnclearSourceFontFormat(FontFormatError):

    def _gen_message(self, path, source_type) -> str:
        return f"Could not resolve a source font format for {path!r}. Please specify it directly."


class UnclearOutputFontFormat(FontFormatWritingError):
    def _gen_message(self, path, source_type) -> str:
        return f"Could not resolve an output font format for {path!r}. Please specify it directly."


class PipingFromStdinRequiresFontFormat(UnclearSourceFontFormat):

    def _gen_message(self, path, source_type) -> str:
        return "You must specify a source type when piping from stdin."


class PipingToStdoutRequiresFontFormat(UnclearSourceFontFormat):

    def _gen_message(self, path, source_type) -> str:
        return "You must specify an source type when piping from stdin."


class FontFormatRequiresGlyphSequence(FontFormatError):

    def _gen_message(self, path, source_type) -> str:
        return f"Specifying glyphs sequence is mandatory for {source_type!r}"
