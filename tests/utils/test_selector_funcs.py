import pytest

from octofont3.utils import max_not_none, min_not_none


@pytest.fixture(params=[max_not_none, min_not_none])
def selector_function(request):
    return request.param


def test_raises_value_error_when_multiple_none_positionals(selector_function):
    with pytest.raises(ValueError):
        a = selector_function(None, None)


def test_raises_value_error_when_single_empty_iterable(selector_function):
    with pytest.raises(ValueError):
        a = selector_function([])


def test_raises_value_error_when_single_iterable_all_nones(selector_function):
    with pytest.raises(ValueError):
        a = selector_function([None, None])
