from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class FontData:

    max_width: int
    max_height: int
    first_glyph: int = None
    last_glyph: int = None

    glyphs: Dict = field(default_factory=dict)

    @property
    def max_bbox(self) -> Tuple[int, int]:
        return self.max_width, self.max_height

    def __repr__(self):
        return f"<FontData {self.max_bbox!r}>"


FONT_HEADER = "FONT"
GLYPH_HEADER = "GLYPH"
