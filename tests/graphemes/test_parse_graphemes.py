"""
Test support of grapheme parsing

This includes both basic single-character graphemes and Zero-Width Joiner (ZJW)
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
    "expected",
    [
        # Country flags (with interesting historical alphabets)
        (
            "🇮🇸", # Iceland: Runes / Furthark
            "🇪🇬"  # Egypt  : Ancient Egyptian Hieroglyphics
        ),
        # Skin color
        (
            "🧙🏻", # Pale / Wizard
            "a",  # Filler disruption
            "🎅🏽", # Medium / Santa,
            "👍", # Thumbs up
            "✍🏿", # Dark / Holding Pen,
            "🫱🏿‍🫲🏻", # Handshake with dark hand and light hand
        ),
        # Various long emoji
        (
            "😶‍🌫️", # Face in clouds, a 4 component weather emoji
            ",", # padding
            "👨‍👩‍👧‍👦", # family of four
            ")", # padding
            "🧔‍♂️", # man with beard, 3 component emoji
            "1", # filler / padding
            "❤️‍🔥", # Heart on fire, a 4 component emoji
        ),
        # Animals
        (
            "🐻‍❄️", # Polar bear
            "🐕‍🦺", # Service dog
        )
    ]
)
def test_complex_sequence(expected):
    result = parse_graphemes(''.join(expected))
    assert result == expected
