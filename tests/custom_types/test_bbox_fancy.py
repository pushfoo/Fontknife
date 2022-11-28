from itertools import combinations_with_replacement

import pytest

from fontknife.custom_types import BboxFancy, BBOX_EDGE_NAMES
from fontknife.utils import tuplemap


# Named functions of lambdas to increase readability in the pytest
# results. Lambdas print as lambda\d+ , which is hard to read.
def bare_args(a):
    return a


def wrapped_args(a):
    return a,


@pytest.fixture(scope='session', params=[bare_args, wrapped_args])
def bare_or_wrapped(request):
    return request.param


BBOX_TYPE_FACTORIES = (
    tuple,
    list,
    BboxFancy,
)


@pytest.fixture(scope='session', params=BBOX_TYPE_FACTORIES)
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
    params=(0, ) + tuple(range(1, 7, 2)))
def bad_args_of_wrong_length(request):
    return tuple(range(request.param))


def test_creation_rejects_negative_values(bad_args_containing_negatives, bare_or_wrapped):
    with pytest.raises(ValueError):
        BboxFancy(*bare_or_wrapped(bad_args_containing_negatives))


def test_creation_rejects_wrong_length_args(bad_args_of_wrong_length, bare_or_wrapped, ):
    with pytest.raises(ValueError):
        BboxFancy(*bare_or_wrapped(bad_args_of_wrong_length))


@pytest.fixture(scope='session', params=[
    ((5, 6), (4, 4)),
    ((3, 4, 5, 6), (4, 4, 5, 6))
])
def pair_valid_bbox_and_base_value_inside(request):
    return request.param


@pytest.fixture(scope='session', params=BBOX_TYPE_FACTORIES)
def value_inside_bbox(request, pair_valid_bbox_and_base_value_inside):
    return request.param(pair_valid_bbox_and_base_value_inside[1])


@pytest.fixture(scope='session', params=[
    (10, 10),
    (10, 11, 12, 13)
])
def value_outside_bbox(request, bbox_arg_source_type):
    return bbox_arg_source_type(request.param)


@pytest.fixture(scope='session', params=BBOX_TYPE_FACTORIES)
def base_valid_args(request, pair_valid_bbox_and_base_value_inside):
    return request.param(pair_valid_bbox_and_base_value_inside[0])


@pytest.fixture(scope='session')
def valid_args(bare_or_wrapped, base_valid_args, bbox_arg_source_type):
    return bare_or_wrapped(bbox_arg_source_type(base_valid_args))


@pytest.fixture(scope='session')
def bbox_fancy_for_valid_args(valid_args):
    return BboxFancy(*valid_args)


@pytest.fixture(scope='session')
def tuple_equivalent_to_bbox_for_valid_args(valid_args):
    actual_vals = tuple(valid_args if len(valid_args) > 1 else valid_args[0])
    return actual_vals if len(actual_vals) == 4 else (0, 0) + actual_vals


def test_bbox_fancy_compares_as_tuple(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert bbox_fancy_for_valid_args == tuple_equivalent_to_bbox_for_valid_args


@pytest.fixture(scope='session', params=enumerate(BBOX_EDGE_NAMES))
def index_edge_name_pair(request):
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
    assert getattr(bbox_fancy_for_valid_args, bound_name) == tuple_equivalent_to_bbox_for_valid_args[bound_index]


def test_bbox_fancy_sets_size_correctly(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert bbox_fancy_for_valid_args.size == (
        tuple_equivalent_to_bbox_for_valid_args[2] - tuple_equivalent_to_bbox_for_valid_args[0],
        tuple_equivalent_to_bbox_for_valid_args[3] - tuple_equivalent_to_bbox_for_valid_args[1]
    )


def test_bbox_fancy_sets_width_correctly(
    bbox_fancy_for_valid_args,
    tuple_equivalent_to_bbox_for_valid_args
):
    assert bbox_fancy_for_valid_args.width ==\
        tuple_equivalent_to_bbox_for_valid_args[2] - tuple_equivalent_to_bbox_for_valid_args[0]


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
    assert not enclosed


@pytest.fixture(
    scope='session',
    params=combinations_with_replacement(BBOX_TYPE_FACTORIES, 3)
)
def bboxes_of_mixed_types(request):
    return tuple(func(box) for func, box in zip(request.param, (
        (0, 5, 2, 3),
        (4, 0, 10, 7),
        (8, 9, 6, 11)
    )))


@pytest.fixture(scope='session')
def expected_bbox_or_result():
    return 0, 0, 10, 11


def test_bbox_or_stretches_bboxes_correctly(bboxes_of_mixed_types, expected_bbox_or_result):
    current = BboxFancy(0, 0)
    for bbox in bboxes_of_mixed_types:
        current |= bbox
    assert current == expected_bbox_or_result

