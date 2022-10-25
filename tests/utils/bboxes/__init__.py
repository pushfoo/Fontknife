from typing import Tuple, Callable

import pytest

from octofont3.custom_types import BboxSimple, BoundingBox, BboxFancy
from octofont3.utils import BboxEnclosingAll


BBOX_TYPE_FACTORIES: Tuple[Callable[[BboxSimple, ], BoundingBox], ...] = (
    tuple,
    list,
    BboxFancy,
    BboxEnclosingAll,
)


@pytest.fixture(params=BBOX_TYPE_FACTORIES)
def bbox_type(request):
    return request.param


@pytest.fixture(scope='package')
def prefilled_bbox_values() -> Tuple[int, int, int, int]:
    return 1, 2, 3, 4


@pytest.fixture(params=[list, tuple])
def sequence_type(request):
    return request.param


@pytest.fixture
def prefilled_bbox_of_type(prefilled_bbox_values, bbox_type):
    return bbox_type(prefilled_bbox_values)
