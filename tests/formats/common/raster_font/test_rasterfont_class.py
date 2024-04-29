from typing import List, Iterable, Tuple, Union, Mapping, Sequence
from string import ascii_letters, ascii_uppercase, hexdigits

import pytest
from PIL import Image

from fontknife.custom_types import ModeConflictError, MissingGlyphError, ModeAny
from fontknife.formats import RasterFont
from fontknife.formats.common.raster_font import GlyphMetadata, GlyphMaskMapping, GlyphMetadataMapping
from fontknife.colors import int_as_mode_color, MODES, ColorAny


@pytest.fixture(params=(ascii_letters, ascii_uppercase, hexdigits))
def ascii_subset(request):
    return request.param


@pytest.fixture(params=[(10, 10)])
def size(request):
    return request.param


@pytest.fixture(params=MODES)
def mode(request) -> str:
    return request.param


@pytest.fixture
def white_for_mode(mode) -> Union[Tuple[int, ...], int]:
    return int_as_mode_color(255, mode)


def raw_mode_variants(
        size: Tuple[int, int],
        modes: Iterable[str] = MODES,
        gray: int = 255
) -> List[Image.Image]:
    return [Image.new(mode, size, int_as_mode_color(gray, mode)) for mode in modes]


def build_tables(
        raw: Union[Iterable[Image.Image], Mapping[str, Image.Image]]
) -> Tuple[GlyphMaskMapping, GlyphMetadataMapping]:
    """
    A parallel implementation of glyph table calculation for tests.

    If ``raw`` is not a mapping, the resulting tables will start with
    ``'0'`` as their mapped character.

    It's simpler than the one currently used since it assumes the
    modes area already converted as needed.
    """
    if isinstance(raw, Mapping):
        source = raw
    else:
        source = {chr(ord('0') + index): image for index, image in enumerate(raw)}

    bitmaps = {}
    metadata = {}

    for glyph, image in source.items():
        image_core = image.im
        bitmaps[glyph] = image.im
        metadata[glyph] = GlyphMetadata.from_font_glyph(image.size, image_core)

    return bitmaps, metadata


def test_init_mode_reading_sets_none_on_empty_data():
    r = RasterFont()
    assert r.mode is None


def test_init_mode_reading_raises_valueerror_when_multiple_modes(size):
    raw_images = raw_mode_variants(size)
    images, metadata = build_tables(raw_images)

    with pytest.raises(ModeConflictError):
        _ = RasterFont(images, metadata)


def test_init_mode_reading_raises_valueerror_with_correct_unique_mismatches(size):
    _modes = tuple(MODES)
    raw_images = raw_mode_variants(size, modes=(_modes[0],) + _modes + (_modes[-1],))
    images, metadata = build_tables(raw_images)

    try:
        _ = RasterFont(images, metadata)
        pytest.fail("The test should raise an exception before hitting this.")

    except ModeConflictError as e:
        assert tuple(e.mismatched) == _modes


@pytest.mark.parametrize("mode", MODES)
def test_init_mode_reading_sets_mode_when_all_same_mode(
        size,
        mode: ModeAny,
        white_for_mode: ColorAny
):

    raw_images = [Image.new(mode, size, white_for_mode) for i in range(5)]
    images, metadata = build_tables(raw_images)

    raster_font = RasterFont(images, metadata)
    assert raster_font.mode == mode


@pytest.mark.parametrize("method_name", ('getsize', 'getmask'))
@pytest.mark.parametrize("contains_missing_glyphs", ("☹️", "alphabet is missing from examples"))
def test_glyph_dependent_methods_raise_missingglypherror_when_glyphs_missing(
        size,
        mode: ModeAny,
        white_for_mode: ColorAny,
        method_name: str,
        contains_missing_glyphs: str
):
    images, metadata = build_tables(Image.new(mode, size, white_for_mode) for i in range(5))
    r = RasterFont(images, metadata)

    with pytest.raises(MissingGlyphError):
        assert getattr(r, method_name)(contains_missing_glyphs)


def test_getsize_returns_size(
        mode: ModeAny,
        ascii_subset: Sequence[str]):
    ascii_grays = {}
    for index, letter in enumerate(ascii_subset):
        code = ord(letter)
        ascii_grays[letter] = Image.new(mode, (index + 1, 10), int_as_mode_color(code, mode))

    images, metadata = build_tables(ascii_grays)
    raster_font = RasterFont(images, metadata)
    expected_width = len(ascii_subset) + sum(range(len(ascii_subset))), 10
    size = raster_font.getsize(''.join(ascii_subset))
    assert size == expected_width
