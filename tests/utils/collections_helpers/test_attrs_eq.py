from dataclasses import dataclass, field

import pytest
from octofont3.utils import attrs_eq


@dataclass
class HasAProp:
    a: int = field(default=0)


@dataclass
class HasBProp:
    b: int = field(default=1)


@pytest.fixture
def equals_reference_instance(attr_dummy_type):
    return attr_dummy_type()


def test_attrs_eq_returns_true_for_equal_but_different_objects_of_same_type(
    attr_dummy_reference_instance,
    equals_reference_instance
):
    """Make sure we never accidentally cheat by checking instance IDs"""
    assert attr_dummy_reference_instance is not equals_reference_instance


@pytest.fixture
def attr_dummy_single_field_different(attr_dummy_type, attr_dummy_single_field):
    return attr_dummy_type(**{attr_dummy_single_field: 99})


def test_attrs_eq_returns_true_when_comparing_single_equal_value(
    attr_dummy_reference_instance,
    equals_reference_instance,
    attr_dummy_single_field
):
    assert attrs_eq(
        attr_dummy_reference_instance,
        equals_reference_instance,
        (attr_dummy_single_field,)
    ) is True


def test_attrs_eq_returns_true_when_comparing_mutliple_equal_fields(
    attr_dummy_reference_instance,
    equals_reference_instance,
    attr_dummy_field_names
):
    assert attrs_eq(
        attr_dummy_reference_instance,
        equals_reference_instance,
        attr_dummy_field_names
    ) is True


def test_attrs_eq_returns_false_when_comparing_single_differing_attr(
    attr_dummy_reference_instance,
    attr_dummy_single_field_different,
    attr_dummy_single_field,
):
    assert attrs_eq(
        attr_dummy_reference_instance,
        attr_dummy_single_field_different,
        (attr_dummy_single_field,)
    ) is False


def test_attrs_eq_returns_false_when_comparing_multiple_fields_and_some_equal(
    attr_dummy_reference_instance,
    attr_dummy_single_field_different,
    attr_dummy_field_names
):
    assert not attrs_eq(
        attr_dummy_reference_instance,
        attr_dummy_single_field_different,
        attr_dummy_field_names
    )


def test_attrs_eq_uses_dict_as_source_of_default_values(attr_dummy_defaults_dict):
    a = HasAProp()
    b = HasBProp()
    assert attrs_eq(a, b, attr_dummy_defaults_dict)


def test_attrs_eq_returns_false_when_same_object_as_a_and_b_with_mutating_property(
    mutates_prop_on_access_instance
):
    # Covers a case where:
    #  1. a is b
    #  2. Accessing the property changes the return value

    assert not attrs_eq(
        mutates_prop_on_access_instance,
        mutates_prop_on_access_instance,
        ['times_accessed_prop']
    )
