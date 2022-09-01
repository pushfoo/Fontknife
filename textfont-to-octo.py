#!/usr/bin/python3
import fileinput
import sys
import getopt
from dataclasses import dataclass, field
from math import log
from typing import Dict, Tuple, List, Optional


@dataclass
class FontData:

    max_width: int
    max_height: int
    first_glyph: int = None
    last_glyph: int = None

    glyphs: Dict = field(default_factory=dict)

    @property
    def max_bbox(self) -> Tuple[int, int]:
        return self.max_width, self.max_height

    def __repr__(self):
        return f"<FontData {self.max_bbox!r}>"


class FontParseError(BaseException):

    def __init__(self, message, filename: str, lineno: int):
        super().__init__(f"{filename}, line {lineno}: {message}")
        self.raw_message = message
        self.filename = filename
        self.lineno = lineno

    @classmethod
    def from_stream_state(cls, message, stream):
        return cls(message, stream.filename(), stream.lineno())


def split_tokens(line: str) -> Optional[List[str]]:

    if line == '':
        return None

    return line.rstrip().split(' ')


def strip_end_comments(line: str) -> str:
    comment_start_index = line.find("#")

    if comment_start_index < 0:
        return line

    return line[:comment_start_index]


def readline_and_split(stream, skip_comment_lines=True) -> Optional[List[str]]:

    if skip_comment_lines:
        raw_line = "#"
        while raw_line and (raw_line.startswith("#") or raw_line[0] == "\n"):
            raw_line = stream.readline()
    else:
        raw_line = stream.readline()
    line = strip_end_comments(raw_line)

    return split_tokens(line)


FONT_HEADER = "FONT"
GLYPH_HEADER = "GLYPH"


def parse_header_and_values(stream, expected_header: str = None) -> Optional[Tuple[str, Tuple[int, ...]]]:
    """
    Return None if empty line, otherwise a string + ints after it

    :param stream:
    :param expected_header:
    :return:
    """
    values = readline_and_split(stream)

    # exit early because we reached the end of the file
    if values is None:
        return None

    header = values[0]

    if expected_header is not None and header != f"{expected_header}:":
        raise FontParseError.from_stream_state(
            f"Expected header {expected_header}, but got {header}", stream
        )

    int_values = tuple(map(int, values[1:]))
    return header, int_values


# this will be refactored later...
def parse_glyph(stream, glyph_width, glyph_height):
    """

    Extract the data for this glyph from the font

    :param stream:
    :param font_data:
    :param ascii_code:
    :param glyph_width:
    :param glyph_height:
    :return:
    """
    raw_font_data = []

    for i in range(glyph_height):
        row_chars = stream.readline().rstrip()
        row_len = len(row_chars)
        if row_len != glyph_width:
            raise FontParseError.from_stream_state(
                f"Expected glyph row of width {glyph_width}, but got {row_len}"
            )
        raw_font_data.append(row_chars)

    return ''.join(raw_font_data)


def parse_textfont_file(stream) -> FontData:
    file_header, bounds = parse_header_and_values(stream, FONT_HEADER)

    font_data = FontData(*bounds)

    first_glyph = 255
    last_glyph = 0

    while glyph_header := parse_header_and_values(stream, GLYPH_HEADER):
        ascii_code, glyph_width, glyph_height = glyph_header[1]
        font_data.glyphs[ascii_code] = parse_glyph(stream, glyph_width, glyph_height)

        first_glyph = min(ascii_code, first_glyph)
        last_glyph = max(ascii_code, last_glyph)

    font_data.first_glyph = first_glyph
    font_data.last_glyph = last_glyph

    return font_data


def main(prog, argv):

    help = prog + ' <textfont-file>'
    try:
        opts, args = getopt.getopt(argv, "h")
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
    if len(args) != 1:
        print(help)
        sys.exit(2)

#    input_filename = args[0]

#    if input_filename == '-':
#        infile = std
    #infile = open(input_filename, "r")

    infile = fileinput.input()

    font_data = parse_textfont_file(infile)
#    print(f)
#    print(f.glyphs)
#    return

    # get the max height and max width of the font?
    # is this really needed? just reparse from it?
    # user COULD edit a font to be bigger...
    font_width = font_data.max_width
    font_height = font_data.max_height

    first_glyph = font_data.first_glyph
    last_glyph = font_data.last_glyph
    glyphs = font_data.glyphs
    #print glyphs


    if font_width == 0 or font_height == 0:
        print("Did not find font dimensions")
        sys.exit(2)
    if font_width > 8:
        print("Font width larger than 8 pixels, not yet supported")
        sys.exit(2)
    if font_height > 8:
        print("Font height larger than 8 pixels, not yet supported")
        sys.exit(2)

    compact_glyphtable = True

    kern_px = 1

    draw_char_reg = "v0"
    draw_x_reg = "v1"
    draw_y_reg = "v2"

    width_char_reg = "v0"

    prefix = "smallfont"


    offset = font_data.first_glyph

    # generate label names
    draw_func_name = prefix + "_draw_glyph"
    width_func_name = prefix + "_glyph_width"
    widthtable_name = prefix + "_width_table"
    glyphtable_name = prefix + "_glyph_table"

    # header
    print()
    available_chars = ''.join(chr(i) if i in glyphs else '' for i in range(255))
    print(f"# Font: {prefix}  Available characters: {available_chars}")

    # generate glyph drawing routine
    print()
    print(f"# Call with {draw_char_reg} = ASCII character, {draw_x_reg} = x, {draw_y_reg} = y")
    print(f"# Returns with {draw_x_reg} incremented by the width of the glyph plus {kern_px}")
    print(f"# Clobbers vF, I{'' if draw_char_reg == width_char_reg else ', ' + width_char_reg}")
    print(f"# Must not be called with {draw_char_reg} < {first_glyph} or {draw_char_reg} > {last_glyph}!")
    print(f": {draw_func_name}")
    print("  " + draw_char_reg + " += " + str(256-offset))
    print("  i := " + glyphtable_name)
    #for i in range(font_y):

    n_shift = int(log(font_height, 2))
    remainder = font_height - int(pow(n_shift, 2))

    if (n_shift * 2 + remainder + 1) >= font_height:
        n_shift = 0
        remainder = font_height

    if n_shift > 0:
        print(("  i += " + draw_char_reg) * remainder)
        print(("  " + draw_char_reg + " <<= " + draw_char_reg) * n_shift)
        print("  i += " + draw_char_reg)
        print(("  " + draw_char_reg + " >>= " + draw_char_reg) * n_shift)

    else:
        print(("  i += " + draw_char_reg) * remainder)

    print("  sprite " + draw_x_reg + " " + draw_y_reg + " " + str(font_height))

    if draw_char_reg != width_char_reg:
        print("  " + width_char_reg + " := " + draw_char_reg)

    print("  " + width_func_name + "_no_offset")
    print("  " + draw_x_reg + " += " + width_char_reg)
    print("  " + draw_x_reg + " += 1")
    print("  return")

    # returns width of a particular glyph
    print()
    print(f"# Call with {width_char_reg} = ASCII character")
    print(f"# Returns {width_char_reg} = width of glyph in pixels")
    print("# Clobbers vF, I")
    print(f"# Must not be called with {width_char_reg} < {first_glyph} or {width_char_reg} > {last_glyph}!")
    print(": " + width_func_name)
    print("  " + width_char_reg + " += " + str(256-offset))
    print(": " + width_func_name + "_no_offset")
    print("  i := " + widthtable_name)
    print("  i += " + width_char_reg)
    print("  load " + width_char_reg)
    print("  return")

    # string drawing routine
    print(": " + prefix + "draw_str")


    # print glyph width table
    width_str = ""
    for i in range(first_glyph, last_glyph + 1):
        if glyphs[i] == 0:
            w = 0
        else:
            w = len(glyphs[i]) // font_height
        width_str += "0x" + hex(w)[2:].zfill(2)

        if i != last_glyph:
            width_str += " "
        if i % 16 == 0:
            width_str += "\n" + " " * (len(widthtable_name) + 3)

    print(": " + widthtable_name + " " + width_str)


    # print glyph table
    glyph_str = ""
    count = 0
    for i in range(first_glyph, last_glyph + 1):
        if glyphs[i] == 0:
            w = 0
            s = ""
        else:
            w = len(glyphs[i]) // font_height
            s = glyphs[i]

        if not compact_glyphtable:
            glyph_str += "\n" + " " * (len(widthtable_name) + 3) + "# " + str(i) + " \'" + chr(i) + "\'\n" + ": " + "gl" + str(i) + " " + " " * (len(widthtable_name) + 3)

        for i in range(font_height):
            val = 0
            byte = s[0:w]
            s = s[w:]

            for i in range(8):

                if len(byte) > i:
                    val = (val << 1) | (1 if byte[i] == 'X' else 0)
                else:
                    val = val << 1
            glyph_str += "0x" + hex(val)[2:].zfill(2) + " "
            count += 1
            if compact_glyphtable and count % 16 == 0:
                glyph_str += '\n' + " " * (len(widthtable_name) + 3)

        #if i != last_glyph:
        #    glyph_str += "\n"
        #if i % 16 == 0:
        #    glyph_str += "\n" + " " * (len(widthtable_name) + 3)

    print(": " + glyphtable_name + " " + glyph_str)


#    print "# " + font_file + ", " + str(font_points) + " points, height " + str(max_height) + " px, widest " + str(max_width) + " px"
#    print "# Exporting: " + font_glyphs
#    print

#    for glyph in font_glyphs:
#        print_character(font, glyph, max_height, alignments)


if __name__ == "__main__":
   main(sys.argv[0], sys.argv[1:])
