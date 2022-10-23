import pytest

from octofont3.custom_types import BboxFancy
from . import prefilled_bbox_values


def test_hash(prefilled_bbox_values):
    assert hash(BboxFancy(*prefilled_bbox_values)) == hash(prefilled_bbox_values)


@pytest.mark.parametrize('source_args', (
    ((0, 0, 7, 8),),  # a full bbox
    ((7, 8),),  # a size
    (0, 0, 7, 8)  # plain int arguments
))
def test_convert_classmethod(source_args):
    bbox = BboxFancy.convert(*source_args)
    assert bbox == (0, 0, 7, 8)