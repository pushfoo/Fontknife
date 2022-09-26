from pathlib import Path

from PIL.BdfFontFile import BdfFontFile


def load_bdf(path: Path):
    font = None

    with open(path, "rb") as raw_file:
        font = BdfFontFile(raw_file)

    return font
