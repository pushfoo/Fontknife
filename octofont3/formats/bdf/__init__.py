from pathlib import Path

from PIL.BdfFontFile import BdfFontFile
from PIL.PcfFontFile import PcfFontFile


def load_raw_pil_convertable_bitfont(
        path: Path,
        force_font_type: str = None,
):
    font_format = force_font_type or path.suffix[1:]
    font = None

    with open(path, "rb") as raw_file:
        if font_format == "bdf":
            font = BdfFontFile(raw_file)
        elif font_format == "pcf":
            font = PcfFontFile(raw_file)
        else:
            raise ("Unknown file type")

    return font
