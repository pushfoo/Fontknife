#!/usr/bin/python3
import sys
import getopt
import string
from PIL import ImageFont
from itertools import chain


def find_max_height(font, glyphs):
    max_height = 0
    for g in glyphs:
        bitmap = font.getmask(g, "1")
        bbox = bitmap.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            max_height = max(y2-y1, max_height)
    return max_height


def find_max_width(font, glyphs):
    max_width = 0
    for g in glyphs:
        bitmap = font.getmask(g, "1")
        bbox = bitmap.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            max_width = max(x2-x1, max_width)
    return max_width


def print_character(font, glyph, max_height, alignments):
    bitmap = font.getmask(glyph, "1")
    bbox = bitmap.getbbox()

    comment = f"# {glyph} (ASCII: {ord(glyph)})"

    if bbox is None:
        print(comment, "skipping empty glyph")
        print()
        return

    x1, y1, x2, y2 = bbox

    pre, post = 0, 0

    extra = max_height - (y2-y1)
    if glyph in alignments["center"]:
        comment += " (centered)"
        post = extra // 2
        pre = extra - post
    elif glyph in alignments["top"]:
        comment += " (align-top)"
        post = extra

        # Move one pixel down from the top if the glyph is really short
        if post > (y2 - y1):
            post -= 1
            pre = 1
    else:
        comment += " (align-bot)"
        pre = extra

    #print comment

    print(f"GLYPH: {ord(glyph)} {x2-x1} {max_height} {comment}")

    for i in range(pre):
        print("." * (x2-x1))

    for y in range(y1, y2):
        s = ""
        for x in range(x1, x2):
            if bitmap.getpixel((x, y)) > 0:
                s += "X"
            else:
                s += "."
        print(s)

    for i in range(post):
        print("." * (x2-x1))


def main(prog, argv):
    vert_center = "~=%!#$()*+/<>@[]\{\}|"
    vert_top = "^\"\'`"

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

    font = ImageFont.truetype(font_file, font_points)

    max_height = find_max_height(font, font_glyphs)
    max_width = find_max_height(font, font_glyphs)

    print("# " + font_file + ", " + str(font_points) + " points, height " + str(max_height) + " px, widest " + str(max_width) + " px")
    print("# Exporting: " + font_glyphs)
    print("FONT: " + str(max_width) + " " + str(max_height))

    for glyph in font_glyphs:
        print_character(font, glyph, max_height, alignments)


if __name__ == "__main__":
   main(sys.argv[0], sys.argv[1:])
