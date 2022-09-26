from pathlib import Path

from PIL.PcfFontFile import PcfFontFile


def load_pcf(path: Path):
    font = None

    with open(path, "rb") as raw_file:
        font = PcfFontFile(raw_file)

    return font
