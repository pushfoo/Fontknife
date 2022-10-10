import string
import sys
from collections import defaultdict
from dataclasses import asdict
from itertools import chain, filterfalse
from typing import Iterable, Tuple, Dict, Optional, Any, Callable, Union, Mapping
from collections.abc import Mapping as MappingABC

from PIL import Image, ImageDraw

from octofont3.custom_types import BoundingBox, Size, ImageFontLike, SizeFancy, BboxFancy, ValidatorFunc, ImageCoreLike


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


def filternone(iterable: Iterable):
    return filter(lambda a: a is None, iterable)


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


