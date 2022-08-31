#!/usr/bin/python3
import fileinput
import sys
import getopt
from math import log


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

    font_x = 0
    font_y = 0
    glyph_num = 0
    glyph_line = 0

    first_glyph = 255
    last_glyph = 0

    glyphs = dict()

    # parse the textfont file to extract metadata & glyphs
    for l in infile:
        #print l
        l = l.replace("\n", "")
        l = l.replace("\r", "")
        words = l.split(' ')

        #print words
        if words[0].upper() == "FONT:":
            font_x = int(words[1])
            font_y = int(words[2])

        elif words[0].upper() == "GLYPH:":
            glyph_num = int(words[1])
            first_glyph = min(glyph_num, first_glyph)
            last_glyph = max(glyph_num, last_glyph)
            glyph_x = int(words[2])
            glyph_y = int(words[3])
            glyph_line = 0
            glyphs[glyph_num] = ""
        elif glyph_num != 0:
            line_dots = words[0]
            glyphs[glyph_num] += line_dots
            glyph_line += 1

    #print glyphs


    if font_x == 0 or font_y == 0:
        print("Did not find font dimensions")
        sys.exit(2)
    if font_x > 8:
        print("Font width larger than 8 pixels, not yet supported")
        sys.exit(2)
    if font_y > 8:
        print("Font height larger than 8 pixels, not yet supported")
        sys.exit(2)

    compact_glyphtable = True

    kern_px = 1

    draw_char_reg = "v0"
    draw_x_reg = "v1"
    draw_y_reg = "v2"

    width_char_reg = "v0"

    prefix = "smallfont"

    offset = first_glyph

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
    print(f"# Call with {draw_char_reg}  = ASCII character, {draw_x_reg} = x, {draw_y_reg} = y")
    print(f"# Returns with {draw_x_reg} incremented by the width of the glyph plus {kern_px}")
    print(f"# Clobbers vF, I{'' if draw_char_reg == width_char_reg else ', ' + width_char_reg}")
    print(f"# Must not be called with {draw_char_reg} < {first_glyph} or {draw_char_reg}  > {last_glyph} !")
    print(f": {draw_func_name}")
    print("  " + draw_char_reg + " += " + str(256-offset))
    print("  i := " + glyphtable_name)
    #for i in range(font_y):

    n_shift = int(log(font_y, 2))
    remainder = font_y - int(pow(n_shift, 2))

    if (n_shift * 2 + remainder + 1) >= font_y:
        n_shift = 0
        remainder = font_y

    if n_shift > 0:
        print(("  i += " + draw_char_reg) * remainder)
        print(("  " + draw_char_reg + " <<= " + draw_char_reg) * n_shift)
        print("  i += " + draw_char_reg)
        print(("  " + draw_char_reg + " >>= " + draw_char_reg) * n_shift)

    else:
        print(("  i += " + draw_char_reg) * remainder)

    print("  sprite " + draw_x_reg + " " + draw_y_reg + " " + str(font_y))

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
            w = len(glyphs[i]) // font_y
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
            w = len(glyphs[i]) // font_y
            s = glyphs[i]

        if not compact_glyphtable:
            glyph_str += "\n" + " " * (len(widthtable_name) + 3) + "# " + str(i) + " \'" + chr(i) + "\'\n" + ": " + "gl" + str(i) + " " + " " * (len(widthtable_name) + 3)

        for i in range(font_y):
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
