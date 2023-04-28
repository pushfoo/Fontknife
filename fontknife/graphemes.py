from functools import lru_cache
from typing import Tuple, cast, Optional

import regex

ASCII_COMMON_SHEET_MEMBERS = tuple(chr(i) for i in range(32, 127))  # Space through tilda (~)
UNICODE_GRAPHEME_REGEX = regex.compile(r'\X')  # noqa: W605 # Allow extended regex module's escapes


@lru_cache
def parse_graphemes(source: str, limit: Optional[int] = None) -> Optional[Tuple[str, ...]]:
    matches = UNICODE_GRAPHEME_REGEX.findall(source)
    num_matches = len(matches)

    if limit is not None:
        if limit.__class__ is not int:
            raise TypeError(f'limit must be None or an integer of value 1 or greater, not {limit!r}')
        elif limit <= 0:
            raise ValueError(f'limit must have value 1 or greater, not {limit!r}')
        elif num_matches > limit:
            raise ValueError(f'source has more matches ({num_matches} than passed limit allows ({limit})')

    return cast(Tuple[str], tuple(UNICODE_GRAPHEME_REGEX.findall(source)))


def cli_grapheme_arg(source: Optional[str]) -> Optional[Tuple[str, ...]]:
    if source is None:
        return None
    return parse_graphemes(source)

