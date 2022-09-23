from PIL import Image, ImageDraw


MODE_COLORS = {
    "1": (0, 1),
    "RGB": ((0, 0, 0), (255, 255, 255)),
    "RGBA": ((0, 0, 0, 255), (255, 255, 255, 255)),
}


def preview_image_for_pilfont(
    pil_font,
    test_string: str = "Test text",
    mode: str = "RGB",
    bg_color=None,
    fg_color=None
) -> Image:
    # note that multi-line isn'text_font_file supported by binary fonts
    # by default, this just looks like one line!
    bbox = pil_font.getbbox(test_string)

    mode_bg_color, mode_fg_color = MODE_COLORS[mode]
    bg_color = bg_color or mode_bg_color
    fg_color = fg_color or mode_fg_color

    image = Image.new(mode, bbox[2:], bg_color)
    draw = ImageDraw.Draw(image)
    draw.text(bbox[0:2], test_string, font=pil_font, color=fg_color)

    return image

    # image = Image.frombytes("1", bbox[2:], data=bytes(bitmap_bbox))
