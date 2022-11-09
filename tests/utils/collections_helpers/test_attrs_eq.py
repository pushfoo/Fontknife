import pytest
from octofont3.utils import attrs_eq

from . import (
    AttrDummy,
    MutatesPropertyOnAccess,
    HasAProp,
    HasBProp,
    mutates_prop_on_access_instance,
    attr_dummy_single_field,
    attr_dummy_field_names,
    attr_dummy_reference_instance,
    value_for_default_arg
)


@pytest.fixture
def equals_reference_instance():
    return AttrDummy()


def test_reference_instance_not_same_instance_as_equals_reference_instance(
    attr_dummy_reference_instance,
    equals_reference_instance
):
    """Make sure we never accidentally cheat by checking instance IDs"""
    assert attr_dummy_reference_instance is not equals_reference_instance


@pytest.fixture
def attr_dummy_single_field_different(attr_dummy_single_field):
    return AttrDummy(**{attr_dummy_single_field: 99})


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


def test_attrs_eq_uses_dict_as_source_of_default_values():
    # Use dictionary as padding default for both of these items.
    a = HasAProp()
    b = HasBProp()
    default = {'a': 0, 'b': 1}
    assert attrs_eq(a, b, default)


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
