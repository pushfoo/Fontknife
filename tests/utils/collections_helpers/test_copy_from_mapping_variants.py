import pytest

from octofont3.utils import copy_from_mapping, pop_items


@pytest.fixture
def reference_dict_missing_single_field(reference_dict, attr_dummy_single_field):
    d = dict(reference_dict)
    del d[attr_dummy_single_field]
    return d


# Set up some copies of dicts to mutate
@pytest.fixture
def mutation_copy_of_reference_dict(reference_dict):
    """
    Mutable copy of reference_dict because some getters are destructive.

    :param reference_dict: The original reference dict fixture.
    :return:
    """
    return dict(reference_dict)


@pytest.fixture
def mutation_copy_of_reference_dict_minus_single_field(reference_dict_missing_single_field):
    return dict(reference_dict_missing_single_field)


# Titular variants of copy_from_mapping
@pytest.fixture(params=[copy_from_mapping, pop_items])
def copier(request):
    return request.param


def test_copier_uses_non_mapping_iterables_of_keys_correctly(
    copier,
    reference_dict,
    mutation_copy_of_reference_dict,
    attr_dummy_field_names_as_non_mapping_iterable
):
    copied = copier(mutation_copy_of_reference_dict, attr_dummy_field_names_as_non_mapping_iterable)
    assert copied == reference_dict


def test_copier_copies_all_keys_when_no_keys_specified(
    copier,
    reference_dict,
    mutation_copy_of_reference_dict
):
    copied = copier(mutation_copy_of_reference_dict)
    assert copied == reference_dict


def test_copier_returns_empty_dict_when_passed_empty_non_mapping_iterable(
    copier,
    reference_dict,
    empty_non_mapping_iterable,
    empty_dict
):
    copied = copier(reference_dict, empty_non_mapping_iterable)
    assert copied == empty_dict


def test_copier_uses_defaults_when_needed_and_specified(
    copier,
    attr_dummy_single_field,
    reference_dict_missing_single_field,
    mutation_copy_of_reference_dict_minus_single_field,
    mapping_of_field_names_to_nones
):
    copied = copier(
        mutation_copy_of_reference_dict_minus_single_field,
        mapping_of_field_names_to_nones)

    assert copied[attr_dummy_single_field] is None
    for k, v in reference_dict_missing_single_field.items():
        assert copied[k] == v


def test_copier_ignores_defaults_when_not_needed_but_specified(
    copier,
    reference_dict,
    mutation_copy_of_reference_dict,
    attr_dummy_single_field,
    mapping_of_field_names_to_nones
):
    copied = copier(mutation_copy_of_reference_dict, mapping_of_field_names_to_nones)
    assert copied == reference_dict


def test_pop_items_removes_keyval_pairs_from_source_when_no_defaults(
    mutation_copy_of_reference_dict,
    attr_dummy_single_field,
    reference_dict_missing_single_field,
):
    pop_items(mutation_copy_of_reference_dict, (attr_dummy_single_field,))
    assert mutation_copy_of_reference_dict == reference_dict_missing_single_field


def test_pop_items_removes_keyval_pairs_from_source_when_defaults_specified_and_needed(
    mutation_copy_of_reference_dict_minus_single_field,
    mapping_of_field_names_to_nones
):
    pop_items(
        mutation_copy_of_reference_dict_minus_single_field,
        mapping_of_field_names_to_nones)
    assert mutation_copy_of_reference_dict_minus_single_field == {}


def test_pop_items_removes_keyval_pairs_from_source_when_defaults_specified_but_unneeded(
    mutation_copy_of_reference_dict,
    mapping_of_field_names_to_nones,
    empty_dict
):
    pop_items(
        mutation_copy_of_reference_dict,
        mapping_of_field_names_to_nones
    )
    assert mutation_copy_of_reference_dict == empty_dict


def test_pop_items_leaves_source_unchanged_when_key_source_is_empty_mapping_iterable(
    mutation_copy_of_reference_dict,
    reference_dict,
    empty_mapping_iterable
):
    pop_items(
        mutation_copy_of_reference_dict,
        empty_mapping_iterable
    )
    assert mutation_copy_of_reference_dict == reference_dict


def test_pop_items_leaves_source_unchanged_when_key_source_is_empty_non_mapping_iterable(
    mutation_copy_of_reference_dict,
    reference_dict,
    empty_non_mapping_iterable
):
    pop_items(
        mutation_copy_of_reference_dict,
        empty_non_mapping_iterable
    )
    assert mutation_copy_of_reference_dict == reference_dict




