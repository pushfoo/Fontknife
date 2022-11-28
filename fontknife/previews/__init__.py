from typing import Optional

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
    fg_color=None,
    force_height: Optional[int] = None,
    force_width: Optional[int] = None
) -> Image:
    # note that multi-line isn't supported by binary fonts!
    # by default, this just looks like one line!
    bbox = pil_font.getbbox(test_string)

    mode_bg_color, mode_fg_color = MODE_COLORS[mode]
    bg_color = bg_color or mode_bg_color
    fg_color = fg_color or mode_fg_color

    image_width = force_width or bbox[2]
    image_height = force_height or bbox[3]

    image = Image.new(mode, (image_width, image_height), bg_color)
    draw = ImageDraw.Draw(image)
    draw.text((0,0), test_string, font=pil_font, color=fg_color)

    return image
