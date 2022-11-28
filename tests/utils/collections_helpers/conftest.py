from dataclasses import asdict

import pytest

from fontknife.utils import getvalue, popvalue


@pytest.fixture
def attr_dummy_reference_instance(attr_dummy_type):
    return attr_dummy_type()


class MutatesPropertyOnAccess:
    """
    This class covers an edgecase in attribute testing such as attrs_eq.

    It's worth checking for since this project is intended to eventually
    be used as a library and not just a CLI tool.
    """
    def __init__(self):
        self._times_accessed_prop = 0

    @property
    def times_accessed_prop(self):
        value_at_access_time = self._times_accessed_prop
        self._times_accessed_prop += 1
        return value_at_access_time


@pytest.fixture
def empty_dict():
    return {}


@pytest.fixture
def reference_dict(attr_dummy_reference_instance):
    return asdict(attr_dummy_reference_instance)


@pytest.fixture
def mutates_prop_on_access_instance():
    return MutatesPropertyOnAccess()


@pytest.fixture(params=['Default string', None])
def value_for_default_arg(request):
    return request.param


@pytest.fixture(params=[getvalue, popvalue])
def mapping_getter(request):
    return request.param
