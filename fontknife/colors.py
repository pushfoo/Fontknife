from typing import (
    Dict,
    FrozenSet,
    Tuple,
    Union,
    Final,
    Iterable
)


from fontknife.custom_types import ColorMode, ModeRGBA, ModeRGB, ModeL, Mode1, ModeAny
from fontknife.utils import cache, steps

MODE_TO_BYTE_SIZE: Dict[ColorMode, int] = {
    ModeRGBA: 4,
    ModeRGB: 2,
    ModeL: 1,
    Mode1: 1
}

MODES: FrozenSet[str] = frozenset(MODE_TO_BYTE_SIZE)
TUPLE_MODES: Final[FrozenSet[str]] = frozenset(
    mode for mode, size in MODE_TO_BYTE_SIZE.items() if size >= 1)
INT_MODES: Final[FrozenSet[str]] = frozenset(
    mode for mode, size in MODE_TO_BYTE_SIZE.items() if size == 1)


ColorRGBA = Tuple[int, int, int, int]
ColorRGB = Tuple[int, int, int]
ColorL = int
Color1 = int
ColorAny = Union[ColorRGBA, ColorRGB, ColorL, Color1]


@cache
def int_as_mode_color(gray: int, mode: ModeAny) -> ColorAny:
    """Return the monochrome gray value as a mode-appropriate color.

    :param mode: One of the following Pillow color modes:
        ``'RGBA'``, ``'RGB'``, ``'L'``, or ``'1'``.
    :param gray: The gray channel to convert to the passed color mode.

    :raises: NotImplementedError for modes other than those above.
     """
    if not 0 <= gray < 256:
        raise ValueError(f"Expected 0 <= gray <= 255, but got {gray}", gray)
    if mode not in MODES:
        raise ValueError(f"Unsupported color mode: {mode!r}")

    if mode == ModeRGBA:
        return gray, gray, gray, 255
    elif mode == ModeRGB:
        return gray, gray, gray
    return gray


def gray_mode_variations(
        gray: Union[ColorL, Color1],
        modes: Iterable[ModeAny] = MODES
) -> Dict[str, ColorAny]:
    """
    Return variations on the gray value for each passed mode.

    :param gray: An int monochrome gray value.
    :param modes: An iterable of mode strings.
    """
    # freeze consumable iterables and check for any invalid modes
    modes = tuple(modes)
    bad = set(modes) ^ MODES
    if bad:
        raise ValueError(f"Unsupported modes: {bad!r}")

    return {mode: int_as_mode_color(gray, mode) for mode in modes}


_MONO_STEPS: Tuple[str, ...] = (
    'BLACK',
    'DARK_GRAY',
    'MEDIUM_GRAY',
    'BRIGHT_GRAY',
    'WHITE'
)

COLOR_RAW_GRAYS: Final[Dict[str, int]] =\
    dict(zip(
        _MONO_STEPS,
        steps(0, 255, len(_MONO_STEPS), end_inclusive=True)
    ))

COLORS_FOR_MODES: Final[Dict[str, Dict[str, ColorAny]]] = {
    k: gray_mode_variations(v) for k, v in COLOR_RAW_GRAYS.items()
}


RGBA_WHITE: Final[ColorRGBA] = COLORS_FOR_MODES['WHITE'][ModeRGBA]
RGBA_BLACK: Final[ColorRGBA] = COLORS_FOR_MODES['BLACK'][ModeRGBA]
