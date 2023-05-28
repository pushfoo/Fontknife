"""
Convert between formats.
"""
from typing import Any, Mapping

from fontknife.custom_types import PathLike
from fontknife.formats import write_font, RasterFont


def main(font: RasterFont, output: PathLike, output_args: Mapping[str, Any]):
    """
    Convert between font formats.

    :param font: Raster font data to write.
    :param output: A path or '-' indicating where to write output to.
    :param output_args: Prefix-stripped args to pass to write_font.
    :return:
    """
    # Set glyph sequence and attempt conversion
    write_font(font, output, **output_args)
