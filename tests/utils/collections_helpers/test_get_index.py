from enum import Enum, auto

import pytest

from octofont3.utils import get_index
from . import value_for_default_arg

@pytest.fixture
def sequence_raw_values():
    return -1, 0, 1, 2, 3, 4


class ValidSeqPosition(Enum):
    START = auto()
    MID = auto()
    END = auto()
    START_NEG = auto()
    END_NEG = auto()


@pytest.fixture(params=[list, tuple])
def sequence_of_type(request, sequence_raw_values):
    return request.param(sequence_raw_values)


@pytest.fixture(params=tuple(e for e in ValidSeqPosition))
def good_int_index(request, sequence_raw_values) -> int:
    position_enum = request.param
    raw_len = len(sequence_raw_values)

    if position_enum is ValidSeqPosition.START:
        return 0
    elif position_enum is ValidSeqPosition.MID:
        return raw_len // 2
    elif position_enum is ValidSeqPosition.END:
        return raw_len - 1
    elif position_enum is ValidSeqPosition.END_NEG:
        return -1
    else:
        return -1 * (raw_len - 1)


@pytest.fixture(params=(-100, 100))
def bad_int_index(request) -> int:
    return request.param


def test_get_index_returns_default_when_seq_is_none(good_int_index, value_for_default_arg):
    assert value_for_default_arg == get_index(None, good_int_index, value_for_default_arg)


def test_get_index_returns_correct_values_for_good_indices_when_default_not_specified(
    sequence_of_type,
    sequence_raw_values,
    good_int_index
):
    assert get_index(sequence_of_type, good_int_index) == sequence_raw_values[good_int_index]


def test_get_index_returns_correct_values_for_good_indices_when_default_is_specified(
    sequence_of_type,
    sequence_raw_values,
    good_int_index,
    value_for_default_arg
):
    assert get_index(sequence_of_type, good_int_index, value_for_default_arg) == sequence_raw_values[good_int_index]


def test_get_index_raises_index_error_for_bad_indices_when_default_not_specified(
    sequence_of_type,
    bad_int_index
):
    with pytest.raises(IndexError):
        get_index(sequence_of_type, bad_int_index)


def test_get_index_returns_default_for_bad_indices_when_default_specified(
    sequence_of_type,
    bad_int_index,
    value_for_default_arg
):
    assert get_index(sequence_of_type, bad_int_index, value_for_default_arg) == value_for_default_arg


def test_wrong_index_type_raises_type_error_when_default_specified(
    sequence_of_type, value_for_default_arg
):
    with pytest.raises(TypeError):
        value = get_index(sequence_of_type, "e", value_for_default_arg)


def test_wrong_index_type_raises_type_error_when_default_not_specified(sequence_of_type):
    with pytest.raises(TypeError):
        value = get_index(sequence_of_type, "e")
