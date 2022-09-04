#!/usr/bin/python3
import sys
import getopt
import string
from typing import Tuple, Iterable, Optional, Dict

from PIL import ImageFont
from itertools import chain
from functools import cache

from octofont3.iohelpers import OutputHelper


def calculate_alignments(vert_center: Iterable[str] = None, vert_top: Iterable[str] = None) -> Dict:
    alignments = {}
    vert_center = set(vert_center) if vert_center else set("~=%!#$()*+/<>@[]\{\}|")
    alignments["center"] = vert_center

    vert_top = set(vert_top) if vert_top else set("^\"\'`")
    alignments["top"] = vert_top

    return alignments


class CachingFontWrapper:
    """
    Mimics font object API & caches returns for certain calls

    :param font: The font object wrapped
    :param size: An optional override for storing size
    :param alignments: Overriding alignment data, if any
    :return:
    """
    def __init__(
        self,
        font: ImageFont,
        size: Optional[int] = None,
        alignments: Optional[Dict] = None
    ):
        self._font = font
        self._size = size

        if alignments is not None:
            self._alignments = alignments
        else:
            self._alignments = calculate_alignments()

    @property
    def path(self):
        return self._font.path

    @property
    def size(self):

        if self._size:
            return self._size

        return self._font.size

    @property
    def alignments(self) -> Dict:
        return self._alignments

    @property
    def font(self) -> ImageFont:
        return self._font

    @cache
    def getmask(self, text: str, mode: str = "1"):
        return self._font.getmask(text, mode)

    @cache
    def getbbox(self, text: str, mode: str = "1") -> Tuple[int, int, int, int]:
        return self.getmask(text, mode).getbbox()


def find_max_dimensions(font: CachingFontWrapper, glyphs: Iterable[str]) -> Tuple[int, int]:
    """
    Get the size of the tile that will fit every glyph requested

    :param font: The font to evaluate
    :param glyphs: which glyphs to use
    :return: the max glyph width and max glyph height for the font
    """
    max_width, max_height = 0, 0
    for glyph in glyphs:
        bbox = font.getbbox(glyph)

        if bbox is not None:

            x1, y1, x2, y2 = bbox
            max_height = max(y2-y1, max_height)
            max_width = max(x2-x1, max_width)

    return max_width, max_height


class TextfontStream(OutputHelper):

    def __init__(self, stream):
        super().__init__(stream)

    def header(self, header: str, *objects, sep=" ", end="\n"):
        self.print(f"{header}: ", end="")
        self.print(*objects, sep=sep, end=end)


def emit_character(stream, font, glyph, max_height):

    bitmap = font.getmask(glyph)
    bbox = font.getbbox(glyph)

    comment = [f"# {glyph} (ASCII: {ord(glyph)})"]

    if bbox is None:
        stream.print(comment[0], "skipping empty glyph")
        stream.print()
        return

    x1, y1, x2, y2 = bbox
    data_width = x2 - x1
    data_height = y2 - y1

    pre, post = 0, 0

    extra = max_height - data_height

    if glyph in font.alignments["center"]:
        comment.append(" (centered)")
        post = extra // 2
        pre = extra - post

    elif glyph in font.alignments["top"]:
        comment.append(" (align-top)")
        post = extra

        # Move one pixel down from the top if the glyph is really short
        if post > data_height:
            post -= 1
            pre = 1
    else:
        comment.append(" (align-bot)")
        pre = extra

    #print comment

    stream.header("GLYPH", ord(glyph), data_width, max_height, ''.join(comment))

    pad_line = "." * data_width
    for i in range(pre):
        stream.print(pad_line)

    line_raw = []
    for y in range(y1, y2):
        line_raw.clear()

        for x in range(x1, x2):
            if bitmap.getpixel((x, y)) > 0:
                char = "X"
            else:
                char = "."
            line_raw.append(char)
        stream.print(''.join(line_raw))

    for i in range(post):
        stream.print(pad_line)


def emit_textfont(stream, font: CachingFontWrapper, font_glyphs: Iterable[str]):
    s = stream
    max_width, max_height = find_max_dimensions(font, font_glyphs)
    s.comment(f"{font.path}, {font.size} points, height {max_height} px, widest {max_width} px")
    s.comment(f"Exporting: {font_glyphs}")
    s.header("FONT", max_width, max_height)

    for glyph in font_glyphs:
        emit_character(stream, font, glyph, max_height)


def main():
    prog, argv = sys.argv[0], sys.argv[1:]


    font_points = 8
    font_glyphs = string.printable

    vert_center = None
    vert_top = None

    help = prog + '[-p <point-size>] [-g <glyphs-to-extract>] [-c <glyphs-to-center>] [-t <glyphs-to-align-top>] <fontfile>'
    try:
        opts, args = getopt.getopt(argv,"hg:p:c:t:")
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
        elif opt == '-g':
            font_glyphs = arg
        elif opt == '-p':
            font_points = int(arg)
        elif opt == '-c':
            vert_center = arg
        elif opt == '-t':
            vert_top = arg

    if len(args) != 1:
        print(help)
        sys.exit(2)

    font_file = args[0]

    # Remove unprintable characters
    exclude = set(chr(i) for i in chain(range(0, 31), range(128, 255)))
    font_glyphs = ''.join(ch for ch in font_glyphs if ch not in exclude)

    # keep this here because someone might override it?
    alignments = calculate_alignments(vert_center=vert_center, vert_top=vert_top)

    font = CachingFontWrapper(
        ImageFont.truetype(font_file, font_points),
        alignments=alignments
    )
    stream = TextfontStream(sys.stdout)
    emit_textfont(stream, font, font_glyphs)


if __name__ == "__main__":
   main()
