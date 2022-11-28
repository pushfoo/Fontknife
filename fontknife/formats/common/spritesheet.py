from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Union, Optional, Sequence, Generator

from fontknife.custom_types import BoundingBox, Size, BboxFancy, Coord, SizeFancy
from fontknife.utils import attrs_eq


# The most popular character selection & ordering for spritesheet fonts
# based on browsing through opengameart.org's font offerings.
DEFAULT_SHEET_GLYPHS = tuple([chr(i) for i in range(ord(' '), ord('~') + 1)])


class GridMapperArgException(ValueError):
    def __init__(self, missing_arg_names: Sequence[str]):
        message =\
            f"At most 1 argument may be None, but {len(missing_arg_names)}"\
            f" / 4 were None instead: {', '.join(missing_arg_names)}"

        super().__init__(message)
        self.missing_arg_names = missing_arg_names


GRID_MAPPER_DIM_NAMES = ('sheet_bounds_px', 'sheet_size_tiles', 'tile_size_px', 'tile_spacing_px')


class GridMapper(MappingABC):

    def __init__(
            self,
            sheet_bounds_px: Optional[Union[Size, BoundingBox]] = None,
            sheet_size_tiles: Optional[Size] = None,
            tile_size_px: Optional[Size] = None,
            tile_spacing_px: Size = SizeFancy(0, 0),
    ):
        """
        Maps tile indices to locations within a rectangular grid.

        Assumes left-to-right, top-to-bottom layout of tiles.

        This class-based approach should probably be refactored since
        __init__  is suspiciously complicated.

        sheet_bounds_px may be a bounding box to allow for cases such as:

            * Data starting at an offset
            * Multiple grids in a single image

        :param sheet_bounds_px: How big the region to iterate over is
        :param sheet_size_tiles: The columns x rows size of the sheet
        :param tile_size_px: Width x height of tiles in px
        :param tile_spacing_px: x, y spacing between each tile
        """

        # Enforce argument requirements to calculate grid data
        _d = {
            'sheet_bounds_px': sheet_bounds_px,
            'sheet_size_tiles': sheet_size_tiles,
            'tile_size_px': tile_size_px,
            'tile_spacing_px': tile_spacing_px
        }
        num_none = tuple(_d.values()).count(None)
        if num_none > 1:
            raise GridMapperArgException([k for k, v in _d.items() if v is None])

        # Calculate & set required parameters
        self._tile_spacing_px = SizeFancy(*tile_spacing_px)
        if sheet_bounds_px is None:
            self._bounds_px = BboxFancy((
                0, 0,
                sheet_size_tiles[0] * tile_size_px[0],
                sheet_size_tiles[1] * tile_size_px[1]
            ))
        else:
            self._bounds_px = BboxFancy(sheet_bounds_px)

        if sheet_size_tiles is None:
            self._sheet_size_tiles = SizeFancy(
                self._bounds_px.width // tile_size_px[0],
                self._bounds_px.height // tile_size_px[1]
            )

        else:
            self._sheet_size_tiles = SizeFancy(*sheet_size_tiles)

        self._number_of_tiles = self._sheet_size_tiles.width * self._sheet_size_tiles.height

        if tile_size_px is None:
            self._tile_size_px = SizeFancy(
                self._bounds_px.width // sheet_size_tiles[0],
                self._bounds_px.height // sheet_size_tiles[1]
            )
        else:
            self._tile_size_px = SizeFancy(*tile_size_px)

        self._tile_step_px = SizeFancy(
            self._tile_size_px.width + self._tile_spacing_px.width,
            self._tile_size_px.height + self._tile_spacing_px.height
        )

    def __len__(self) -> int:
        return self._number_of_tiles

    def __contains__(self, item: int) -> bool:
        return 0 <= item < len(self)

    def __eq__(self, other: GridMapper):
        return attrs_eq(
            self, other,
            (
                'sheet_bounds_px',
                'sheet_size_tiles',
                'tile_size_px',
                'offset',
                'tile_spacing_px'
            )
        )

    @property
    def tile_spacing_px(self) -> Size:
        return self._tile_spacing_px

    @property
    def sheet_bounds_px(self) -> BboxFancy:
        return self._bounds_px

    @property
    def sheet_size_tiles(self) -> Size:
        return self._sheet_size_tiles

    @property
    def tile_size_px(self) -> Size:
        return self._tile_size_px

    @property
    def offset(self) -> Coord:
        return self._bounds_px[0], self._bounds_px[1]

    def _check_for_raw_index_bound_error(self, index: int) -> Optional[KeyError]:
        if index < 0 or index >= self._number_of_tiles:
            return KeyError(f'Index {index} not in grid')
        return None

    def bbox_for_tile_coord(self, coord: Coord) -> BoundingBox:
        """
        Calculate the bounding box for a given tile col, row coord

        :param coord: The col, row position to get a bbox for
        """
        offset = self.offset

        left = offset[0] + coord[0] * self._tile_step_px.width
        top = offset[1] + coord[1] * self._tile_step_px.height

        return BboxFancy(
            left, top,
            left + self._tile_size_px.width,
            top + self._tile_size_px.height
        )

    def coord_for_sheet_index(self, index: int) -> Coord:
        """

        Get col, row corresponding to a linear index in the grid.

        :param index: The linear index of a glyph
        :return:
        """
        if type(index) != int:
            raise TypeError('Only ints are supported for this operation')

        e = self._check_for_raw_index_bound_error(index)
        if e:
            raise e

        column = index % self._sheet_size_tiles[0]
        row = index // self._sheet_size_tiles[0]
        return column, row

    def bbox_for_sheet_index(self, index: int) -> BoundingBox:
        """A bounding box for a specific linear index"""
        coord = self.coord_for_sheet_index(index)
        bbox = self.bbox_for_tile_coord(coord)
        return bbox

    def __iter__(self) -> Generator[int, None, None]:
        for i in range(len(self)):
            yield i

    def __getitem__(self, item: int) -> BoundingBox:
        if isinstance(item, int):
            e = self._check_for_raw_index_bound_error(item)
            if e:
                raise e
            return self.bbox_for_sheet_index(item)

        raise TypeError(f'Getting item using type {item!r} is not supported')

