import pytest

from octofont3.utils import remap, tuplemap


def increment_ord(base: str, increment: int):
    ords = tuplemap(ord, base)
    finished = ''.join(chr(o + increment) for o in ords)
    return finished


@pytest.fixture
def key_remapper_func(num_default_fields):
    return lambda s: increment_ord(s, num_default_fields)


@pytest.fixture
def remapped_keys(attr_dummy_field_names, key_remapper_func):
    return tuplemap(key_remapper_func, attr_dummy_field_names)


@pytest.fixture
def remapped_single_key(attr_dummy_single_field, key_remapper_func):
    return key_remapper_func(attr_dummy_single_field)


@pytest.fixture
def expected_remapping_of_default_keys_and_values(remapped_keys, attr_dummy_default_values):
    return {k: v for k, v in zip(remapped_keys, attr_dummy_default_values)}


@pytest.fixture
def remapping_table_for_default_keys(attr_dummy_defaults_dict):
    # Generate a shifted version of the table
    table = {}
    len_defaults = len(attr_dummy_defaults_dict)
    for k in attr_dummy_defaults_dict:
        table[k] = increment_ord(k, len_defaults)
    return table


def test_remap_returns_empty_on_full_source_with_empty_remapping_table(attr_dummy_defaults_dict):
    remapped = remap(attr_dummy_defaults_dict, {})
    assert remapped == {}


def test_remap_returns_empty_on_empty_source_and_empty_remapping_table():
    remapped = remap({}, {})
    assert remapped == {}


def test_remap_alters_all_keys_when_remapping_table_covers_all_members(
    attr_dummy_defaults_dict,
    remapping_table_for_default_keys,
    expected_remapping_of_default_keys_and_values
):
    remapped = remap(attr_dummy_defaults_dict, remapping_table_for_default_keys)
    assert expected_remapping_of_default_keys_and_values == remapped


def test_remap_returns_correct_pair_subset_when_remapping_table_covers_one_key(
    attr_dummy_defaults_dict,
    attr_dummy_single_field,
    remapped_single_key,
    expected_remapping_of_default_keys_and_values
):
    remapped = remap(attr_dummy_defaults_dict, {attr_dummy_single_field: remapped_single_key})
    # <= is a neat trick for dictionary item view comparison.
    # It reportedly runs faster than converting to set pairs, and seems
    # to be more flexible as well.
    assert remapped.items() <= expected_remapping_of_default_keys_and_values.items()
