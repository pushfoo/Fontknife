from typing import Iterable, Tuple, Union

import pytest

from octofont3.custom_types import BboxFancy, SizeFancy
from . import prefilled_bbox_values


def test_hash(prefilled_bbox_values):
    assert hash(BboxFancy(*prefilled_bbox_values)) == hash(prefilled_bbox_values)


@pytest.fixture(params=(
    (0, 0, 7, 8),  # plain int arguments
    (7, 8),  # a size tuple
    [7, 8],  # a size list
    ((0, 0, 7, 8),),
    ((7, 8),),
    ([7, 8],),
    (SizeFancy(7, 8))
))
def good_source_args(request):
    return request.param


def test_bbox_fancy_init_works_with_valid_objects(good_source_args):
    bbox = BboxFancy(*good_source_args)
    assert bbox == (0, 0, 7, 8)


@pytest.mark.parametrize(
    ['args', 'expected_width', 'expected_height'], (
    ((2, 2), 2, 2),
    (((2, 2),), 2, 2),
    ((SizeFancy(3, 3),), 3, 3),
    ((1, 1, 3, 6), 2, 5),
    (((1, 1, 3, 6),), 2, 5)
))
def test_bbox_fancy_init_sets_size_attributes_correctly(args, expected_width, expected_height):
    bbox = BboxFancy(*args)
    assert bbox.width == expected_width
    assert bbox.height == expected_height
    assert bbox.size == (expected_width, expected_height)


@pytest.mark.parametrize(
    'bad_source_args',
    (
        tuple(),  # 0 length raw args
        tuple([tuple()]),  # 0 length wrapped tuple
        tuple([[]]),  # 0 length wrapped list
        ((1, 2, 3),),  # 3-length wrapped tuple,
        (1, 2, 3),  # 3 length raw args
        ((1, 2, 3, 4, 5),),
        (1, 2, 3, 4, 5)
    )
)
def test_bbox_fancy_init_raises_value_error_when_wrong_length(bad_source_args):
    with pytest.raises(ValueError):
        bbox = BboxFancy(*bad_source_args)
