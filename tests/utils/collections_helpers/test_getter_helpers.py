import pytest

from fontknife.custom_types import StarArgsLengthError
from fontknife.utils import getvalue, popvalue, detect_getter_for_source


@pytest.fixture
def too_many_default_values(non_mapping_iterable_type):
    return non_mapping_iterable_type(range(2))


@pytest.fixture
def not_a_field_name() -> str:
    return 'z'


def test_mapping_getter_gets_correct_value_for_attr(
    mapping_getter,
    attr_dummy_defaults_dict,
    attr_dummy_single_field,
    attr_dummy_value_for_single_field
):
   gotten = mapping_getter(attr_dummy_defaults_dict, attr_dummy_single_field)
   assert gotten == attr_dummy_value_for_single_field


def test_mapping_getter_uses_default_if_provided(
    mapping_getter,
    attr_dummy_defaults_dict,
    not_a_field_name,
):
    gotten = mapping_getter(attr_dummy_defaults_dict, not_a_field_name, 'default_value')
    assert gotten == 'default_value'


def test_mapping_getter_raises_attribute_error_when_value_missing_and_no_default_passed(
    mapping_getter,
    attr_dummy_defaults_dict,
    not_a_field_name
):
    with pytest.raises(KeyError):
        mapping_getter(attr_dummy_defaults_dict, not_a_field_name)


def test_mapping_getter_raises_exception_when_too_many_defaults(
    mapping_getter,
    attr_dummy_defaults_dict,
    too_many_default_values
):
    with pytest.raises(StarArgsLengthError):
        mapping_getter(
            attr_dummy_defaults_dict,
            'a',
            *too_many_default_values)


def test_popvalue_removes_keys_from_mapping_correctly(
    attr_dummy_defaults_dict,
    attr_dummy_single_field,
    attr_dummy_field_names_minus_single_field
):
    popvalue(attr_dummy_defaults_dict, attr_dummy_single_field)
    assert tuple(attr_dummy_defaults_dict.keys()) == attr_dummy_field_names_minus_single_field


def test_detect_getter_for_source_returns_get_value_for_mapping():
    getter = detect_getter_for_source({})
    assert getter is getvalue


def test_detect_getter_for_source_returns_get_attr_for_nonmapping_object(attr_dummy_reference_instance):
    getter = detect_getter_for_source(attr_dummy_reference_instance)
    assert getter is getattr