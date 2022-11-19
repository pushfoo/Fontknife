from contextlib import ExitStack
from typing import Any, Mapping

from octofont3.custom_types import PathLike
from octofont3.formats import RasterFont
from octofont3.iohelpers import StdOrFile
from octofont3.octo import emit_octo


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
