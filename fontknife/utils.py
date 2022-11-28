import re
import string
import sys
from collections import defaultdict
from dataclasses import asdict
from itertools import chain, filterfalse
from typing import Iterable, Tuple, Dict, Optional, Any, Callable, Union, Mapping, overload, TypeVar, Hashable, \
    Pattern, Generator, MutableMapping
from collections.abc import Mapping as MappingABC

from PIL import Image, ImageDraw

from fontknife.custom_types import (
    SequenceLike,
    T, Size, SizeFancy, BoundingBox, BboxFancy,
    ImageFontLike, ValidatorFunc,
    ImageCoreLike,
    StarArgsLengthError
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


ValueT = TypeVar('ValueT')


def tuplemap(callable: Callable, iterable: Iterable[ValueT]) -> Tuple:
    return tuple(map(callable, iterable))


def empty_image(size: Size, mode: str = '1', fill=0) -> Image.Image:
    return Image.new(mode, size, fill)


def image_from_core(
    core: ImageCoreLike,
    image_size: Optional[Size] = None,
    mode: Optional[str] = None,
    fill=0
) -> Image.Image:
    """
    Convert bare bitmap cores to images.

    .. warning:: Set `image_size` to prevent errors on 0-length cores!

                 Although PIL allows zero-size images to be created,
                 they will raise SystemErrors about tiles extending
                 outside images when composing images.

    If `image_size` is larger than the core, the value of `fill` will
    be visible in the background behind the pasted core.

    This function is primarily useful for inspecting glyph mask data.
    Drawing RasterFont objects with the ImageDraw module is more
    effective and efficient for working with sprite sheets.

    :param core: An imaging core object.
    :param image_size: Force an image size instead of the core's size.
    :param mode: A valid PIL image mode.
    :param fill: Fill the image background with this before pasting.
    :return:
    """
    if image_size is None:
        image_size = core.size
    composite = Image.new(mode or core.mode, tuple(image_size), color=fill)

    # Skip pasting if there's no image data
    if len(core):
        # Convert to image of the goal color mode and paste into composite
        to_paste = Image.frombytes(core.mode, tuple(core.size), bytes(core))
        if to_paste.mode != mode:
            to_paste = to_paste.convert(mode)
        composite.paste(to_paste)

    return composite


def show_core(core: ImageCoreLike, image_size: Size = None, mode: Optional[str] = None, fill = 0) -> None:
    """
    Preview the contents of a core using a system image viewer.

    .. warning:: Set `image_size` to prevent errors on 0-length cores!

                 Although PIL allows zero-size images to be created,
                 they will raise SystemErrors about tiles extending
                 outside images when previewing images.

    If `image_size` is larger than the core, the value of `fill` will
    be visible in the background behind the pasted core.

    :param core: A PIL image core.
    :param image_size: An image size to force.
    :param mode: A valid PIL image mode.
    :param fill: A valid PIL fill value.
    :return:
    """
    image_from_core(core, image_size=image_size, mode=mode or core.mode, fill=fill).show()


def empty_core(width: int = 0, height: int = 0, mode: str = '1') -> ImageCoreLike:
    return Image.new(mode, (width, height), 0).im


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


# Typing helpers for mappings
KeyT = TypeVar('KeyT', bound=Hashable)
NewKeyT = TypeVar('NewKeyT', bound=Hashable)
MappingT = Mapping[KeyT, ValueT]
KeyAndOrDefaultSource = Union[Iterable[KeyT], Mapping[KeyT, ValueT]]
ValueSource = Union[object, MappingT]
ReturnDict = Dict[KeyT, ValueT]


# Ugly but explicitly clear workaround for overloads not working
# with type hinting as initially expected.
GetterCallable = Union[
    # Attribute-based getters such as getattr
    Callable[[object, str, ValueT], ValueT],
    Callable[[object, str], ValueT],
    # Non-modifying mapping getters
    Callable[[MappingT, KeyT, ValueT], ValueT],
    Callable[[MappingT, KeyT], ValueT],
    # Destructive getters for removing items from mappings
    Callable[[MutableMapping[KeyT, ValueT], KeyT, ValueT], ValueT],
    Callable[[MutableMapping[KeyT, ValueT], KeyT], ValueT],
]
GetterPartialArgs = Union[Tuple[KeyT], Tuple[KeyT, Optional[KeyT]]]


@overload
def getvalue(source: MappingT, key: KeyT) -> ValueT:
    return getvalue(source, key)


@overload
def getvalue(source: MappingT, key: KeyT, default: Optional[ValueT]) -> Optional[ValueT]:
    return getvalue(source, key, default)


def getvalue(source: MappingT, key: KeyT, *default: ValueT) -> ValueT:
    """
    Get a value from source, or raise a KeyError if absent + no default

    Mimics the signature and behavior of getvalue to allow more
    consistent iteration behavior.

    :param source: The mapping to get a value from.
    :param key: The key to get a value for.
    :param default: The default to use if not found.
    :return:
    """
    default_len = len(default)

    if default_len > 1:
        raise StarArgsLengthError(default_len, max_args=1, args_name='default')

    elif default_len and key not in source:
        return default[0]

    return source[key]


def detect_getter_for_source(value_source: ValueSource) -> GetterCallable:
    return getvalue if isinstance(value_source, Mapping) else getattr


@overload
def get(
    value_source: ValueSource,
    key: str,
    getter: Optional[GetterCallable] = None
) -> ValueT:
    return get(value_source, key, getter=getter)


@overload
def get(
    value_source: ValueSource,
    key: str,
    default: ValueT,
    getter: Optional[GetterCallable] = None
) -> ValueT:
    return get(value_source, key, default, getter=getter)


def get(
    value_source: ValueSource,
    key: str,
    *default: ValueT,
    getter: Optional[GetterCallable] = None
) -> ValueT:
    """
    Generic getter for single attribute calls on mappings or generic objects.

    You may specify a getter to override auto-detection for cases such as
    a mapping object with an attribute you would like to fetch.

    :param value_source: An object to get a value from.
    :param key: The mapping key or attribute name to get.
    :param default: An single optional value to get.
    :param getter: Override getter auto-detection. If not specified,
                   getvalue will be used if value_source is a mapping,
                   otherwise get_attr will be used.
    :return:
    """
    getter = getter or detect_getter_for_source(value_source)

    default_len = len(default)

    if default_len > 1:
        raise StarArgsLengthError(default_len, max_args=1, args_name='default')
    elif default_len:
        return getter(value_source, key, default[0])

    return getter(value_source, key)


def yield_partial_getter_args(key_source: KeyAndOrDefaultSource) -> Generator[GetterPartialArgs, None, None]:
    """
    Generate partial args for a getter for each entry in key_source

    If key_source is a mapping, this will be (key, value). Otherwise, it
    will be a 1-length tuple consisting only of the key.

    :param key_source: An iterable of keys.
    :return:
    """

    if isinstance(key_source, Mapping):
        for pair in key_source.items():
            yield pair
    else:
        for key in key_source:
            yield key,


def get_all(
    value_source: ValueSource,
    keys_and_or_defaults: KeyAndOrDefaultSource,
    getter: Optional[GetterCallable] = None
) -> Dict[KeyT, ValueT]:
    """
    Get values by their names/keys from an object or mapping.

    It homogenizes access to make passing config easier. You can
    override getter behavior detection by passing a specific getter
    function for ambiguous cases such as copying attributes from mapping
    objects.

    If no getter is passed, then keys_and_or_defaults will be handled
    in one of two ways:

        1. If getter is a simple linear iterable, all keys/attributes
           in keys_or_defaults must be present. If any are missing, a
           KeyError or AttributeError will be raised.

        2. If getter is a mapping, any keys or attributes missing from
           value_source will be filled using a corresponding value. This
           works well with dicts or defaultdicts to provide fillers or
           defaults.

    This function omits built-in index-based access because:
        1. It may be unnecessary with the new CLI flag design
        2. It would make this function more complicated

    :param value_source: Where to get values from.
    :param keys_and_or_defaults: A simple linear iterable or mapping.
    :param getter: Manually specify a getter function. If not specified,
                   getvalue will be used if value_source is a mapping,
                   otherwise get_attr will.
    :return:
    """
    getter = getter or detect_getter_for_source(value_source)

    result = dict()

    for partial_args in yield_partial_getter_args(keys_and_or_defaults):
        result[partial_args[0]] = getter(value_source, *partial_args)

    return result


def get_attrs(obj: Any, attrs: Iterable[str]) -> Dict[str, ValueT]:
    """
    Attempt to get requested attrs; a mapping will trigger defaults mode

    If attrs is a non-mapping Iterable, any missing attributes will raise
    an AttributeError. See the documentation for get for more information.

    If attrs is a mapping, its values will be used as defaults. Pairs well
    with `collections.defaultdict`.

    :param obj: The object to get attributes from.
    :param attrs: An iterable of attributes to fetch, with mappings
                  treated as default values.
    :return:
    """
    result = get_all(obj, attrs, getter=getattr)
    return result


def attrs_eq(a: Any, b: Any, attrs: Iterable[str]) -> bool:
    """
    Compare the requested attributes on a and b.

    If attrs is a simple non-mapping iterable, all attributes are required.
    If attrs is a mapping, its values will be used as default values.

    :param a: Any object.
    :param b: Any object.
    :param attrs: An iterable of attribute names. Any mapping passed will
                  be used as a source of defaults per get_attrs.
    :return:
    """

    # Does not exit early when a is b because of an edge case where:
    #   1. a is b
    #   2. accessing a property causes its return value to change

    # Does not use get_all to ensure compatibility with consumable
    # iterables such as generators.

    for partial_args in yield_partial_getter_args(attrs):
        a_val = get(a, *partial_args, getter=getattr)
        b_val = get(b, *partial_args, getter=getattr)

        if a_val != b_val:
            return False

    return True


def copy_from_mapping(
    source: Mapping,
    which_keys: Optional[Iterable[str]] = None,
    getter: GetterCallable = getvalue
) -> Dict[str, Any]:
    """
    Copy keys in which_keys from source, optionally using defaults

    If which_keys is a mapping, its values will be used as a source of
    defaults whenever a key is missing from source.

    This function's behavior can be changed by passing a custom getter,
    such as using a getter which deletes items from the dict.

    :param source: A mapping to copy from.
    :param which_keys: An iterable of keys. Mappings will be used as
                       sources of defaults.
    :param getter: A getter function. Override to customize behavior.
    :return:
    """

    if which_keys is None:
        return dict(source)
    return get_all(source, which_keys, getter=getter)


def remap(
    source: Mapping[KeyT, ValueT],
    remapping_table: Mapping[KeyT, NewKeyT],
) -> Dict[NewKeyT, ValueT]:
    """
    Copy specified elements to a new dict under replacement names.

    Important: unlike other collection helpers, there are no ways
    to specify defaults. All keys must be in the dictionary.

    :param source: A mapping to copy from
    :param remapping_table: pairs of old_key, new_key to store values
                            under.
    :return:
    """
    remapped = {}
    for old_key, new_key in remapping_table.items():
        remapped[new_key] = source[old_key]
    return remapped


def ensure_compiled(pattern: Union[str, Pattern]) -> Pattern:
    if isinstance(pattern, Pattern):
        return pattern
    return re.compile(pattern)


def extract_matching_keys(
    source: Iterable[str],
    pattern: Union[str, Pattern],
) -> Tuple[str, ...]:
    """
    Return a tuple of all keys which match the pattern.

    This can be used with both Dict[str, Any] and simple iterables.

    :param source: an iterable of string keys to search
    :param pattern: a regex as a string or compiled Pattern
    :return: all keys which match the pattern.
    """
    compiled = ensure_compiled(pattern)
    matching_keys = tuple(filter(compiled.match, source))
    return matching_keys


def remap_prefixed_keys(
    source: Mapping[str, T],
    prefix: str,
    unprefixed_keys: Iterable[str]
) -> Dict[str, T]:
    """
    Transfer the prefixed k/v pairs to a new dict under unprefixed names

    Initially added to ease separating src-* and out-* arg versions as a
    replacement for ambiguous and difficult-to-implement positionally
    interpreted repeated arguments for the input and output.

    :param source: A mapping with string keys
    :param prefix: The string prefix to use
    :param unprefixed_keys: The keys without their prefix
    :return:
    """
    remapping_table = {f"{prefix}{s}": s for s in unprefixed_keys}
    remapped = remap(source, remapping_table)
    return remapped


@overload
def popvalue(source: MutableMapping[KeyT, ValueT], key: KeyT, default: KeyT) -> ValueT:
    return popvalue(source, key, default)


@overload
def popvalue(source: MutableMapping[KeyT, ValueT], key: KeyT) -> ValueT:
    return popvalue(source, key)


def popvalue(
    source: MutableMapping[KeyT, ValueT],
    key: KeyT,
    *default: Optional[ValueT]
) -> ValueT:
    """
    Pop for key off of source, with default as a fallback if provided

    If no default is provided, a KeyError will be raised if key is not
    in source.

    :param source: A mapping to remove a value from
    :param key: The key to remove the value for
    :param default: Optional, returned if key not in source
    :return:
    """
    default_len = len(default)
    if default_len > 1:
        raise StarArgsLengthError(default_len, max_args=1, args_name='default')
    elif default_len and key not in source:
        return default[0]

    return source.pop(key)


def pop_items(
    source: MutableMapping[KeyT, ValueT],
    keys_or_defaults: Optional[KeyAndOrDefaultSource] = None
) -> Dict[KeyT, ValueT]:
    """
    Transfer key/value pairs to new mapping, using defaults if provided

    When keys_or_defaults is a simple iterable, all keys are mandatory.
    If it is a mapping, the values for each key will be used as a
    fallback default if the key is not found. See get_all for more
    information.

    :param source: The mapping to transfer values from.
    :param keys_or_defaults: An iterable of keys or key / default value
                             mapping.
    :return:
    """
    result = copy_from_mapping(source, keys_or_defaults, getter=popvalue)
    return result


def pop_values(
    source: MutableMapping[KeyT, ValueT],
    keys_or_defaults: KeyAndOrDefaultSource
) -> Tuple[ValueT, ...]:
    """
    Remove values for keys from source, using defaults if provided

    When keys_or_defaults is a simple iterable, all keys are mandatory.
    If it is a mapping, the values for each key will be used as a
    fallback default if the key is not found. See get_all for more
    information.

    :param source: The mapping to transfer values from.
    :param keys_or_defaults: An iterable of keys or key / default value
                             mapping.
    :return:
    """
    dict_raw = pop_items(source, keys_or_defaults)
    as_tuple = tuple(dict_raw.values())
    return as_tuple


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
