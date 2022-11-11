from dataclasses import field, make_dataclass
from typing import Tuple, Iterable

import pytest


def as_map_iterator(it: Iterable):
    return map(lambda b: b, it)


# Use fixtures to access this instead of imports
_ATTR_DUMMY_FIELD_NAMES = ('a', 'b', 'c')


@pytest.fixture
def attr_dummy_field_names() -> Tuple[str, ...]:
    return _ATTR_DUMMY_FIELD_NAMES


@pytest.fixture(params=_ATTR_DUMMY_FIELD_NAMES)
def attr_dummy_single_field(request) -> str:
    return request.param


@pytest.fixture
def attr_dummy_default_values(attr_dummy_field_names) -> Tuple[int, ...]:
    return tuple(range(len(attr_dummy_field_names)))


@pytest.fixture
def num_default_fields(attr_dummy_default_values) -> int:
    return len(attr_dummy_default_values)


@pytest.fixture
def attr_dummy_defaults_dict(
    attr_dummy_field_names,
    attr_dummy_default_values
    # Return type left without annotation because of
    # type checker issues in next fixture.
):
    return {k: v for k, v in zip(attr_dummy_field_names, attr_dummy_default_values)}


@pytest.fixture
def attr_dummy_type(attr_dummy_defaults_dict) -> type:
    # Some type checkers get confused if this is inlined
    template = [(k, int, field(default=v)) for k, v in attr_dummy_defaults_dict.items()]
    attr_dummy = make_dataclass('AttrDummy', template)
    return attr_dummy


@pytest.fixture
def attr_dummy_field_names_as_non_mapping_iterable(
    attr_dummy_field_names, non_mapping_iterable_type
):
    return non_mapping_iterable_type(attr_dummy_field_names)


@pytest.fixture(params=(list, tuple, as_map_iterator))
def non_mapping_iterable_type(request):
    return request.param


@pytest.fixture(params=(dict,))
def mapping_iterable_type(request):
    return request.param


@pytest.fixture
def empty_non_mapping_iterable(non_mapping_iterable_type):
    return non_mapping_iterable_type(tuple())


@pytest.fixture
def empty_mapping_iterable(mapping_iterable_type):
    return mapping_iterable_type({})


@pytest.fixture
def mapping_of_field_names_to_nones(attr_dummy_field_names):
    """
    Provide an all-None defaults mapping for tests.

    Collections helpers can use a mapping iterable as a way to fill in
    gaps in a source object, and this fixture provides a blanket set of
    defaults for tests to use.
    """
    return {k: None for k in attr_dummy_field_names}
