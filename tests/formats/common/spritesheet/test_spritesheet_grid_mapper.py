"""
Tests for this class are intentionally left sparse.

The class will be rewritten as soon as the problem domain of sprite
existing sheet font formats is better understood. The current
implementation was written to get something working as quickly as
possible.
"""
import pytest

from fontknife.formats.common.spritesheet import GridMapper, GRID_MAPPER_DIM_NAMES
from fontknife.utils import get_attrs


@pytest.fixture
def grid_mapper_all_arg_names():
    return GRID_MAPPER_DIM_NAMES


@pytest.fixture
def grid_mapper_essential_arg_names(grid_mapper_all_arg_names):
    return grid_mapper_all_arg_names[:-1]


@pytest.fixture(params=[
    (
       (0, 0, 100, 100),
       (20, 20),
       (5, 5)
    ),
])
def essential_values_preset(request):
    return request.param


@pytest.fixture
def dict_essential_values_precomputed(
    grid_mapper_essential_arg_names,
    essential_values_preset
):
    return dict(zip(
        grid_mapper_essential_arg_names,
        essential_values_preset
    ))


@pytest.fixture(params=range(len(GRID_MAPPER_DIM_NAMES) - 1))
def single_grid_mapper_essential_arg_name(request, grid_mapper_essential_arg_names):
    return grid_mapper_essential_arg_names[request.param]


@pytest.fixture
def grid_mapper_essential_values_missing_one_key(
    dict_essential_values_precomputed,
    single_grid_mapper_essential_arg_name
):
    _d = dict(dict_essential_values_precomputed)
    _d.pop(single_grid_mapper_essential_arg_name)
    return _d


@pytest.fixture
def grid_mapper_computed_values_instance(grid_mapper_essential_values_missing_one_key):
    return GridMapper(**grid_mapper_essential_values_missing_one_key)


@pytest.fixture(params=(
        # offsets to
        lambda len_: -1,  # Negative indices aren't supported
        lambda len_: len_,  # Off by 1 error past bounds of sheet
        lambda len_: len_ + 1005  # Absurdly high index
))
def bad_index_value_offset_func(request):
    return request.param


@pytest.fixture
def expected_grid_mapper_computed_length(dict_essential_values_precomputed):
    width, height = dict_essential_values_precomputed['sheet_size_tiles']
    return width * height


@pytest.fixture
def bad_raw_index_value(expected_grid_mapper_computed_length, bad_index_value_offset_func) -> int:
    return bad_index_value_offset_func(expected_grid_mapper_computed_length)


def test_grid_mapper_computes_essential_values_correctly(
    grid_mapper_computed_values_instance,
    grid_mapper_essential_values_missing_one_key,
    dict_essential_values_precomputed,
    grid_mapper_essential_arg_names
):
    calculated_values = get_attrs(grid_mapper_computed_values_instance, grid_mapper_essential_arg_names)
    assert calculated_values == dict_essential_values_precomputed


@pytest.fixture
def grid_mapper_instance(dict_essential_values_precomputed):
    return GridMapper(**dict_essential_values_precomputed)


@pytest.fixture
def test_len(grid_mapper_instance, expected_grid_mapper_computed_length):
    assert len(grid_mapper_instance) == expected_grid_mapper_computed_length


@pytest.fixture(params=(1.0, "1"))
def bad_raw_index_type(request):
    return request.param


def test_subscript_raises_key_error_on_type_other_than_int(grid_mapper_instance, bad_raw_index_value):
    with pytest.raises(KeyError):
        grid_mapper_instance[bad_raw_index_value]


def test_subscript_raises_type_error_on_type_other_than_int(grid_mapper_instance, bad_raw_index_type):
    with pytest.raises(TypeError):
        grid_mapper_instance[bad_raw_index_type]


# Ugly, should be replaced with functions, probably
@pytest.mark.parametrize(
    ('index_value', 'expected_coord'), [
        (0, (0, 0)),
        (19, (19, 0)),
        (20, (0, 1)),
        (399, (19, 19))
    ]
)
def test_coord_for_sheet_index_returns_correct_values(
    grid_mapper_computed_values_instance,
    index_value,
    expected_coord
):
    gotten = grid_mapper_computed_values_instance.coord_for_sheet_index(index_value)
    assert gotten == expected_coord


def test_coord_for_sheet_index_raises_key_error_on_invalid_int_value(
    grid_mapper_instance,
        bad_raw_index_value
):
    with pytest.raises(KeyError):
        grid_mapper_instance.coord_for_sheet_index(bad_raw_index_value)


def test_coord_for_sheet_index_raises_type_error_on_type_other_than_int(grid_mapper_instance, bad_raw_index_type):
    with pytest.raises(TypeError):
        grid_mapper_instance[bad_raw_index_type]
