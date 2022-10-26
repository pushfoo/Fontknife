import pytest

from octofont3.custom_types import BboxFancy, BBOX_PROP_NAMES, CoordFancy
from octofont3.utils import BboxEnclosingAll

from . import (
    bbox_type,
    prefilled_bbox_values,
    prefilled_bbox_of_type,
    sequence_type
)


@pytest.fixture(params=(BboxFancy, BboxEnclosingAll))
def custom_bbox_type(request):
    return request.param


@pytest.fixture
def prefilled_custom_bbox_instance(custom_bbox_type, prefilled_bbox_values):
    return custom_bbox_type(prefilled_bbox_values)


def test_eq_works_with_self(prefilled_custom_bbox_instance):
    assert prefilled_custom_bbox_instance == prefilled_custom_bbox_instance


def test_eq_returns_true_on_matching_bbox(prefilled_custom_bbox_instance, prefilled_bbox_of_type):
    assert prefilled_custom_bbox_instance == prefilled_bbox_of_type


def test_eq_returns_false_on_nonmatching_bbox(prefilled_custom_bbox_instance, bbox_type):
    other = bbox_type((0, 0, 0, 0))
    assert prefilled_custom_bbox_instance != other


@pytest.mark.parametrize('wrong_length', (0, 3, 5))
def test_eq_with_wrong_length_raises_value_error(
    prefilled_custom_bbox_instance,
    wrong_length,
    sequence_type
):
    wrong_length_sequence = sequence_type((i for i in range(wrong_length)))

    with pytest.raises(ValueError):
        result = prefilled_custom_bbox_instance == wrong_length_sequence


def test_getitem_dunder(prefilled_custom_bbox_instance, prefilled_bbox_values):
    for i in range(4):
        assert prefilled_custom_bbox_instance[i] == prefilled_bbox_values[i]


def test_iter_dunder(prefilled_custom_bbox_instance, prefilled_bbox_values):
    for i, value in enumerate(prefilled_custom_bbox_instance):
        assert value == prefilled_bbox_values[i]


def test_name_properties(
    prefilled_custom_bbox_instance,
    prefilled_bbox_values,
):
    for expected_value, prop_name in zip(prefilled_bbox_values, BBOX_PROP_NAMES):
        assert getattr(prefilled_custom_bbox_instance, prop_name) == expected_value


@pytest.mark.parametrize(
    'inside_value',
    (
        (1, 2, 2, 2),
        (1, 2),
        [1, 2],
        [1, 2, 2, 2],
        BboxFancy(1, 2, 2, 2),
        CoordFancy(1, 2)
    )
)
def test_encloses_returns_true_for_values_inside_bbox(inside_value, prefilled_custom_bbox_instance):
    assert prefilled_custom_bbox_instance.encloses(inside_value)


@pytest.mark.parametrize(
    'outside_values',
    (
        (0, 0, 0, 0),
        (4, 5, 5, 7),
        (4, 5),
        [4, 5],
        BboxFancy(1, 2, 6, 7),
        CoordFancy(1, 10)
    )
)
def test_encloses_returns_false_for_values_outside_bbox(outside_values, prefilled_custom_bbox_instance):
    assert not prefilled_custom_bbox_instance.encloses(outside_values)


@pytest.mark.parametrize(
    'bad_values',
    (
        (1, ),
        (1, 2, 3),
        [1, ],
        [1, 2, 3],
    )
)
def test_encloses_raises_value_error_when_encloses_gets_bad_arg_length(bad_values, prefilled_custom_bbox_instance):
    with pytest.raises(ValueError):
        prefilled_custom_bbox_instance.encloses(bad_values)
