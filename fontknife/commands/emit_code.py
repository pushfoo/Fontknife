from contextlib import ExitStack
from typing import Any, Mapping

from fontknife.custom_types import PathLike
from fontknife.formats import RasterFont
from fontknife.iohelpers import StdOrFile
from fontknife.octo import emit_octo


def main(font: RasterFont, output: PathLike, output_args: Mapping[str, Any]):
    """
    Generate code from a font.

    :param font: Raster font data to write.
    :param output: A path or '-' indicating where to write output to.
    :param output_args: Prefix-stripped args to pass to emit_octo.
    :return:
    """
    with ExitStack() as output_streams:
        output_stream = output_streams.enter_context(StdOrFile(output, 'w')).raw
        emit_octo(output_stream, font, output_args['glyph_sequence'])
