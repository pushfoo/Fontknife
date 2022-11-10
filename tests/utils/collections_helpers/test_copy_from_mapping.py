from dataclasses import asdict

import pytest

from octofont3.utils import copy_from_mapping


@pytest.fixture
def empty_dict():
    return {}


@pytest.fixture
def reference_dict(attr_dummy_reference_instance):
    return asdict(attr_dummy_reference_instance)


@pytest.fixture
def reference_dict_missing_single_field(reference_dict, attr_dummy_single_field):
    d = dict(reference_dict)
    del d[attr_dummy_single_field]
    return d


def test_copy_from_mapping_uses_non_mapping_iterables_of_keys_correctly(
   reference_dict,
   attr_dummy_field_names_as_non_mapping_iterable
):
    copied = copy_from_mapping(reference_dict, attr_dummy_field_names_as_non_mapping_iterable)
    assert copied == reference_dict


def test_copy_from_mapping_copies_all_keys_when_no_keys_specified(reference_dict):
    copied = copy_from_mapping(reference_dict)
    assert copied == reference_dict


def test_copy_from_mapping_returns_empty_dict_when_passed_empty_non_mapping_iterable(
    reference_dict,
    empty_non_mapping_iterable,
    empty_dict
):
    copied = copy_from_mapping(reference_dict, empty_non_mapping_iterable)
    assert copied == empty_dict


def test_copy_from_mapping_uses_defaults_when_needed_and_specified(
    attr_dummy_single_field,
    reference_dict_missing_single_field,
    mapping_of_field_names_to_nones
):
    copied = copy_from_mapping(reference_dict_missing_single_field, mapping_of_field_names_to_nones)
    assert copied[attr_dummy_single_field] is None
    for k, v in reference_dict_missing_single_field.items():
        assert copied[k] == v


def test_copy_from_mapping_ignores_defaults_when_not_needed_but_specified(
    reference_dict,
    attr_dummy_single_field,
    mapping_of_field_names_to_nones
):
    copied = copy_from_mapping(reference_dict, mapping_of_field_names_to_nones)
    assert copied == reference_dict
