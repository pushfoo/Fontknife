from typing import Dict, Iterable

# from fontknife.custom_types import Size, BoundingBox, ImageFontLike, BboxFancy


def calculate_alignments(vert_center: Iterable[str] = None, vert_top: Iterable[str] = None) -> Dict:
    alignments = {}
    vert_center = set(vert_center) if vert_center else set("~=%!#$()*+/<>@[]\{\}|")
    alignments["center"] = vert_center

    vert_top = set(vert_top) if vert_top else set("^\"\'`")
    alignments["top"] = vert_top

    return alignments


