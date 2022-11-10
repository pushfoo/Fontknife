import math
import string
import sys
from collections import defaultdict
from dataclasses import asdict
from itertools import chain, filterfalse
from typing import Iterable, Tuple, Dict, Optional, Any, Callable, Union, Mapping, overload, TypeVar, cast
from collections.abc import Mapping as MappingABC

from PIL import Image, ImageDraw

from octofont3.custom_types import (
    SequenceLike,
    T, Size, SizeFancy, BoundingBox, BboxFancy,
    ImageFontLike, ValidatorFunc,
    ImageCoreLike, SelectorCallable,
    CompareByLenAndElementsMixin, BboxEnclosureMixin, BBOX_PROP_NAMES
)


def generate_glyph_sequence(
    raw_character_sequence: Optional[Iterable[str]] = None,
    exclude: [Union[Callable,Iterable[str]]] = None
) -> Tuple[str, ...]:
    """
    Generate an output order of strings as keys to glyph data.

    If no arguments are provided, it will return the following ordering::

        0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    Digits are placed first to eliminate offset math for displaying
    scores when working in retro development environments.

    If you desire a different order, pass a value to
    ``raw_character_sequence``. Use ``exclude`` to filter the iterables


    :param raw_character_sequence:
    :param exclude:
    :return:
    """

    # If passed a function, use it to exclude
    if callable(exclude):
        exclude_func = exclude

    else: # We need to generate an exclusion function
        if exclude is None:
            # Exclude everything before space and after base ASCII
            exclude = set(chr(i) for i in chain(range(0, 31), range(128, 255)))
        else:
            # Convert the iterable to a set for efficient lookup
            exclude = set(exclude)

        def exclude_func(s):
            return s in exclude

    if not raw_character_sequence:
        raw_character_sequence = string.printable

    glyph_sequence = tuple(filterfalse(exclude_func, raw_character_sequence))

    return glyph_sequence


def get_bbox_size(bbox: BoundingBox) -> Size:
    left, top, right, bottom = bbox
    return right - left, bottom - top


def get_total_image_size_for_bbox(bbox: BoundingBox) -> Size:
    """
    Return the size of the image that would fit this bounding box.

    :param bbox:
    :return:
    """
    x0, y0, x1, y1 = bbox
    return x1, y1


def show_image_for_text(font, text, mode="RGBA"):
    bbox = font.getbbox(text)
    im = Image.new(mode, get_total_image_size_for_bbox(bbox))
    draw = ImageDraw.Draw(im, mode=mode)
    draw.text((0, 0), text, font=font)

    im.show()


FIELD_NAMES_MAX_LEN: Dict[type, int] = {}


def print_dataclass_info(dataclass_instance, prefix: str = "#", file=sys.stdout):
    instance_as_dict = asdict(dataclass_instance)
    instance_type = type(dataclass_instance)
    if instance_type not in FIELD_NAMES_MAX_LEN:
       FIELD_NAMES_MAX_LEN[instance_type] = max(map(len, instance_as_dict.keys()))

    just_length = FIELD_NAMES_MAX_LEN[instance_type]
    for field, value in instance_as_dict.items():
        print(f"{prefix}   {field.ljust(just_length)} : {value!r}", file=file)


def filter_none(iterable: Iterable[T]) -> Iterable[T]:
    return filter(lambda a: a is not None, iterable)


def get_glyph_bbox(font: ImageFontLike, g: str) -> BoundingBox:
    return BboxFancy(0,0, *font.getmask(g).size)


def get_glyph_bbox_classic(font: ImageFontLike, g: str) -> BoundingBox:
    return font.getbbox(g)


def find_max_dimensions(
    font: ImageFontLike,
    glyphs_to_check: Iterable[str],
    bbox_getter: Callable[[ImageFontLike, str], BoundingBox] = get_glyph_bbox_classic
) -> SizeFancy:
    """
    Get the size of the tile that will fit every glyph requested

    :param font: The font to evaluate
    :param glyphs_to_check: which glyphs to use
    :param bbox_getter: A function to process the font and requested glyphs with
    :return: the max glyph width and max glyph height for the font
    """
    max_width, max_height = 0, 0
    for glyph in glyphs_to_check:
        bbox = bbox_getter(font, glyph)

        if bbox is not None:
            width, height = get_bbox_size(bbox)
            max_width = max(width, max_width)
            max_height = max(height, max_height)

    return SizeFancy(max_width, max_height)


def tuplemap(callable: Callable, iterable: Iterable) -> Tuple:
    return tuple(map(callable, iterable))


def image_from_core(core: ImageCoreLike, mode="L") -> Image.Image:
    # note that this has to start out in mode L or it doesn't work
    initial = Image.frombytes("L", core.size, bytes(core))
    if initial.mode != mode:
        return initial.convert(mode)
    return initial


def show_core(core: ImageCoreLike, mode: str = "L"):
    image_from_core(core, mode=mode).show()


def empty_core(width: int = 0, height: int = 0, mode: str = '1') -> ImageCoreLike:
    return Image.new(mode, (width, height), 0).im


def generate_missing_character_core(
    image_size: Size,
    rectangle_bbox: Optional[BoundingBox] = None,
    mode: str = 'L',
    rectangle_margins_px: int = 1
) -> ImageCoreLike:
    """
    Generate a missing glyph "tofu" square as an image core object.

    :param tofu_size:
    :param mode:
    :return:
    """
    # Calculate dimensions
    image_size = SizeFancy(*image_size)
    if rectangle_bbox is None:
       rectangle_bbox = (
           rectangle_margins_px,
           rectangle_margins_px,
           image_size.width - (1 + rectangle_margins_px),
           image_size.height - (1 + rectangle_margins_px)
       )

    # Draw a rectangle on the image
    image = Image.new(mode, image_size, 0)
    draw = ImageDraw.Draw(image, mode)
    draw.rectangle(rectangle_bbox, outline=255)

    # Return the core for use as a mask
    return image.im


def first_attribute_present(obj: Any, attr_iterable: Iterable[str]) -> Optional[str]:
    """
    Return None or the name of the first attribute found on the object.

    :param obj: The object to search
    :param attr_iterable: An iterable of attribute names to search for
    :return: None or the first attribute found
    """
    for attr in attr_iterable:
        if hasattr(obj, attr):
            return attr
    return None


def value_of_first_attribute_present(
        obj: Any, attr_iterable: Iterable[str], default: Any = None, missing_ok: bool = False) -> Any:
    """
    Search for passed attributes, returning a default or excepting if not found

    The ``strict`` argument determines how failing to find the argument
    is handled:

        * When ``strict`` is False, returns the default
        * When ``strict`` is True, raises an exception

    :param obj: The object to search for attributes
    :param attr_iterable: An iterable of attribute names to search for
    :param default: the default value to return if no element is present
    :param missing_ok: whether to raise an exception if none are found
    :return: The value of an attribute or the default
    """
    # Convert the requested object only if we might need it later
    if missing_ok:
        attr_iterable = tuple(attr_iterable)

    # Check for presence of attributes, returning the first
    first_on_object = first_attribute_present(obj, attr_iterable)
    if first_on_object is not None:
        return getattr(obj, first_on_object)

    # Error if in strict mode, otherwise return a default
    if not missing_ok:
        raise AttributeError(f"Could not find any of following attributes: {attr_iterable}")

    return default


def has_all_attributes(
    obj: Any,
    attribute_names: Iterable[str],
    validator: Optional[Union[Mapping[str, ValidatorFunc], ValidatorFunc]] = None
) -> bool:
    """
    Return True if the object has all attribute names.

    A validator function or mapping of attributes to functions can also
    be passed to make sure all the named attributes meet requirements.

    :param obj: The object to check.
    :param attribute_names: The attributes to check for.
    :param validator: If not None, used to check the attribute values.
    :return:
    """
    if validator and not isinstance(validator, MappingABC):
        validator = defaultdict(lambda: validator)

    for attribute in attribute_names:
        if not hasattr(obj, attribute):
            return False
        if validator and not validator[attribute](getattr(obj, attribute)):
            return False
    return True


DT = TypeVar('DT')


@overload
def get_index(sequence: Optional[SequenceLike[T]], index: int, default: DT) -> Union[T, DT]:
    """
    Attempt to get sequence[index], returning default on any failure.

    Invalid indices will also cause the default to be returned.

    :param sequence: The sequence to fetch from
    :param index: An integer to attempt to use as the index
    :param default: This value will be returned on any failure
    :return:
    """
    return get_index(sequence, index, default)


@overload
def get_index(sequence: SequenceLike[T], index: int) -> T:
    """
    Identical to sequence[index], provided for consistency.

    :param sequence: The sequence to fetch from.
    :param index: The index to get from.
    :return:
    """
    return get_index(sequence, index)


def get_index(sequence: Optional[SequenceLike[T]], index: int, *args: DT) -> Union[T, DT]:
    """
    Get sequence[index] if index valid, raise, or return passed default

    This is wrapped by the overload functions above.

    :param sequence:
    :param index:
    :param args:
    :return:
    """
    if type(index) != int:
        raise TypeError('Index must be an integer')

    # Detect any passed default and use it
    args_len = len(args)
    if args_len not in (0, 1):
        raise ValueError('get_index only accepts 1 extra positional argument!')
    default = None
    use_default = bool(args_len)
    if use_default:
        default = args[0]

    try:
        return sequence[index]

    # Return any provided default on failure, otherwise re-raise exception
    except (IndexError, TypeError) as e:
        if use_default:
            return default
        raise e


def get_attrs(obj: Any, attrs: Iterable[str]) -> Dict[str, Any]:
    """
    Attempt to get requested attrs; a mapping will trigger defaults mode

    If a non-mapping Iterable is passed, no defaults will be passed to
    getattr, and a missing attribute will raise an exception.

    Pairs well with collections.defaultdict.

    :param obj: The object to get attributes from.
    :param attrs: An iterable of attributes to fetch, with mappings
                  treated as default values.
    :return:
    """
    result: Dict[str, Any] = {}

    if isinstance(attrs, Mapping):
        for attr_name, default_value in attrs.items():
            result[attr_name] = getattr(obj, attr_name, default_value)
    else:
        for attr_name in attrs:
            result[attr_name] = getattr(obj, attr_name)

    return result


def attrs_eq(a: Any, b: Any, attrs: Iterable[str]) -> bool:
    """
    Compare the requested attributes on a and b.

    If attrs is a list, tuple, or other non-mapping, all attributes will be
    a hard requirement. If attrs is a mapping, it will be used as defaults
    per the description of get_attrs.

    :param a: Any object.
    :param b: Any object.
    :param attrs: An iterable of attribute names. Any mapping passed will
                  be used as a source of defaults per get_attrs.
    :return:
    """

    # Does not exit early when a is b because of an edge case where:
    #   1. a is b
    #   2. accessing a property causes its return value to change

    a_values = get_attrs(a, attrs).values()
    b_values = get_attrs(b, attrs).values()

    for a_value, b_value in zip(a_values, b_values):
        if a_value != b_value:
            return False
    return True


def copy_from_mapping(
    source: Mapping,
    which_keys: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    Copy keys in which_keys from source, optionally using defaults

    If which_keys is a mapping, its values will be used as a source of
    defaults whenever a key is missing from source.

    :param source: A mapping to copy from.
    :param which_keys: An iterable of keys. May be a dict to set defaults.
    :return:
    """

    if which_keys is None:
        return dict(source)

    copied_dict = {}
    if isinstance(which_keys, Mapping):
        for key in which_keys:
            copied_dict[key] = source.get(key, which_keys[key])
    else:
        for key in cast(Iterable[str], which_keys):
            copied_dict[key] = source.get(key)

    return copied_dict


def has_method(obj: Any, method_name: str) -> bool:
    return callable(getattr(obj, method_name, None))


def has_all_methods(obj: Any, method_names: Iterable[str]) -> bool:
    """
    True if all the named methods exist as callable attributes.

    :param obj:
    :param method_names:
    :return:
    """
    return has_all_attributes(obj, method_names, callable)


class PropUninitializedError(ValueError):
    def __init__(self, prop_name: str):
        super().__init__(
            f"Can't access property {prop_name} when the base value is None!"
            f" Please initialize it!")


@overload
def _select_not_none(chooser: SelectorCallable, candidates: Iterable[T]) -> T:
    return _select_not_none(chooser, *candidates)


@overload
def _select_not_none(chooser: SelectorCallable, *candidates: T) -> T:
    return _select_not_none(chooser, *candidates)


def _select_not_none(chooser: SelectorCallable, *candidates: Optional[T]) -> T:
    if len(candidates) == 1:
        candidates = candidates[0]
    return chooser(tuple(filter_none(candidates)))


@overload
def max_not_none(candidates: Iterable[Optional[T]]) -> T:
    return max_not_none(*candidates)


@overload
def max_not_none(*candidates: Optional[T]) -> T:
    return max_not_none(*candidates)


def max_not_none(*candidates: Optional[T]) -> T:
    return _select_not_none(max, *candidates)

@overload
def min_not_none(candidates: Iterable[Optional[T]]) -> T:
    return min_not_none(*candidates)


@overload
def min_not_none(*candidates: Optional[T]) -> T:
    return min_not_none(*candidates)


def min_not_none(*candidates: Optional[T]) -> T:
    return _select_not_none(min, *candidates)


class BboxEnclosingAll(CompareByLenAndElementsMixin, BboxEnclosureMixin):
    """
    This class grows to enclose all bboxes it's updated from.

    It has some caveats to its usage:

        1. Because it is mutable, it cannot be hashed. Convert it to a
           tuple or a ``BboxFancy`` first.

        2. Attempts to access properties without updating it with values
           will raise a PropUninitializedError.

    """

    def __init__(self, *bboxes: BoundingBox):
        self._left: Optional[int] = None
        self._top: Optional[int] = None
        self._right: Optional[int] = None
        self._bottom: Optional[int] = None

        if bboxes:
            self.update(*bboxes)

    def __getitem__(self, item: int):
        return getattr(self, BBOX_PROP_NAMES[item])

    def __len__(self) -> int:
        return 4

    def __iter__(self):
        yield self._left
        yield self._top
        yield self._right
        yield self._bottom

    @property
    def left(self) -> int:
        if self._left is None:
            raise PropUninitializedError('left')
        return self._left

    @property
    def top(self) -> int:
        if self._top is None:
            raise PropUninitializedError('top')
        return self._top

    @property
    def right(self) -> int:
        if self._right is None:
            raise PropUninitializedError('right')
        return self._right

    @property
    def bottom(self) -> int:
        if self._bottom is None:
            raise PropUninitializedError('bottom')
        return self._bottom

    def update(self, *boxes: BoundingBox) -> None:
        """
        Grow to enclose all bounding boxes passed.

        :param boxes:
        :return:
        """
        # locals for fast access
        min_left = self._left
        min_top = self._top
        max_right = self._right
        max_bottom = self._bottom

        for box in boxes:
            left, top, right, bottom = box

            min_left = min_not_none(min_left, left)
            min_top = min_not_none(min_top, top)
            max_right = max_not_none(max_right, right)
            max_bottom = max_not_none(max_bottom, bottom)

        self._left = min_left
        self._top = min_top
        self._right = max_right
        self._bottom = max_bottom

    def reset(self, *boxes: BoundingBox) -> None:
        self._left = None
        self._top = None
        self._right = None
        self._bottom = None

        if boxes:
            self.update(*boxes)
