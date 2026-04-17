from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SIZE = 512
PRIMARY = (123, 63, 228)
ACCENT = (169, 112, 255)
WHITE = (245, 242, 255)
RED = (255, 74, 96)

OUT_DIR = Path(__file__).resolve().parent


# --------------------------
# Core drawing utilities
# --------------------------

def lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def mix(c1, c2, t: float):
    return tuple(lerp(c1[i], c2[i], t) for i in range(3))


def gradient_rect(size: int, top, bottom) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        row = mix(top, bottom, t)
        for x in range(size):
            px[x, y] = (*row, 255)
    return img


def base_tile() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bbox = (66, 66, 446, 446)
    radius = 96

    # Outer glow
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle(bbox, radius=radius, fill=(*ACCENT, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    img.alpha_composite(glow)

    # Glossy gradient card
    card_mask = Image.new("L", (SIZE, SIZE), 0)
    mdraw = ImageDraw.Draw(card_mask)
    mdraw.rounded_rectangle(bbox, radius=radius, fill=255)

    card = gradient_rect(SIZE, mix(PRIMARY, (30, 18, 56), 0.22), mix(ACCENT, (16, 8, 34), 0.34))
    img.alpha_composite(Image.composite(card, Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0)), card_mask))

    # Inner top highlight
    h = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(h)
    hdraw.rounded_rectangle((86, 84, 426, 240), radius=72, fill=(255, 255, 255, 26))
    h = h.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(h)

    # Crisp edge
    edge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rounded_rectangle(bbox, radius=radius, outline=(255, 255, 255, 88), width=3)
    img.alpha_composite(edge)

    return img


def add_icon_glow(icon: Image.Image, color=(180, 132, 255), blur=10, alpha=170) -> Image.Image:
    mask = icon.split()[-1]
    glow = Image.new("RGBA", (SIZE, SIZE), (*color, alpha))
    glow.putalpha(mask)
    return glow.filter(ImageFilter.GaussianBlur(blur))


def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_note(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color, w: int):
    # Single eighth note
    stem_h = int(120 * scale)
    stem_x = x
    draw.line([(stem_x, y), (stem_x, y - stem_h)], fill=color, width=w)
    head_r = int(26 * scale)
    draw.ellipse((stem_x - head_r - int(26 * scale), y - head_r, stem_x - int(26 * scale) + head_r, y + head_r), fill=color)
    flag_w = int(56 * scale)
    draw.polygon(
        [
            (stem_x, y - stem_h),
            (stem_x + flag_w, y - stem_h + int(16 * scale)),
            (stem_x + flag_w, y - stem_h + int(44 * scale)),
            (stem_x, y - stem_h + int(30 * scale)),
        ],
        fill=color,
    )


def draw_speaker(draw: ImageDraw.ImageDraw, color, w: int):
    body = [(170, 286), (224, 286), (274, 326), (274, 186), (224, 226), (170, 226)]
    draw.polygon(body, fill=color)


def draw_wave(draw, center, r, start, end, color, width):
    x, y = center
    draw.arc((x - r, y - r, x + r, y + r), start=start, end=end, fill=color, width=width)


# --------------------------
# Icon renderers
# --------------------------

def icon_play(draw, c, w):
    draw.polygon([(208, 176), (208, 336), (336, 256)], fill=c)


def icon_pause(draw, c, w):
    rounded_rect(draw, (186, 172, 238, 340), 18, c)
    rounded_rect(draw, (274, 172, 326, 340), 18, c)


def icon_stop(draw, c, w):
    rounded_rect(draw, (180, 180, 332, 332), 26, c)


def icon_skip(draw, c, w):
    draw.polygon([(152, 176), (152, 336), (242, 256)], fill=c)
    draw.polygon([(238, 176), (238, 336), (328, 256)], fill=c)
    rounded_rect(draw, (336, 184, 360, 328), 10, c)


def icon_prev(draw, c, w):
    draw.polygon([(360, 176), (360, 336), (270, 256)], fill=c)
    draw.polygon([(274, 176), (274, 336), (184, 256)], fill=c)
    rounded_rect(draw, (152, 184, 176, 328), 10, c)


def icon_vol_up(draw, c, w):
    draw_speaker(draw, c, w)
    draw_wave(draw, (282, 256), 44, -45, 45, c, w)
    draw_wave(draw, (282, 256), 74, -45, 45, c, w)


def icon_vol_down(draw, c, w):
    draw_speaker(draw, c, w)
    draw_wave(draw, (282, 256), 44, -45, 45, c, w)


def icon_mute(draw, c, w):
    draw_speaker(draw, c, w)
    draw.line([(300, 212), (356, 300)], fill=c, width=w)
    draw.line([(356, 212), (300, 300)], fill=c, width=w)


def icon_vol_max(draw, c, w):
    draw_speaker(draw, c, w)
    for r in (42, 70, 98):
        draw_wave(draw, (282, 256), r, -45, 45, c, w)


def loop_base(draw, c, w):
    draw.arc((150, 178, 346, 334), start=32, end=190, fill=c, width=w)
    draw.arc((166, 178, 362, 334), start=212, end=358, fill=c, width=w)
    draw.polygon([(336, 196), (378, 192), (352, 228)], fill=c)
    draw.polygon([(176, 316), (134, 320), (160, 284)], fill=c)


def icon_loop_off(draw, c, w):
    loop_base(draw, c, w)
    draw.line([(320, 178), (372, 230)], fill=c, width=w)
    draw.line([(372, 178), (320, 230)], fill=c, width=w)


def icon_loop_one(draw, c, w):
    loop_base(draw, c, w)
    rounded_rect(draw, (236, 220, 276, 298), 12, c)
    draw.polygon([(220, 230), (236, 220), (236, 242)], fill=c)


def icon_loop_all(draw, c, w):
    loop_base(draw, c, w)


def icon_autoplay(draw, c, w):
    loop_base(draw, c, w)
    # Headphone accent
    draw.arc((210, 212, 302, 304), start=200, end=-20, fill=c, width=w)
    rounded_rect(draw, (206, 250, 226, 296), 8, c)
    rounded_rect(draw, (286, 250, 306, 296), 8, c)


def icon_shuffle(draw, c, w):
    draw.line([(150, 184), (236, 256), (150, 328)], fill=c, width=w)
    draw.line([(236, 256), (342, 256)], fill=c, width=w)
    draw.polygon([(342, 256), (306, 230), (306, 282)], fill=c)

    draw.line([(150, 328), (236, 256), (150, 184)], fill=c, width=w)
    draw.line([(236, 184), (306, 184)], fill=c, width=w)
    draw.polygon([(342, 184), (306, 158), (306, 210)], fill=c)


def icon_queue(draw, c, w):
    for y in (196, 242, 288):
        draw.line([(148, y), (294, y)], fill=c, width=w)
    draw_note(draw, 344, 300, 0.56, c, w)


def icon_add(draw, c, w):
    draw_note(draw, 292, 306, 0.72, c, w)
    draw.line([(160, 256), (236, 256)], fill=c, width=w)
    draw.line([(198, 218), (198, 294)], fill=c, width=w)


def icon_remove(draw, c, w):
    draw_note(draw, 292, 306, 0.72, c, w)
    draw.line([(154, 214), (238, 298)], fill=c, width=w)
    draw.line([(238, 214), (154, 298)], fill=c, width=w)


def icon_clear(draw, c, w):
    draw.line([(190, 188), (322, 188)], fill=c, width=w)
    rounded_rect(draw, (204, 204, 308, 338), 14, None)
    draw.polygon([(204, 204), (308, 204), (294, 338), (218, 338)], fill=c)
    rounded_rect(draw, (230, 166, 282, 188), 8, c)
    for x in (236, 256, 276):
        draw.line([(x, 226), (x, 314)], fill=(60, 24, 112, 160), width=max(4, w // 4))


def icon_move(draw, c, w):
    draw.line([(256, 186), (256, 326)], fill=c, width=w)
    draw.polygon([(256, 156), (222, 198), (290, 198)], fill=c)
    draw.polygon([(256, 356), (222, 314), (290, 314)], fill=c)


def icon_search(draw, c, w):
    draw.ellipse((166, 168, 292, 294), outline=c, width=w)
    draw.line([(278, 282), (350, 354)], fill=c, width=w)


def icon_suggest(draw, c, w):
    # bulb
    draw.ellipse((164, 162, 284, 284), outline=c, width=w)
    rounded_rect(draw, (204, 280, 244, 320), 10, c)
    draw.line([(194, 334), (254, 334)], fill=c, width=w)
    draw_note(draw, 336, 306, 0.56, c, w)


def icon_loading(draw, c, w):
    for i in range(10):
        a0 = i * 32
        a1 = a0 + 20
        alpha = int(60 + i * 18)
        col = (c[0], c[1], c[2], alpha)
        draw.arc((164, 164, 348, 348), start=a0, end=a1, fill=col, width=w)


def icon_success(draw, c, w):
    draw.line([(168, 262), (232, 322), (344, 198)], fill=c, width=w)


def icon_error(draw, c, w):
    draw.polygon([(256, 154), (360, 338), (152, 338)], fill=(255, 186, 110, 240))
    draw.line([(256, 214), (256, 286)], fill=(86, 36, 0, 255), width=w)
    draw.ellipse((242, 300, 270, 328), fill=(86, 36, 0, 255))


def icon_music(draw, c, w):
    draw_note(draw, 286, 324, 0.92, c, w)


def icon_artist(draw, c, w):
    draw.ellipse((168, 176, 248, 256), outline=c, width=w)
    draw.arc((150, 238, 266, 346), start=205, end=-25, fill=c, width=w)
    # mic
    draw.ellipse((280, 196, 352, 268), outline=c, width=w)
    draw.line([(316, 268), (316, 320)], fill=c, width=w)
    draw.line([(288, 322), (344, 322)], fill=c, width=w)


def icon_album(draw, c, w):
    draw.ellipse((146, 146, 366, 366), outline=c, width=w)
    draw.ellipse((228, 228, 284, 284), fill=c)
    draw.arc((178, 178, 334, 334), start=24, end=72, fill=c, width=max(6, w // 3))


def icon_time(draw, c, w):
    draw.ellipse((152, 152, 360, 360), outline=c, width=w)
    draw.line([(256, 256), (256, 202)], fill=c, width=w)
    draw.line([(256, 256), (308, 284)], fill=c, width=w)


def icon_live(draw, c, w):
    draw.ellipse((198, 198, 314, 314), fill=RED)
    draw.ellipse((198, 198, 314, 314), outline=(255, 208, 216, 240), width=6)


def icon_fav(draw, c, w):
    draw.polygon([(256, 344), (158, 248), (158, 194), (196, 166), (256, 206), (316, 166), (354, 194), (354, 248)], fill=c)


def icon_library(draw, c, w):
    rounded_rect(draw, (162, 176, 214, 336), 10, c)
    rounded_rect(draw, (222, 160, 278, 336), 10, c)
    rounded_rect(draw, (286, 188, 346, 336), 10, c)


def icon_download(draw, c, w):
    draw_note(draw, 318, 322, 0.6, c, w)
    draw.line([(190, 170), (190, 286)], fill=c, width=w)
    draw.polygon([(190, 318), (154, 272), (226, 272)], fill=c)
    draw.line([(146, 334), (234, 334)], fill=c, width=w)


def icon_radio(draw, c, w):
    rounded_rect(draw, (150, 194, 362, 332), 24, (0, 0, 0, 0))
    draw.rounded_rectangle((150, 194, 362, 332), radius=24, outline=c, width=w)
    draw.line([(188, 186), (230, 146)], fill=c, width=w)
    draw.ellipse((196, 238, 272, 314), outline=c, width=w)
    draw.line([(298, 244), (338, 244)], fill=c, width=w)
    draw.line([(298, 274), (338, 274)], fill=c, width=w)


def icon_eq(draw, c, w):
    for x, y in ((188, 220), (256, 270), (324, 206)):
        draw.line([(x, 170), (x, 344)], fill=c, width=max(10, w // 2))
        draw.ellipse((x - 22, y - 22, x + 22, y + 22), fill=c)


RENDERERS = {
    "play": icon_play,
    "pause": icon_pause,
    "stop": icon_stop,
    "skip": icon_skip,
    "prev": icon_prev,
    "vol_up": icon_vol_up,
    "vol_down": icon_vol_down,
    "mute": icon_mute,
    "vol_max": icon_vol_max,
    "loop_off": icon_loop_off,
    "loop_one": icon_loop_one,
    "loop_all": icon_loop_all,
    "autoplay": icon_autoplay,
    "shuffle": icon_shuffle,
    "queue": icon_queue,
    "add": icon_add,
    "remove": icon_remove,
    "clear": icon_clear,
    "move": icon_move,
    "search": icon_search,
    "suggest": icon_suggest,
    "loading": icon_loading,
    "success": icon_success,
    "error": icon_error,
    "music": icon_music,
    "artist": icon_artist,
    "album": icon_album,
    "time": icon_time,
    "live": icon_live,
    "fav": icon_fav,
    "library": icon_library,
    "download": icon_download,
    "radio": icon_radio,
    "eq": icon_eq,
}


def render_one(name: str):
    base = base_tile()

    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon, "RGBA")

    fg = WHITE
    stroke = 24

    RENDERERS[name](draw, fg, stroke)

    # Subtle icon glow
    base.alpha_composite(add_icon_glow(icon, color=ACCENT, blur=11, alpha=156))
    base.alpha_composite(icon)

    # Slight center sheen
    sheen = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.ellipse((146, 120, 366, 318), fill=(255, 255, 255, 18))
    sheen = sheen.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(sheen)

    out = OUT_DIR / f"{name}.png"
    base.save(out, "PNG")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in RENDERERS:
        render_one(name)
    print(f"Generated {len(RENDERERS)} icons in {OUT_DIR}")


if __name__ == "__main__":
    main()
