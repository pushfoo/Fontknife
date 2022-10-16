from dataclasses import dataclass
from itertools import filterfalse
from typing import Dict, Tuple, overload, Iterable

from PIL import Image

from octofont3.custom_types import ImageCoreLike


@dataclass
class SpritesheetMetadata:

    sheet_size_px: Tuple[int, int] = None
    sheet_size_tiles: Tuple[int, int] = None
    tile_size_px: Tuple[int, int] = None

    def __post_init__(self):
        """
        Calculate any missing dimensions
        :return:
        """
        num = len(list(filterfalse([self.sheet_size_px, self.sheet_size_tiles, self.tile_size_px])))
        if num < 2:
            raise ValueError("Must provide at least 2/3 arguments to SpritesheetBoundsData")


def calculate_bounds(

) -> Tuple[Tuple[int,int], Tuple[int, int]]:
    """
    Calculate the bounds for
    :param sheet_size_px:
    :param sheet_size_tiles:
    :param tile_size_px:
    :return:
    """
    pass

def load_spritesheet_glyphs(
    sheet_size_tiles: Tuple[int, int],
    tile_size_px: Tuple[int, int],
    glyph_sequence: Iterable[str]
) -> Dict[str, ImageCoreLike]:
    pass


