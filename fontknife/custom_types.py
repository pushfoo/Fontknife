"""
Common annotations and building blocks used throughout the project

Module members fall into two categories:

    * IO & Streams
    * Image & Font support

IO & Streams heavily lean on Protocols for annotating file-like objects
per Guido van Rossum's advice on the subject:
https://github.com/python/typing/discussions/829#discussioncomment-1150579
"""
from __future__ import annotations
from array import array
from collections import namedtuple
from pathlib import Path
from typing import Tuple, Protocol, Optional, Union, runtime_checkable, Any, TypeVar, Callable, ByteString, Sequence, \
    overload, Iterator, cast, Iterable


T = TypeVar('T')
ValidatorFunc = Callable[[Any, ], bool]


# Partial workaround for there being no way to represent buffer protocol
# support via typing. Relevant PEP: https://peps.python.org/pep-0687/
BytesLike = Union[ByteString, array]

PathLike = Union[Path, str, bytes]
StreamTypeVar = TypeVar('StreamTypeVar')


class StarArgsLengthError(TypeError):
    def __init__(
        self,
        num_args: int,
        min_args: int = 0,
        max_args: int = 1,
        args_name: str = 'args'
    ):
        message =\
            f"Expected {min_args} <= n <= {max_args} arguments in *{args_name}, "\
            f"but got {num_args} args."

        super().__init__(self, message)
        self.num_args = num_args
        self.min_args = min_args
        self.max_args = max_args
        self.args_name = args_name


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


@runtime_checkable
class SequenceLike(Protocol[T]):
    """
    Baseclass for sequence-like Protocols to inherit from.

    It helps define protocols covering both the original sequences and
    classes that imitate sequences without subclassing a sequence type.
    """
    def __iter__(self) -> Iterator[T]:
        ...

    @overload
    def __getitem__(self, item: int) -> T:
        ...

    @overload
    def __getitem__(self, item: slice) -> SequenceLike[T]:
        ...

    def __getitem__(self, item: Union[int, slice]) -> Union[int, SequenceLike[T]]:
        ...

    def __len__(self) -> int:
        ...


@runtime_checkable
class Coord(SequenceLike[int], Protocol):

    def __len__(self) -> int:
        return 2


CoordFancy = namedtuple('CoordFancy', ['x', 'y'])


@runtime_checkable
class Size(SequenceLike[int], Protocol):

    def __len__(self) -> int:
        return 2


SizeFancy = namedtuple('SizeFancy', ['width', 'height'])


@runtime_checkable
class BoundingBox(SequenceLike[int], Protocol):
    """
    Protocol to cover all bounding box behavior.

    It covers the original bounding box tuple behavior, as well as the
    class-based bounding boxes that mimic it.
    """

    def __len__(self) -> int:
        return 4


BboxSimple = Tuple[int, int, int, int]


BboxArgsLikeValue = Union[
    # An *args value that consists of a single sequence-like
    Sequence[SequenceLike[int]],
    # An *args value that is a series of arg
    SequenceLike[int]
]


# Convenience constant for BboxClassABC subclasses
BBOX_EDGE_NAMES = ('left', 'top', 'right', 'bottom')


def _unpack_single_args_member(raw_args: BboxArgsLikeValue) -> SequenceLike:
    """
    Return inner SequenceLike for 1-lengths, otherwise return raw_args.

    :param raw_args: A sequence-like to unpack or return
    :return:
    """
    if len(raw_args) and isinstance(raw_args[0], SequenceLike) == 1:
        return tuple(raw_args[0])
    return raw_args


def _prefix_if_not_long_enough(
    prefix: SequenceLike,
    arg_seq: BboxArgsLikeValue,
    goal_length: int = 4,
) -> SequenceLike:
    """
    Unwrap ``arg_seq``. Return it if long enough, otherwise prefix it.

    This is intended to speed writing __init__ and __new__ methods which
    may take multiple lengths of *args or a single SequenceLike
    equivalent to those lengths of *args.

    :param prefix: The prefix that will be prepended to meet goal length
    :param arg_seq: A potentially wrapped SequenceLike to process.
    :param goal_length: How long the returned SequenceLike should be
    :return:
    """
    # Unwrap the first element if it's an iterable
    unpacked_seq = _unpack_single_args_member(arg_seq)

    seq_len = len(unpacked_seq)
    prefix_len = len(prefix)

    # Return the unwrapped version if it's already the right length
    if seq_len == goal_length:
        return unpacked_seq

    # Raise a value error if we cannot achieve the goal length
    if seq_len + prefix_len != goal_length:
        raise ValueError(
            f"Cannot reach goal length {goal_length}"
            f" by prefixing {prefix!r} of length {prefix_len} to "
            f"{arg_seq!r} of length {seq_len}"
        )

    # Return a prefixed version
    return tuple(prefix) + tuple(unpacked_seq)


def _no_negatives(seq: SequenceLike[T]) -> bool:
    if any(map(lambda a: a < 0, seq)):
        raise ValueError(
            f"All values must be >= 0, but {seq!r} contains negatives")
    return True


def _validate_and_unpack_bbox_like_args(
    prefix: SequenceLike[int],
    arg_seq: BboxArgsLikeValue
):
    unpacked_seq = _unpack_single_args_member(arg_seq)
    _no_negatives(unpacked_seq)
    prefixed = _prefix_if_not_long_enough(prefix, unpacked_seq)
    return prefixed


class CompareByLenAndElementsMixin:
    """
    Ease compatibility when comparing against other sequences.
    """

    def __eq__(self: SequenceLike, other: SequenceLike) -> bool:
        if other is None:
            return False

        len_self = len(self)

        if len(other) != len_self:
            raise ValueError(
                f"Invalid comparison: Bounding boxes must be sequence-like of"
                f" length 4, but got {other}")

        for i in range(len_self):
            if self[i] != other[i]:
                return False
        return True


class HashAsTupleMixin:
    """
    Allows classes to be hashed as if they were tuples.

    Requirements for use:

        1. This is placed early enough in the parent class order to
           ensure __hash__ isn't overridden. Putting this class first
           may be easiest.
        2. The parent class will be in an immutable state when it is
           hashed.
        3. The subclass is sufficiently Sequence-like for tuple() to
           convert it.
    """
    def __hash__(self: SequenceLike):
        return hash(tuple(self))


class BboxFancy(HashAsTupleMixin, CompareByLenAndElementsMixin, tuple):

    @overload
    def __new__(cls, left: int, top: int, right: int, bottom: int) -> BboxFancy:
        return cls.__new__(cls, left, top, right, bottom)

    @overload
    def __new__(cls, right: int, bottom: int) -> BboxFancy:
        return cls.__new__(cls, 0, 0, right, bottom)

    @overload
    def __new__(cls, size: Size):
        return cls.__new__(cls, 0, 0, size[0], size[1])

    @overload
    def __new__(cls, bbox_sequence: BoundingBox) -> BboxFancy:
        return cls.__new__(cls, bbox_sequence)

    def __new__(cls, *args):
        args = _validate_and_unpack_bbox_like_args((0, 0), args)
        return super(BboxFancy, cls).__new__(cls, args)

    # __init__ must be overloaded to match __new__ to make
    # autocomplete to work in IDEs such as PyCharm.
    @overload
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.__init__(left, right, top, bottom)

    @overload
    def __init__(self, right: int, bottom: int):
        self.__init__(right, bottom)

    @overload
    def __init__(self, size: Size):
        self.__init__(size)

    @overload
    def __init__(self, bbox_sequence: BoundingBox):
        self.__init__(bbox_sequence)

    # Setting the indexed values is done by __new__ since this is a
    # tuple subclass, but the other values must be set by __init__
    def __init__(self, *args):
        self._size = SizeFancy(
            self.right - self.left,
            self.bottom - self.top)

    @property
    def size(self) -> Size:
        return self._size

    @property
    def left(self) -> int:
        return self[0]

    @property
    def top(self) -> int:
        return self[1]

    @property
    def right(self) -> int:
        return self[2]

    @property
    def bottom(self) -> int:
        return self[3]

    @property
    def width(self) -> int:
        return self._size.width

    @property
    def height(self) -> int:
        return self._size.height

    def encloses(self, other: Union[Coord, BoundingBox]) -> bool:
        """
        True if the Coord or BoundingBox fits inside this Bbox.

        Coordinates will be treated as a bounding box with their starts
        and ends equal to the coordinate.

        :param other: The object to check for enclosure.
        :return:
        """
        unpacked = _validate_and_unpack_bbox_like_args(other, other)
        left, top, right, bottom = unpacked
        return self.left <= left and self.top <= top and right <= self.right and bottom <= self.bottom

    def __or__(self, other: Union[BoundingBox, Size]) -> BboxFancy:
        args = _validate_and_unpack_bbox_like_args((0, 0), other)
        return BboxFancy(
            # Casting is necessary because zip has ongoing issues with
            # detection as an iterable:
            # https://github.com/python/mypy/issues/8454
            # https://github.com/python/typeshed/pull/3830 (reverted)
            *map(min, cast(Iterable, zip(self[:2], args[:2]))),
            *map(max, cast(Iterable, zip(self[2:], args[2:])))
        )


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
