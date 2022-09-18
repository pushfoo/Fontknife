from collections import namedtuple
from dataclasses import dataclass, field
from typing import Tuple, Protocol, Optional, Union, Dict, List, runtime_checkable, Any

from PIL import Image

Pair = Tuple[int, int]

Size = Tuple[int, int]
SizeFancy = namedtuple('SizeFancy', ['width', 'height'])



# BboxFancy = namedtuple('BboxFancy', ['left', 'top', 'right', 'bottom'])
@dataclass(frozen=True)
class BboxFancy:
    left: int
    top: int
    right: int
    bottom: int

    width: Optional[int] = field(default=None)
    height: Optional[int] = field(default=None)
    size: Optional[SizeFancy] = field(default=None)

    def __len__(self) -> int:
        return 4

    def __post_init__(self):
        object.__setattr__(self, 'width', self.right - self.left)
        object.__setattr__(self, 'height', self.bottom - self.top)
        object.__setattr__(self, 'size', SizeFancy(self.width, self.height))

    def __iter__(self):
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __getitem__(self, index):
        return tuple(self)[index]


BoundingBox = Union[BboxFancy, Tuple[int, int, int, int]]

@runtime_checkable
class ImageFontLike(Protocol):
    """
    Describes the required behavior to be used as a font by pillow.

    If it meets this protocol's requirements, it should work with ImageDraw.
    """

    # Dangerous! Pillow's Image.py warns that this may change
    def getmask(self, text: str) -> Image.core:
        ...

    def getbbox(self, text: str) -> Optional[Union[BoundingBox, BboxFancy]]:
        ...

GlyphTableEntry = Optional[Any]


# This seems to interact poorly with Imaging.core
@runtime_checkable
class FontWithGlyphTable(Protocol):
    """
    A font with a glyph table.

    The dict is this tool's "new" style, while the list of Image.core
    instances or None is the old-style ASCII bitfont.
    """
    glyph: Union[Dict[int, Any], List[Optional[Any]]]
