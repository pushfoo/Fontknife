from __future__ import annotations
from itertools import combinations_with_replacement

import pytest

from fontknife.custom_types import BboxFancy, BBOX_EDGE_NAMES, sort_ltrb
from fontknife.utils import tuplemap


BBOX_LIKE_TYPES = (
    tuple,
    list,
    lambda arg: BboxFancy(*arg),
)


def alt_sorting_logic(raw: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Alternate version of x & sorting logic for tests.

    Bboxes are directionless, so it makes sense to normalize the order
    on creation for convenience.
    """
    # We don't need C-style efficiency / swapping since this test code,
    # so we unpack and use if statements instead of using temp vars.
    _left, _top, _right, _bottom = raw

    if _left > _right:
        left, right = _right, _left
    else:
        left, right = _left, _right

    if _top > _bottom:
        top, bottom = _bottom, _top
    else:
        top, bottom = _top, _bottom

    return left, top, right, bottom


@pytest.fixture(scope='session', params=BBOX_LIKE_TYPES)
def bbox_arg_source_type(request):
    return request.param


@pytest.fixture(
    scope='session', params=filter(
        # keep only combos where at least 1 element is negative
        lambda combo: any(map(lambda elt: elt < 0, combo)),
        combinations_with_replacement((1, -1), 4)
    )
)
def bad_args_containing_negatives(request):
    return tuplemap(
        lambda a: a[0] * a[1],
        zip(request.param, (1, 2, 3, 4))
    )


@pytest.fixture(
    scope='session',
    params=(0, 1, 2, 3, 5, 6, 7)
)
def bad_args_of_wrong_length(request):
    return tuple(range(request.param))


def test_creation_rejects_negative_values(bad_args_containing_negatives):
    with pytest.raises(ValueError):
        BboxFancy(*bad_args_containing_negatives)


def test_creation_rejects_wrong_length_args(bad_args_of_wrong_length):
    with pytest.raises(TypeError):
        BboxFancy(*bad_args_of_wrong_length)


@pytest.fixture(scope='session', params=[
    ((0, 0, 1, 1), (0, 0, 0, 0)),
    ((0, 0, 1, 1), (1, 1, 1, 1)),
    ((3, 4, 5, 6), (4, 4, 5, 6))
])
def pair_valid_bbox_and_base_value_inside(request):
    return request.param


@pytest.fixture(scope='session', params=BBOX_LIKE_TYPES)
def value_inside_bbox(request, pair_valid_bbox_and_base_value_inside):
    return request.param(pair_valid_bbox_and_base_value_inside[1])


@pytest.fixture(scope='session', params=[
    (10, 11, 12, 13),
    (100, 0, 0, 0)
])
def value_outside_bbox(request, bbox_arg_source_type):
    return bbox_arg_source_type(request.param)


@pytest.fixture(scope='session', params=BBOX_LIKE_TYPES)
def base_valid_args(request, pair_valid_bbox_and_base_value_inside):
    return request.param(pair_valid_bbox_and_base_value_inside[0])


@pytest.fixture(scope='session')
def valid_args(base_valid_args, bbox_arg_source_type):
    return bbox_arg_source_type(base_valid_args)


@pytest.fixture(scope='session')
def bbox_fancy_for_valid_args(valid_args):
    return BboxFancy(*valid_args)


@pytest.fixture(scope='session')
def tuple_equivalent_to_bbox_for_valid_args(valid_args):
    return alt_sorting_logic(valid_args)


@pytest.mark.parametrize("raw", (
        (1, 1, 0, 0),
        (0, 1, 1, 0),
        (1, 0, 0, 1),
        (0, 0, 1, 1)
))
def test_sorting_logic(raw: tuple[int, int, int, int]):
    assert sort_ltrb(*raw) == alt_sorting_logic(raw)


def test_bbox_fancy_compares_as_tuple(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert bbox_fancy_for_valid_args == alt_sorting_logic(tuple_equivalent_to_bbox_for_valid_args)


# A pair of an index + property name
@pytest.fixture(scope='session', params=enumerate(BBOX_EDGE_NAMES))
def index_edge_name_pair(request):
    """A pair of (index, property_name)"""
    return request.param


@pytest.fixture(scope='session')
def bound_index(index_edge_name_pair):
    return index_edge_name_pair[0]


@pytest.fixture(scope='session')
def bound_name(index_edge_name_pair):
    return index_edge_name_pair[1]


def test_bbox_fancy_sets_edge_props_correctly(
    bbox_fancy_for_valid_args,
    bound_name,
    tuple_equivalent_to_bbox_for_valid_args,
    bound_index
):
    fancy_value = getattr(bbox_fancy_for_valid_args, bound_name)
    equi_value  = tuple_equivalent_to_bbox_for_valid_args[bound_index]
    assert fancy_value == equi_value


def test_bbox_fancy_sets_size_correctly(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    other_left, other_top, other_right, other_bottom = tuple_equivalent_to_bbox_for_valid_args
    assert bbox_fancy_for_valid_args.size == (
        other_right - other_left,
        other_bottom - other_top
    )


def test_bbox_fancy_sets_width_correctly(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    other_left, _, other_right, _ = tuple_equivalent_to_bbox_for_valid_args
    assert bbox_fancy_for_valid_args.width == other_right - other_left


def test_bbox_fancy_sets_height_correctly(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert bbox_fancy_for_valid_args.height ==\
        tuple_equivalent_to_bbox_for_valid_args[3] - tuple_equivalent_to_bbox_for_valid_args[1]


def test_bbox_fancy_hash_collides_with_hash_of_equivalent_tuple(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert hash(bbox_fancy_for_valid_args) == hash(tuple_equivalent_to_bbox_for_valid_args)


def test_bbox_fancy_encloses_raises_value_error_on_negatives(bbox_fancy_for_valid_args, bad_args_containing_negatives):
    with pytest.raises(ValueError):
        bbox_fancy_for_valid_args.encloses(bad_args_containing_negatives)


def test_bbox_fancy_encloses_raises_value_error_on_wrong_length_args(bbox_fancy_for_valid_args, bad_args_of_wrong_length):
    with pytest.raises(ValueError):
        bbox_fancy_for_valid_args.encloses(bad_args_of_wrong_length)


def test_bbox_encloses_returns_true_for_values_inside(
    bbox_fancy_for_valid_args, value_inside_bbox
):
    enclosed = bbox_fancy_for_valid_args.encloses(value_inside_bbox)
    assert enclosed


def test_bbox_encloses_returns_false_for_values_outside(bbox_fancy_for_valid_args, value_outside_bbox):
    enclosed = bbox_fancy_for_valid_args.encloses(value_outside_bbox)
    assert enclosed is False


def test_bbox_or_stretches_bboxes_correctly():
    # Base all-zero bbox
    current  = BboxFancy(0, 0,  0,  0)  # flake8: noqa
    # Union with a tuple
    current |=          (0, 5,  2,  3)  # flake8: noqa
    # Union with a list
    current |=          [4, 0, 10,  7]  # flake8: noqa
    # Union with another BboxFancy
    current |= BboxFancy(8, 9,  6, 11)  # flake8: noqa

    # expected =         0, 0, 10, 11

    # Unrolled for max visibility
    assert current[0] == 0
    assert current[1] == 0
    assert current[2] == 10
    assert current[3] == 11
