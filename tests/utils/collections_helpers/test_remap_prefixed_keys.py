from typing import Dict

import pytest

from octofont3.utils import remap_prefixed_keys


@pytest.fixture
def key_prefix() -> str:
    return "prefix_"


@pytest.fixture
def prefixed_defaults_dict(key_prefix, attr_dummy_defaults_dict) -> Dict[str, int]:
    return {f"{key_prefix}{k}": v for k, v in attr_dummy_defaults_dict.items()}


@pytest.fixture
def single_attr_name_key_source_dict(attr_dummy_single_field, attr_dummy_defaults_dict):
    return {attr_dummy_single_field: None}


@pytest.fixture
def single_attr_name_expected_dict(attr_dummy_single_field, attr_dummy_defaults_dict):
    return {attr_dummy_single_field: attr_dummy_defaults_dict[attr_dummy_single_field]}


@pytest.fixture
def single_attr_name_simple_iterable(attr_dummy_single_field, non_mapping_iterable_type):
    return non_mapping_iterable_type((attr_dummy_single_field,))


def test_remap_prefixed_keys_returns_empty_dict_when_unprefixed_keys_is_empty_simple_iterable(
    prefixed_defaults_dict,
    key_prefix,
    empty_non_mapping_iterable
):
    remapped = remap_prefixed_keys(prefixed_defaults_dict, key_prefix, empty_non_mapping_iterable)
    assert isinstance(remapped, Dict)
    assert not remapped


def test_remap_prefixed_keys_returns_empty_dict_when_unprefixed_keys_is_empty_dict_iterable(
    prefixed_defaults_dict,
    key_prefix,
    empty_mapping_iterable
):
    remapped = remap_prefixed_keys(prefixed_defaults_dict, key_prefix, empty_mapping_iterable)
    assert isinstance(remapped, Dict)
    assert not remapped


def test_remap_prefixed_keys_returns_correct_remap_when_unprefixed_keys_is_simple_string_iterable(
    prefixed_defaults_dict,
    single_attr_name_simple_iterable,
    key_prefix,
    single_attr_name_expected_dict,
):
    remapped = remap_prefixed_keys(
        prefixed_defaults_dict,
        key_prefix,
        single_attr_name_simple_iterable
    )
    assert remapped == single_attr_name_expected_dict


def test_remap_prefixed_keys_returns_correct_remap_when_unprefixed_keys_is_dict_iterable(
    prefixed_defaults_dict,
    key_prefix,
    single_attr_name_key_source_dict,
    single_attr_name_expected_dict,
):
    remapped = remap_prefixed_keys(
        prefixed_defaults_dict,
        key_prefix,
        single_attr_name_expected_dict
    )
    assert remapped == single_attr_name_expected_dict
