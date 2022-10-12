"""
Custom types for annotations, falling into two categories:

    * IO & Streams
    * Image & Font support

IO & Streams heavily lean on Protocols for annotating file-like objects
per Guido van Rossum's advice on the subject:
https://github.com/python/typing/discussions/829#discussioncomment-1150579
"""
from array import array
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Protocol, Optional, Union, runtime_checkable, Any, TypeVar, Callable, ByteString, Sequence

ValidatorFunc = Callable[[Any, ], bool]


# Partial workaround for there being no way to represent buffer protocol
# support via typing. Relevant PEP: https://peps.python.org/pep-0687/
BytesLike = Union[ByteString, array]


PathLike = Union[Path, str, bytes]
InputTypeVar = TypeVar('InputTypeVar')
OutputTypeVar = TypeVar('OutputTypeVar')


# Generic stream method classes
@runtime_checkable
class HasWrite(Protocol[InputTypeVar]):
    def write(self, b: InputTypeVar) -> InputTypeVar:
        ...


@runtime_checkable
class HasRead(Protocol[OutputTypeVar]):
    def read(self, hint: int = -1) -> OutputTypeVar:
        ...


@runtime_checkable
class HasReadline(Protocol[OutputTypeVar]):

    def readline(self) -> OutputTypeVar:
        ...


# Type-specific classes
@runtime_checkable
class HasBytesWrite(Protocol):
    def write(self, b: BytesLike) -> bytes:
        ...


# These function as generics
PathLikeOrHasRead = Union[HasRead[InputTypeVar], PathLike]
PathLikeOrHasReadline = Union[HasReadline[InputTypeVar], PathLike]


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

    It's unclear if there's a good way to handle this. Using Image.core
    appears to be crucial to interacting with font drawing in pillow,
    but the pillow source also warns that Image.core is not part of
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

    def getpixel(self, position: Sequence) -> Union[int, Tuple[int, ...]]:
        """
        Returns the value for a pixel in the image.

        :param position:
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
