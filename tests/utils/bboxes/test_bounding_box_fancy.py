from octofont3.custom_types import BboxFancy
from . import prefilled_bbox_values


def test_hash(prefilled_bbox_values):
    assert hash(BboxFancy(*prefilled_bbox_values)) == hash(prefilled_bbox_values)
