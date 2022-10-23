import pytest

from octofont3.custom_types import BboxClassABC, BboxFancy


from . import (
    bbox_type,
    prefilled_bbox_values,
    prefilled_bbox_of_type,
    sequence_type
)


@pytest.fixture(params=BboxClassABC.__subclasses__())
def prefilled_abc_subclass_instance(request, prefilled_bbox_values) -> BboxClassABC:
    type_ = request.param
    if type_ is BboxFancy:
        bbox = type_(*prefilled_bbox_values)
    else:
        bbox = type_(prefilled_bbox_values)

    return bbox


def test_eq_works_with_self(prefilled_abc_subclass_instance):
    assert prefilled_abc_subclass_instance == prefilled_abc_subclass_instance


def test_eq_returns_true_on_matching_bbox(prefilled_abc_subclass_instance, prefilled_bbox_of_type):
    assert prefilled_abc_subclass_instance == prefilled_bbox_of_type


def test_eq_returns_false_on_nonmatching_bbox(prefilled_abc_subclass_instance, bbox_type):
    other = bbox_type((0, 0, 0, 0))
    assert prefilled_abc_subclass_instance != other


@pytest.mark.parametrize('wrong_length', (0, 3, 5))
def test_eq_with_wrong_length_raises_value_error(
    prefilled_abc_subclass_instance,
    wrong_length,
    sequence_type
):
    with pytest.raises(ValueError):
        wrong_length_sequence = sequence_type((i for i in range(wrong_length)))
        result = prefilled_abc_subclass_instance == wrong_length_sequence


def test_getitem_dunder(prefilled_abc_subclass_instance, prefilled_bbox_values):
    for i in range(4):
        assert prefilled_abc_subclass_instance[i] == prefilled_bbox_values[i]


def test_iter_dunder(prefilled_abc_subclass_instance, prefilled_bbox_values):
    for i, value in enumerate(prefilled_abc_subclass_instance):
        assert value == prefilled_bbox_values[i]


def test_name_properties(
    prefilled_abc_subclass_instance,
    prefilled_bbox_values,
):
    for expected_value, prop_name in zip(prefilled_bbox_values, ('left', 'top', 'right', 'bottom')):
        assert getattr(prefilled_abc_subclass_instance, prop_name) == expected_value
