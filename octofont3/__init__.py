from dataclasses import dataclass, field
from functools import cache
from typing import Dict, Tuple, Iterable, Optional, Protocol

from PIL import ImageFont, Image

Size = Tuple[int, int]
BoundingBox = Tuple[int, int, int, int]


class ImageFontLike(Protocol):
    """
    Something that behaves like a pillow ImageFont.

    """
    def getmask(self, text: str) -> Image:
        ...

    def getbbox(self, text: str) -> BoundingBox:
        ...

    @property
    def size(self) -> int:
        ...


def calculate_alignments(vert_center: Iterable[str] = None, vert_top: Iterable[str] = None) -> Dict:
    alignments = {}
    vert_center = set(vert_center) if vert_center else set("~=%!#$()*+/<>@[]\{\}|")
    alignments["center"] = vert_center

    vert_top = set(vert_top) if vert_top else set("^\"\'`")
    alignments["top"] = vert_top

    return alignments


class CachingFontWrapper:
    """
    Mimics font object API & caches returns for certain calls

    Currently used in Textfont generation.

    :param font: The font object wrapped
    :param size: An optional override for storing size
    :param alignments: Overriding alignment data, if any
    :return:
    """
    def __init__(
        self,
        font: ImageFontLike,
        size: Optional[int] = None,
        alignments: Optional[Dict] = None
    ):
        self._font = font
        self._size = size
        self._path = getattr(font, 'path', None)

        if alignments is not None:
            self._alignments = alignments
        else:
            self._alignments = calculate_alignments()

    @property
    def path(self):
        return self._path

    @property
    def size(self):

        if self._size:
            return self._size

        return self._font.size

    @property
    def alignments(self) -> Dict:
        return self._alignments

    @property
    def font(self) -> ImageFont:
        return self._font

    @cache
    def getmask(self, text: str, mode: str = "1"):
        return self._font.getmask(text, mode)

    @cache
    def getbbox(self, text: str, mode: str = "1") -> Tuple[int, int, int, int]:
        return self.getmask(text, mode).getbbox()

