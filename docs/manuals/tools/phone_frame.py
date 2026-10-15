"""Frame app screenshots as a phone and add numbered stickers (manuals).

    uv run python docs/manuals/tools/phone_frame.py \
        docs/manuals/images/reception-produits/frames.json [out.png ...]

The spec (JSON) lists, per output image: the raw screenshot (``raw/``, a
phone-sized capture of the app) and its stickers: a target box in screenshot
pixels, a short label and the side (``left`` / ``right``) of its bubble.
Next.js's development badge (bottom-left "N") is cropped away with the
bottom strip of the screen unless ``hide_dev_badge`` is false; ``crop_to``
(a y in screenshot pixels) sets that bottom edge by hand. Only Pillow is needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TEAL = (27, 84, 80)
WHITE = (255, 255, 255)
BODY = (24, 26, 29)
SCALE = 2  # screenshots are 1x device pixels
BEZEL = 26
RADIUS = 92
MIN_MARGIN_X = 60
MARGIN_Y = 70
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def _is_badge(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    # Next.js's badge: red with an issue, else near black.
    return (r > 170 and g < 110 and b < 110) or max(rgb) < 40


def hide_dev_badge(shot: Image.Image) -> Image.Image:
    """Remove Next.js's dev badge (a ~36 px disc near the bottom-left corner,
    red or black, with a white rim) by cropping the bottom strip it sits in.
    Better: capture with ``devIndicators: false`` in next.config."""
    shot = shot.convert("RGB")
    w, h = shot.size
    px = shot.load()
    # Badge-coloured pixels near the bottom-left corner, ignoring rows that
    # are a long line (a button or card border crossing the badge).
    pts = []
    for y in range(h - 70, h - 8):
        row = [x for x in range(12, 70) if _is_badge(px[x, y])]
        if 0 < len(row) < 45:
            pts += [(x, y) for x in row]
    if not pts:
        return shot
    ys = sorted(p[1] for p in pts)
    cy = ys[len(ys) // 2]
    # What it covers cannot be recovered and a painted patch always shows:
    # crop the bottom strip it sits in instead (the screen gets shorter).
    return shot.crop((0, 0, w, max(0, cy - 21)))  # disc ~18 px + white rim


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return mask


def bubble(
    draw: ImageDraw.ImageDraw, number: int, text: str, x: int, y: int, side: str
) -> tuple[int, int]:
    """Label bubble with its number; returns the point the leader line meets."""
    f = font(30)
    fn = font(30)
    tw = draw.textlength(text, font=f)
    pad, dot = 18, 44
    w, h = int(tw + dot + pad * 3), 64
    left = x - w if side == "left" else x
    top = y - h // 2
    draw.rounded_rectangle((left, top, left + w, top + h), 32, fill=WHITE, outline=TEAL, width=4)
    cx, cy = left + pad + dot // 2, y
    draw.ellipse((cx - dot // 2, cy - dot // 2, cx + dot // 2, cy + dot // 2), fill=TEAL)
    draw.text((cx, cy), str(number), font=fn, fill=WHITE, anchor="mm")
    draw.text((left + pad * 2 + dot, cy), text, font=f, fill=(20, 30, 30), anchor="lm")
    return (left + w, y) if side == "left" else (left, y)


def render(spec: dict, base: Path) -> None:
    shot = Image.open(base / spec["raw"])
    if "crop_to" in spec:
        # Explicit bottom edge (badge undetectable, e.g. black on black).
        shot = shot.crop((0, 0, shot.width, spec["crop_to"]))
    elif spec.get("hide_dev_badge", True):
        shot = hide_dev_badge(shot)
    shot = shot.convert("RGB")
    sw, sh = shot.size
    screen = shot.resize((sw * SCALE, sh * SCALE), Image.LANCZOS)
    pw, ph = screen.width + 2 * BEZEL, screen.height + 2 * BEZEL
    # Each side as wide as its widest label bubble.
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    need = {"left": MIN_MARGIN_X, "right": MIN_MARGIN_X}
    for s in spec.get("stickers", []):
        side = s.get("side", "right")
        width = measure.textlength(s["label"], font=font(30)) + 44 + 18 * 3 + 24 + 40
        need[side] = max(need[side], int(width))
    canvas = Image.new("RGB", (pw + need["left"] + need["right"], ph + 2 * MARGIN_Y), WHITE)
    draw = ImageDraw.Draw(canvas)
    ox, oy = need["left"], MARGIN_Y

    # Phone: body, side buttons, screen, camera pill.
    draw.rounded_rectangle((ox - 6, oy + 260, ox + 4, oy + 360), 4, fill=BODY)
    draw.rounded_rectangle((ox - 6, oy + 390, ox + 4, oy + 490), 4, fill=BODY)
    draw.rounded_rectangle((ox + pw - 4, oy + 320, ox + pw + 6, oy + 460), 4, fill=BODY)
    draw.rounded_rectangle((ox, oy, ox + pw, oy + ph), RADIUS, fill=BODY)
    canvas.paste(screen, (ox + BEZEL, oy + BEZEL), rounded_mask(screen.size, RADIUS - BEZEL))
    pill = 150
    draw.rounded_rectangle(
        (ox + pw // 2 - pill // 2, oy + BEZEL + 14, ox + pw // 2 + pill // 2, oy + BEZEL + 50),
        18,
        fill=BODY,
    )

    # Stickers: ring around the target, leader line, numbered bubble outside.
    sx, sy = ox + BEZEL, oy + BEZEL
    for i, s in enumerate(spec.get("stickers", []), start=1):
        x0, y0, x1, y1 = s["box"]
        box = (sx + x0 * SCALE - 8, sy + y0 * SCALE - 8, sx + x1 * SCALE + 8, sy + y1 * SCALE + 8)
        draw.rounded_rectangle(box, 18, outline=TEAL, width=7)
        side = s.get("side", "right")
        by = int((box[1] + box[3]) / 2) if "label_y" not in s else sy + s["label_y"] * SCALE
        bx = ox - 24 if side == "left" else ox + pw + 24
        end = bubble(draw, i, s["label"], bx, by, side)
        start = (
            (box[0], (box[1] + box[3]) // 2) if side == "left" else (box[2], (box[1] + box[3]) // 2)
        )
        draw.line((start, (bx, by), end), fill=TEAL, width=5)
        draw.ellipse((start[0] - 9, start[1] - 9, start[0] + 9, start[1] + 9), fill=TEAL)

    out = canvas.resize((canvas.width // 2, canvas.height // 2), Image.LANCZOS)
    out.save(base / spec["out"], optimize=True)
    print("wrote", spec["out"], out.size)


def main() -> None:
    path = Path(sys.argv[1])
    base = path.parent
    for spec in json.loads(path.read_text())["images"]:
        if len(sys.argv) > 2 and spec["out"] not in sys.argv[2:]:
            continue
        render(spec, base)


if __name__ == "__main__":
    main()
