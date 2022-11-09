import pytest

from octofont3.utils import get_attrs

from . import (
    AttrDummy,
    attr_dummy_field_names,
    attr_dummy_reference_instance
)


@pytest.fixture
def return_value(attr_dummy_field_names):
    return {field_name:i for i, field_name in enumerate(attr_dummy_field_names)}


def test_get_attrs_returns_correct_values_when_sequence_attrs_arg_and_all_values_present(
        attr_dummy_reference_instance,
        attr_dummy_field_names,
    return_value,
):
    assert get_attrs(attr_dummy_reference_instance, attr_dummy_field_names) == return_value


def test_get_attrs_raises_attribute_error_when_sequence_attrs_arg_and_values_missing(
        attr_dummy_reference_instance
):
    with pytest.raises(AttributeError):
        get_attrs(attr_dummy_reference_instance, ('missing_name',))


def test_dict_attrs_returns_correct_values_when_all_attrs_present_and_defaults_provided(
        attr_dummy_reference_instance, attr_dummy_field_names, return_value
):
    assert get_attrs(attr_dummy_reference_instance, {name: None for name in attr_dummy_field_names}) == return_value


def test_dict_attrs_args_uses_default_when_attrs_missing(
        attr_dummy_reference_instance
):
    template = {'missing_name': 99}
    assert get_attrs(attr_dummy_reference_instance, template) == template
