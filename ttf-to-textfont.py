#!/usr/bin/python3
import sys
import getopt
import string
from typing import Tuple, Iterable

from PIL import ImageFont
from itertools import chain
from functools import cache


class CachingFontWrapper:
    """
    Caches conversions to avoid recreating masks and bboxes

    :param text:
    :return:
    """
    def __init__(self, font: ImageFont):
        self._font = font

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


def print_character(font, glyph, max_height, alignments):
    bitmap = font.getmask(glyph)
    bbox = font.getbbox(glyph)

    comment = [f"# {glyph} (ASCII: {ord(glyph)})"]

    if bbox is None:
        print(comment[0], "skipping empty glyph")
        print()
        return

    x1, y1, x2, y2 = bbox
    data_width = x2 - x1
    data_height = y2 - y1

    pre, post = 0, 0

    extra = max_height - data_height
    if glyph in alignments["center"]:
        comment.append(" (centered)")
        post = extra // 2
        pre = extra - post
    elif glyph in alignments["top"]:
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

    print(f"GLYPH: {ord(glyph)} {data_width} {max_height} {''.join(comment)}")

    pad_line = "." * data_width
    for i in range(pre):
        print(pad_line)

    line_raw = []
    for y in range(y1, y2):
        line_raw.clear()

        for x in range(x1, x2):
            if bitmap.getpixel((x, y)) > 0:
                char = "X"
            else:
                char = "."
            line_raw.append(char)
        print(''.join(line_raw))

    for i in range(post):
        print(pad_line)


def main(prog, argv):
    vert_center = set("~=%!#$()*+/<>@[]\{\}|")
    vert_top = set("^\"\'`")

    font_points = 8
    font_glyphs = string.printable

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

    alignments = {"top": vert_top, "center": vert_center}

    font = CachingFontWrapper(ImageFont.truetype(font_file, font_points))

    max_width, max_height = find_max_dimensions(font, font_glyphs)
    print(f"# {font_file}, {font_points} points, height {max_height} px, widest {max_width} px")
    print(f"# Exporting: {font_glyphs}")
    print(f"FONT: {max_width} {max_height}")

    for glyph in font_glyphs:
        print_character(font, glyph, max_height, alignments)


if __name__ == "__main__":
   main(sys.argv[0], sys.argv[1:])
