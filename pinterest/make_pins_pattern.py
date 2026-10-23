#!/usr/bin/env python3
"""Pattern promo pins for the Everyday Ribbed Beanie (2026-10-23).

Full-bleed realistic photo, FREE PATTERN pill, white title card, brand footer.
Usage: python3 make_pins_pattern.py
"""
from PIL import Image, ImageDraw
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_pins import font, wrap

OUT = Path(__file__).resolve().parent / "pins-pattern"
SRC = Path(__file__).resolve().parent.parent / "assets" / "pattern-beanie"
W, H = 1000, 1500

WHITE = (255, 255, 255)
TEAL = (7, 59, 58)
CORAL = (240, 82, 114)
MUTED = (120, 100, 108)


def cover(img, w, h):
    scale = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1), Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def make_pin(photo, headline, subline, out_name):
    img = cover(Image.open(SRC / photo).convert("RGB"), W, H)
    d = ImageDraw.Draw(img, "RGBA")
    # gentle top/bottom shades for text legibility
    for y in range(300):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(80 * (1 - y / 300))))
    for y in range(H - 560, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(110 * (y - (H - 560)) / 560)))

    # FREE PATTERN pill
    f_pill = font("Fredoka-Bold.ttf", 44)
    pt = "FREE PATTERN"
    pw_ = d.textlength(pt, font=f_pill) + 80
    d.rounded_rectangle([48, 48, 48 + pw_, 48 + 88], radius=44, fill=CORAL)
    d.text((48 + 40, 48 + 18), pt, font=f_pill, fill=WHITE)

    # bottom title card
    f_head = font("Fredoka-Bold.ttf", 84)
    lines = wrap(d, headline, f_head, W - 220)
    while len(lines) > 2:
        f_head = font("Fredoka-Bold.ttf", f_head.size - 6)
        lines = wrap(d, headline, f_head, W - 220)
    f_sub = font("Quicksand-Bold.ttf", 36)
    card_h = 40 + len(lines) * (f_head.size + 14) + 60 + 90
    card = [48, H - 48 - card_h, W - 48, H - 48]
    d.rounded_rectangle(card, radius=36, fill=(255, 255, 255, 235))
    y = card[1] + 36
    for line in lines:
        d.text(((W - d.textlength(line, font=f_head)) / 2, y), line, font=f_head, fill=TEAL)
        y += f_head.size + 14
    d.text(((W - d.textlength(subline, font=f_sub)) / 2, y + 8), subline, font=f_sub, fill=MUTED)
    # footer url
    f_url = font("Fredoka-Bold.ttf", 34)
    ut = "HowMuchYarn.com"
    uw_ = d.textlength(ut, font=f_url) + 64
    d.rounded_rectangle([(W - uw_) / 2, H - 40 - 64, (W + uw_) / 2, H - 40],
                        radius=32, fill=CORAL)
    d.text(((W - d.textlength(ut, font=f_url)) / 2, H - 40 - 50), ut, font=f_url, fill=WHITE)

    OUT.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT / out_name, "JPEG", quality=90, optimize=True)
    print("wrote", OUT / out_name)


if __name__ == "__main__":
    make_pin("beanie-hero.webp", "FREE Crochet Beanie Pattern",
             "4 sizes · beginner friendly · exact yardage", "pattern-beanie-1.jpg")
    make_pin("beanie-flatlay.webp", "Ribbed Beanie, Zero Shaping",
             "free pattern + yardage chart inside", "pattern-beanie-2.jpg")
    make_pin("beanie-detail.webp", "The Everyday Ribbed Beanie",
             "free beginner crochet pattern", "pattern-beanie-3.jpg")
