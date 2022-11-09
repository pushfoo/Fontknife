from dataclasses import dataclass, field, fields

import pytest

from octofont3.utils import tuplemap


@dataclass
class AttrDummy:
    a: int = field(default=0)
    b: int = field(default=1)
    c: int = field(default=2)


class MutatesPropertyOnAccess:
    """
    A footgun of an object that changes the value of one of its
    every time it is accessed.
    """
    def __init__(self):
        self._times_accessed_prop = 0

    @property
    def times_accessed_prop(self):
        value_at_access_time = self._times_accessed_prop
        self._times_accessed_prop += 1
        return value_at_access_time


@dataclass
class HasAProp:
    a: int = field(default=0)

@dataclass
class HasBProp:
    b: int = field(default=1)


@pytest.fixture
def mutates_prop_on_access_instance():
    return MutatesPropertyOnAccess()


@pytest.fixture
def attr_dummy_reference_instance():
    return AttrDummy()


@pytest.fixture(params=tuplemap(lambda f: f.name, fields(AttrDummy)))
def attr_dummy_single_field(request):
    return request.param


@pytest.fixture
def attr_dummy_field_names(attr_dummy_reference_instance):
    return tuple(f.name for f in fields(type(attr_dummy_reference_instance)))


@pytest.fixture(params=['Default string', None])
def value_for_default_arg(request):
    return request.param
