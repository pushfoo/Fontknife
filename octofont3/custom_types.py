from collections import namedtuple
from dataclasses import dataclass, field
from io import TextIOBase, IOBase
from pathlib import Path
from typing import Tuple, Protocol, Optional, Union, runtime_checkable, Any, TypeVar, Callable


PathLike = Union[Path, str, bytes]
StreamOrPathLike = Union[PathLike, IOBase]
ValidatorFunc = Callable[[Any, ], bool]


@runtime_checkable
class HasRead(Protocol):
    def read(self, hint: int = -1):
        ...


@runtime_checkable
class HasReadline(Protocol):

    def readline(self):
        ...


@runtime_checkable
class HasTextReadline(Protocol):

    def readline(self) -> str:
        ...


@runtime_checkable
class HasBytesReadline(Protocol):

    def readline(self) -> bytes:
        ...


TextIOBaseSubclass = TypeVar("TextIOBaseSubclass", bound=TextIOBase)


Pair = Tuple[int, int]
Size = Tuple[int, int]
SizeFancy = namedtuple('SizeFancy', ['width', 'height'])


BboxSimple = Tuple[int, int, int, int]


@dataclass(frozen=True)
class BboxFancy:
    left: int
    top: int
    right: int
    bottom: int

    width: Optional[int] = field(default=None)
    height: Optional[int] = field(default=None)
    size: Optional[SizeFancy] = field(default=None)
    _cached_tuple: Optional[BboxSimple] = field(
        default=None, init=False, repr=False, compare=False)

    def __len__(self) -> int:
        return 4

    def __post_init__(self):
        object.__setattr__(self, 'width', self.right - self.left)
        object.__setattr__(self, 'height', self.bottom - self.top)
        object.__setattr__(self, 'size', SizeFancy(self.width, self.height))
        object.__setattr__(self, '_cached_tuple', tuple(self))

    def __iter__(self):
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __getitem__(self, index):
        return self._cached_tuple[index]


BoundingBox = Union[BboxFancy, BboxSimple]


class ImageCoreLike(Protocol):
    """
    An attempt at typing the Image.core internal class.

    It's unclear if there's a good way to handle this. While it appears
    to be impossible to hook into pillow's font rendering without using
    Image.core, the pillow source warns that Image.core is not part of
    the public API and may vanish at any time.

    Using Image.core directly does not work with linters because the
    .pyi file for PIL.Image does not provide it. A bad alternative to
    protocols is the following::

        ImageCore = type(Image.new('1', (0, 0), 0).im)

    The protocol approach seems better by comparison.
    """
    mode: str
    size: Size

    def getbbox(self) -> Optional[BoundingBox]:
        """
        Returns None if the core is empty.

        :return:
        """
        ...

    def __len__(self) -> int:
        ...

    def __bytes__(self) -> bytes:
        ...


@runtime_checkable
class ImageFontLike(Protocol):
    """
    The features required for PIL.ImageDraw to use an object as a font
    """

    def getmask(self, text: str) -> ImageCoreLike:
        ...

    def getbbox(self, text: str) -> Optional[BoundingBox]:
        ...
