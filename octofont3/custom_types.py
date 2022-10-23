"""
Custom types used as annotations or building blocks of larger types.

Module members fall into two categories:

    * IO & Streams
    * Image & Font support

IO & Streams heavily lean on Protocols for annotating file-like objects
per Guido van Rossum's advice on the subject:
https://github.com/python/typing/discussions/829#discussioncomment-1150579
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from array import array
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Protocol, Optional, Union, runtime_checkable, Any, TypeVar, Callable, ByteString, Sequence, \
    Mapping, Dict, Iterable, overload

T = TypeVar('T')
ValidatorFunc = Callable[[Any, ], bool]
SelectorCallable = Union[Callable[[T, ...], T], Callable[[Iterable[T]], T]]

# Partial workaround for there being no way to represent buffer protocol
# support via typing. Relevant PEP: https://peps.python.org/pep-0687/
BytesLike = Union[ByteString, array]

PathLike = Union[Path, str, bytes]
StreamTypeVar = TypeVar('StreamTypeVar')


# Generic stream method Protocols
@runtime_checkable
class HasWrite(Protocol[StreamTypeVar]):
    def write(self, b: StreamTypeVar) -> int:
        ...


@runtime_checkable
class HasRead(Protocol[StreamTypeVar]):
    def read(self, hint: int = -1) -> StreamTypeVar:
        ...


@runtime_checkable
class HasReadline(Protocol[StreamTypeVar]):

    def readline(self) -> StreamTypeVar:
        ...


# Type-specific classes
@runtime_checkable
class HasBytesWrite(Protocol):
    def write(self, b: BytesLike) -> int:
        ...


# Combined path + stream types for resources / loading
PathLikeOrHasRead = Union[HasRead[StreamTypeVar], PathLike]
PathLikeOrHasReadline = Union[HasReadline[StreamTypeVar], PathLike]
PathLikeOrHasWrite = Union[HasWrite[StreamTypeVar], PathLike]
PathLikeOrHasStreamFunc = Union[
    PathLike,
    HasRead[StreamTypeVar],
    HasWrite[StreamTypeVar],
    HasReadline[StreamTypeVar]]


Size = Tuple[int, int]
SizeFancy = namedtuple('SizeFancy', ['width', 'height'])


@runtime_checkable
class BoundingBox(Protocol):
    """
    Protocol to cover all bounding box behavior.

    It covers the original bounding box tuple behavior, as well as the
    class-based bounding boxes that mimic it.
    """

    def __len__(self) -> int:
        return 4

    def __iter__(self):
        ...

    def __getitem__(self, index: int):
        ...


BboxSimple = Tuple[int, int, int, int]


# Convenience constant for BboxClassABC subclasses
BBOX_PROP_NAMES = ('left', 'top', 'right', 'bottom')


class BboxClassABC(ABC):
    """Common functionality for Bounding Box-like classes."""

    def __len__(self) -> int:
        return 4

    @abstractmethod
    def __getitem__(self, item) -> int:
        raise NotImplementedError()

    def __eq__(self, other: BoundingBox) -> bool:
        if len(other) != 4:
            raise ValueError(
                f"Invalid comparison: Bounding boxes must be of value 4, but got {other}")

        for i in range(4):
            if self[i] != other[i]:
                return False
        return True

    def __iter__(self):
        yield self[0]
        yield self[1]
        yield self[2]
        yield self[3]


@dataclass(frozen=True, eq=False)
class BboxFancy(BboxClassABC):
    """A Bounding Box with pre-calculated convenience attributes"""
    left: int
    top: int
    right: int
    bottom: int

    width: Optional[int] = field(default=None, init=False)
    height: Optional[int] = field(default=None, init=False)
    size: Optional[SizeFancy] = field(default=None, init=False)
    _cached_tuple: Optional[BboxSimple] = field(
        default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        # This workaround allows setting instance attributes on a
        # frozen dataclass.
        object.__setattr__(self, 'width', self.right - self.left)
        object.__setattr__(self, 'height', self.bottom - self.top)
        object.__setattr__(self, 'size', SizeFancy(self.width, self.height))
        object.__setattr__(self, '_cached_tuple', tuple(self))

    def __hash__(self) -> int:
        """
        Hash the bbox in a way that will collide with matching tuples.

        This allows the bounding box to be used interchangeably with
        pillow-style bounding boxes.

        :return:
        """
        return hash(tuple(self))

    def __iter__(self):
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __getitem__(self, index: int):
        return self._cached_tuple[index]

    @classmethod
    @overload
    def convert(cls, bbox: BoundingBox):
        cls.convert(*bbox)

    @classmethod
    @overload
    def convert(cls, size: Size):
        cls.convert(*size)

    @classmethod
    def convert(cls, *args: int) -> BboxFancy:
        argc = len(args)

        # handle single length values for size and bbox
        if argc == 1:
            args = args[0]
            argc = len(args)

        # handle a size object, otherwise assume it's 4 long
        if argc == 2:
            args = (0, 0) + args

        return cls(*args)


@runtime_checkable
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

    def getmask(self, text: str, mode: str = '') -> ImageCoreLike:
        ...

    def getbbox(self, text: str) -> Optional[BoundingBox]:
        ...


GlyphMapping = Mapping[str, ImageCoreLike]
GlyphDict = Dict[str, ImageCoreLike]


@dataclass
class GlyphMetadata:
    """
    Keep track of bounding box information about glyphs.

    Glyphs can have empty actual data despite having a bounding box. In
    this case, bitmap_bbox will be None.

    This class does not store the PIL.Image.core object itself because
    doing so causes issues with dataclass library internals.
    """
    bitmap_bbox: Optional[BboxFancy]
    glyph_bbox: BboxFancy
    bitmap_size: Size
    bitmap_len_bytes: int

    @classmethod
    def from_font_glyph(
        cls,
        bitmap: ImageCoreLike,
        glyph_bbox: BoundingBox
    ) -> "GlyphMetadata":

        # get the stated values
        glyph_bbox = BboxFancy(*glyph_bbox)
        bitmap_bbox = None

        if bitmap is not None:
            bitmap_bbox = bitmap.getbbox()
            if bitmap_bbox is not None:
                bitmap_bbox = BboxFancy(*bitmap_bbox)

        return cls(
            glyph_bbox=glyph_bbox,
            bitmap_bbox=bitmap_bbox,
            bitmap_size=SizeFancy(*bitmap.size),
            bitmap_len_bytes=len(bitmap)
        )


class MissingGlyphError(Exception):
    """
    1 or more required glyphs were not found.

    Does not subclass Key or Index errors because the underlying
    representation below may be either.
    """
    def __init__(self, message_header, missing_glyph_codes: Sequence[int]):
        super().__init__(f"{message_header} : {missing_glyph_codes}")
        self.missing_glyph_codes = missing_glyph_codes

    @classmethod
    def default_msg(cls, missing_glyph_codes: Sequence[int]):
        cls(
            "One or more required glyphs was found to be missing",
            missing_glyph_codes)
