#!/usr/bin/python3
import sys
import getopt
import string

from PIL import ImageFont
from itertools import chain

from octofont3 import calculate_alignments
from octofont3.font_adapter import CachingFontAdapter
from octofont3.textfont.writer import FontRenderer


def main():
    prog, argv = sys.argv[0], sys.argv[1:]

    font_points = 8
    glyph_sequence = None

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
            glyph_sequence = arg
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

    # If no glyph order was specified, generate a default
    if glyph_sequence is None:
        exclude = set(chr(i) for i in chain(range(0, 31), range(128, 255)))
        glyph_sequence = ''.join(ch for ch in string.printable if ch not in exclude)

    # keep this here because someone might override it?
    alignments = calculate_alignments(vert_center=vert_center, vert_top=vert_top)
    raw_font = ImageFont.truetype(font_file, font_points)
    font = CachingFontAdapter(
        raw_font,
        alignments=alignments,
        require_glyph_sequence=tuple(glyph_sequence)
    )
    #show_image_for_text(raw_font, "Test text")
    renderer = FontRenderer(sys.stdout, verbose=False)
    renderer.emit_textfont(font, glyph_sequence)
    pass

if __name__ == "__main__":
   main()
