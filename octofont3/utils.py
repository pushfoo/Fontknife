import sys
from dataclasses import asdict
from math import inf
from typing import Iterable, Tuple, Dict, Optional, Any, Callable, Union, Sized

from PIL import Image, ImageDraw

from octofont3.custom_types import BoundingBox, Size, ImageFontLike, SizeFancy, BboxFancy, Pair


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


def guess_glyphs_to_check(font: Any) -> Iterable[str]:
    glyphs_to_check = []

    if not hasattr(font, 'glyph'):
        raise ValueError("The passed font requires glyphs to be specified manually.")
    else:
        glyphs = font.glyph
        if isinstance(glyphs, Dict):
            glyphs_to_check.extend((chr(i) for i in glyphs.keys()))
        else:
            glyphs_to_check.extend((chr(i) for i in range(len(glyphs))))

    return glyphs_to_check


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


def find_max_dimensions(
    font: ImageFontLike,
    glyphs_to_check: Iterable[str],
    bbox_getter: Callable[[ImageFontLike, Iterable[str]], BoundingBox] = lambda font, glyph: font.getbbox(glyph)
) -> SizeFancy:
    """
    Get the size of the tile that will fit every glyph requested

    :param font: The font to evaluate
    :param glyphs: which glyphs to use
    :param bbox_getter: A function to process the font and requested glyphs with
    :return: the max glyph width and max glyph height for the font
    """
    max_width, max_height = 0, 0
    for glyph in glyphs_to_check:
        bbox = bbox_getter(font, glyph)

        if bbox is not None:
            width, height = get_bbox_size(bbox)
            max_height = max(width, max_height)
            max_width = max(height, max_width)

    return SizeFancy(max_width, max_height)
