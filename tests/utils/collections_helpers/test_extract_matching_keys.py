"""
Instead of compacting some tests with more complicated fixtures, it's
being left as-is on the basis of "Explicit is better than implicit."
"""

import re

import pytest

from octofont3.utils import extract_matching_keys


@pytest.fixture(params=[str, re.compile])
def regex_type_converter(request):
    return request.param


@pytest.fixture
def abc_regex_of_type(regex_type_converter):
    return regex_type_converter('[a-c]$')


@pytest.fixture
def nonmatching_keys():
    return (str(i) for i in range(3))


@pytest.fixture
def mapping_with_nonmatching_keys(nonmatching_keys):
    return {k: v for v, k in enumerate(nonmatching_keys)}


def test_extract_matching_keys_returns_empty_tuple_for_empty_simple_key_iterable_with_no_matching_keys(
    empty_non_mapping_iterable,
    abc_regex_of_type,
):
    extracted = extract_matching_keys(empty_non_mapping_iterable, abc_regex_of_type)
    assert extracted == tuple()


def test_extract_matching_keys_returns_empty_tuple_for_empty_mapping_iterable_with_no_matching_keys(
    empty_mapping_iterable,
    abc_regex_of_type
):
    extracted = extract_matching_keys(empty_mapping_iterable, abc_regex_of_type)
    assert extracted == tuple()


def test_extract_matching_keys_returns_empty_tuple_for_simple_iterable_with_no_matching_keys(
    nonmatching_keys,
    abc_regex_of_type
):
    extracted = extract_matching_keys(nonmatching_keys, abc_regex_of_type)
    assert extracted == tuple()


def test_extract_matching_keys_returns_empty_tuple_for_mapping_iterable_with_no_matching_keys(
    mapping_with_nonmatching_keys,
    abc_regex_of_type
):
    extracted = extract_matching_keys(mapping_with_nonmatching_keys, abc_regex_of_type)
    assert extracted == tuple()


def test_extract_matching_matching_keys_returns_correct_keys_for_simple_iterable_source(
    attr_dummy_field_names_as_non_mapping_iterable,
    abc_regex_of_type,
    attr_dummy_field_names,
):
    extracted = extract_matching_keys(attr_dummy_field_names_as_non_mapping_iterable, abc_regex_of_type)
    assert extracted == attr_dummy_field_names


def test_extract_matching_matching_keys_returns_correct_keys_for_mapping_source(
    attr_dummy_defaults_dict,
    abc_regex_of_type,
    attr_dummy_field_names,
):
    extracted = extract_matching_keys(attr_dummy_defaults_dict, abc_regex_of_type)
    assert extracted == attr_dummy_field_names
