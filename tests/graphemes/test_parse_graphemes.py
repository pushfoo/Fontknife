"""
Test support of grapheme parsing

This includes both basic single-character graphemes and Zero-Width Joiner (ZWJ)
sequences, such as:

* Skin color modifiers
* Region flags
* Long sequences of 3+ components, such as advanced weather emoji

"""
import string
import pytest

from fontknife.graphemes import parse_graphemes


def test_parses_basic_ascii():
    expected = tuple(string.printable)
    result = parse_graphemes(string.printable)
    assert expected == result


@pytest.mark.parametrize(
    "separate_graphemes",
    # Each emoji-bearing string in these tuples is a zero-width joiner
    # sequence. Therefore, running ''.join(any_tuple_in_these) returns
    # a string which correct ZWJ sequence parsing should return as the
    # exact same result.
    [
        # Country flags (with interesting historical alphabets)
        (
            "🇮🇸",  # Iceland: Runes / Futhark
            "🇪🇬"  # Egypt  : Ancient Egyptian Hieroglyphics
        ),
        # Skin color
        (
            "🧙🏻",  # Pale / Wizard
            "a",  # Filler disruption
            "🎅🏽",  # Medium / Santa,
            "👍",  # Thumbs up
            "✍🏿",  # Dark / Holding Pen,
            "🫱🏿‍🫲🏻",  # Handshake with dark hand and light hand
        ),
        # Various long emoji
        (
            "😶‍🌫️", # Face in clouds, a 4 component weather emoji
            ",", # padding (not a ZJW sequence)
            "👨‍👩‍👧‍👦", # family of four
            ")",  # test padding (not a ZJW sequence)
            "🧔‍♂️",  # man with beard, 3 component emoji
            "1",  # padding (not a ZJW sequence)
            "❤️‍🔥", # Heart on fire, a 4 component emoji
        ),
        # Animals
        (
            "🐻‍❄️",  # Polar bear
            "🐕‍🦺",  # Service dog
        )
    ]
)
def test_complex_sequence(separate_graphemes):
    as_one_string = ''.join(separate_graphemes)
    result = parse_graphemes(as_one_string)
    assert result == separate_graphemes
