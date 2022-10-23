from itertools import combinations

import pytest

from octofont3.utils import BboxEnclosingAll, PropUninitializedError, BBOX_PROP_NAMES
from tests.utils.bboxes import BBOX_TYPE_FACTORIES


from . import (
    bbox_type,
    prefilled_bbox_values,
    prefilled_bbox_of_type
)


# Some bbox values and the expected result for enclosing all of them
BBOXES_SIMPLE = (
    (0, 5, 2, 3),
    (4, 1, 10, 7),
    (8, 9, 6, 11)
)
EXPECTED_ENCLOSING_ALL = (0, 1, 10, 11)


@pytest.fixture
def bboxes_of_type(bbox_type):
    return tuple(map(bbox_type, BBOXES_SIMPLE))


@pytest.fixture
def bbox_enclosing_all() -> BboxEnclosingAll:
    return BboxEnclosingAll()


@pytest.fixture(params=BBOX_PROP_NAMES)
def bbox_basic_prop_name(request):
    return request.param


@pytest.fixture
def prefilled_bbox_enclosing_all(prefilled_bbox_values) -> BboxEnclosingAll:
    return BboxEnclosingAll(prefilled_bbox_values)


@pytest.fixture(params=combinations(BBOX_TYPE_FACTORIES, len(BBOXES_SIMPLE)))
def bboxes_of_mixed_types(request):
    return tuple(func(box) for func, box in zip(request.param, BBOXES_SIMPLE))


def test_exception_on_accessing_uninitialized_after_init(resettable_bbox, bbox_basic_prop_name):
    bbox = BboxEnclosingAll()
    with pytest.raises(PropUninitializedError):
        getattr(bbox, bbox_basic_prop_name)


def test_init_from_bboxes_of_single_type(bboxes_of_type):
    bbox_enclosing_all = BboxEnclosingAll(*bboxes_of_type)
    assert bbox_enclosing_all == EXPECTED_ENCLOSING_ALL


def test_init_from_bboxes_of_mixed_types(bboxes_of_mixed_types):
    bbox_enclosing_all = BboxEnclosingAll(*bboxes_of_mixed_types)
    assert bbox_enclosing_all == EXPECTED_ENCLOSING_ALL


def test_update_from_bboxes_of_single_type(bbox_enclosing_all, bboxes_of_type):
    bbox_enclosing_all.update(*bboxes_of_type)
    assert bbox_enclosing_all == EXPECTED_ENCLOSING_ALL


def test_update_from_bboxes_of_mixed_types(bbox_enclosing_all, bboxes_of_mixed_types):
    bbox_enclosing_all.update(*bboxes_of_mixed_types)
    assert bbox_enclosing_all == EXPECTED_ENCLOSING_ALL


@pytest.fixture
def resettable_bbox():
    return BboxEnclosingAll((100, 100, 100, 100))


def test_exception_on_accessing_uninitialized_after_reset(
        resettable_bbox, bbox_basic_prop_name):
    resettable_bbox.reset()
    with pytest.raises(PropUninitializedError):
        getattr(resettable_bbox, bbox_basic_prop_name)


def test_reset_from_bboxes_of_single_type(resettable_bbox, bboxes_of_type):
    resettable_bbox.reset(*bboxes_of_type)
    assert resettable_bbox == EXPECTED_ENCLOSING_ALL


def test_reset_from_bboxes_of_mixed_types(resettable_bbox, bboxes_of_mixed_types):
    resettable_bbox.reset(*bboxes_of_mixed_types)
    assert resettable_bbox == EXPECTED_ENCLOSING_ALL

