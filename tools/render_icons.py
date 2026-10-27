#!/usr/bin/env python3
"""Deterministic Cyber Spectrum icon renderer for Icon-Magic (SnowBoard)."""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "manifests" / "design-tokens.json").read_text())
APPS = json.loads((ROOT / "manifests" / "apps.json").read_text())

SIZE = int(TOKENS["icon_size"])
PAL = TOKENS["palette"]
VARIANT_DEFAULT = "spectrum"


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


OBS = hex_rgb(PAL["obsidian"])
GRA = hex_rgb(PAL["graphite"])
GRN = hex_rgb(PAL["terminal_green"])
BLU = hex_rgb(PAL["electric_blue"])
RED = hex_rgb(PAL["signal_red"])
VIO = hex_rgb(PAL["violet"])
TXT = hex_rgb(PAL["text"])

ACCENTS = {
    "spectrum": [GRN, BLU, VIO, RED],
    "green": [GRN, GRN, GRN, GRN],
    "blue": [BLU, BLU, BLU, BLU],
}


def accent_for(bundle_id: str, variant: str) -> tuple[int, int, int]:
    pool = ACCENTS.get(variant, ACCENTS["spectrum"])
    h = int(hashlib.sha256(bundle_id.encode()).hexdigest()[:8], 16)
    return pool[h % len(pool)]


def try_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_base(draw: ImageDraw.ImageDraw, accent: tuple[int, int, int]) -> None:
    # Square canvas — SnowBoard/mask handles rounding; avoid double-mask.
    draw.rectangle([0, 0, SIZE - 1, SIZE - 1], fill=OBS)
    # Graphite panel inset
    m = 10
    draw.rounded_rectangle([m, m, SIZE - 1 - m, SIZE - 1 - m], radius=22, fill=GRA)
    # Circuit corner marks
    c = accent
    for x0, y0, dx, dy in (
        (18, 18, 1, 1),
        (SIZE - 19, 18, -1, 1),
        (18, SIZE - 19, 1, -1),
        (SIZE - 19, SIZE - 19, -1, -1),
    ):
        draw.line([(x0, y0), (x0 + dx * 14, y0)], fill=c, width=2)
        draw.line([(x0, y0), (x0, y0 + dy * 14)], fill=c, width=2)
    # Top accent bar
    draw.rectangle([m + 8, m + 6, SIZE - m - 8, m + 10], fill=c)


def glyph_phone(d, cx, cy, a):
    d.rounded_rectangle([cx - 18, cy - 28, cx + 18, cy + 28], 6, outline=a, width=3)
    d.ellipse([cx - 4, cy + 18, cx + 4, cy + 26], fill=a)


def glyph_chat(d, cx, cy, a):
    d.rounded_rectangle([cx - 28, cy - 20, cx + 28, cy + 14], 10, outline=a, width=3)
    d.polygon([(cx - 8, cy + 14), (cx - 18, cy + 28), (cx + 4, cy + 14)], fill=a)


def glyph_mail(d, cx, cy, a):
    d.rounded_rectangle([cx - 30, cy - 18, cx + 30, cy + 18], 4, outline=a, width=3)
    d.line([(cx - 28, cy - 16), (cx, cy + 4), (cx + 28, cy - 16)], fill=a, width=3)


def glyph_video(d, cx, cy, a):
    d.rounded_rectangle([cx - 28, cy - 16, cx + 12, cy + 16], 6, outline=a, width=3)
    d.polygon([(cx + 14, cy - 8), (cx + 30, cy - 16), (cx + 30, cy + 16), (cx + 14, cy + 8)], outline=a, width=2)


def glyph_person(d, cx, cy, a):
    d.ellipse([cx - 12, cy - 28, cx + 12, cy - 4], outline=a, width=3)
    d.arc([cx - 24, cy - 2, cx + 24, cy + 36], 200, 340, fill=a, width=3)


def glyph_compass(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=3)
    d.polygon([(cx, cy - 20), (cx + 8, cy + 4), (cx, cy), (cx - 8, cy + 4)], fill=a)


def glyph_camera(d, cx, cy, a):
    d.rounded_rectangle([cx - 30, cy - 18, cx + 30, cy + 22], 6, outline=a, width=3)
    d.rectangle([cx - 10, cy - 26, cx + 10, cy - 18], outline=a, width=2)
    d.ellipse([cx - 12, cy - 8, cx + 12, cy + 16], outline=a, width=3)


def glyph_photo(d, cx, cy, a):
    d.rounded_rectangle([cx - 28, cy - 22, cx + 28, cy + 22], 4, outline=a, width=3)
    d.ellipse([cx - 18, cy - 12, cx - 6, cy], fill=a)
    d.polygon([(cx - 20, cy + 18), (cx - 2, cy - 2), (cx + 12, cy + 12), (cx + 24, cy + 2), (cx + 24, cy + 18)], fill=a)


def glyph_gear(d, cx, cy, a):
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=a, width=3)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=a, width=3)
    for i in range(8):
        ang = i * math.pi / 4
        x1, y1 = cx + 18 * math.cos(ang), cy + 18 * math.sin(ang)
        x2, y2 = cx + 28 * math.cos(ang), cy + 28 * math.sin(ang)
        d.line([(x1, y1), (x2, y2)], fill=a, width=4)


def glyph_clock(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=3)
    d.line([(cx, cy), (cx, cy - 16)], fill=a, width=3)
    d.line([(cx, cy), (cx + 12, cy + 6)], fill=a, width=3)


def glyph_calendar(d, cx, cy, a):
    d.rounded_rectangle([cx - 26, cy - 22, cx + 26, cy + 26], 4, outline=a, width=3)
    d.rectangle([cx - 26, cy - 22, cx + 26, cy - 8], fill=a)
    d.line([(cx - 10, cy - 28), (cx - 10, cy - 16)], fill=a, width=3)
    d.line([(cx + 10, cy - 28), (cx + 10, cy - 16)], fill=a, width=3)


def glyph_map(d, cx, cy, a):
    d.polygon([(cx - 8, cy - 28), (cx + 22, cy - 18), (cx + 22, cy + 22), (cx - 8, cy + 12)], outline=a, width=2)
    d.polygon([(cx - 22, cy - 18), (cx - 8, cy - 28), (cx - 8, cy + 12), (cx - 22, cy + 22)], outline=a, width=2)
    d.ellipse([cx - 6, cy - 10, cx + 6, cy + 2], fill=a)


def glyph_music(d, cx, cy, a):
    d.ellipse([cx - 22, cy + 8, cx - 6, cy + 24], outline=a, width=3)
    d.ellipse([cx + 2, cy + 2, cx + 18, cy + 18], outline=a, width=3)
    d.line([(cx - 6, cy + 16), (cx - 6, cy - 24)], fill=a, width=3)
    d.line([(cx + 18, cy + 10), (cx + 18, cy - 30)], fill=a, width=3)
    d.line([(cx - 6, cy - 24), (cx + 18, cy - 30)], fill=a, width=3)


def glyph_folder(d, cx, cy, a):
    d.polygon([(cx - 30, cy - 8), (cx - 30, cy - 18), (cx - 8, cy - 18), (cx - 2, cy - 10), (cx + 30, cy - 10), (cx + 30, cy + 22), (cx - 30, cy + 22)], outline=a, width=3)


def glyph_store(d, cx, cy, a):
    d.rounded_rectangle([cx - 24, cy - 8, cx + 24, cy + 26], 6, outline=a, width=3)
    d.arc([cx - 16, cy - 28, cx + 16, cy + 4], 200, 340, fill=a, width=3)


def glyph_cloud(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 8, cx - 4, cy + 16], outline=a, width=3)
    d.ellipse([cx - 12, cy - 20, cx + 20, cy + 12], outline=a, width=3)
    d.ellipse([cx + 4, cy - 4, cx + 28, cy + 18], outline=a, width=3)


def glyph_calc(d, cx, cy, a):
    d.rounded_rectangle([cx - 24, cy - 28, cx + 24, cy + 28], 6, outline=a, width=3)
    d.rectangle([cx - 16, cy - 20, cx + 16, cy - 8], outline=a, width=2)
    for i, j in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]:
        x = cx - 14 + i * 16
        y = cy - 2 + j * 12
        d.rectangle([x, y, x + 10, y + 8], outline=a, width=1)


def glyph_wallet(d, cx, cy, a):
    d.rounded_rectangle([cx - 30, cy - 18, cx + 30, cy + 18], 6, outline=a, width=3)
    d.rectangle([cx + 8, cy - 6, cx + 28, cy + 6], outline=a, width=2)
    d.ellipse([cx + 14, cy - 3, cx + 20, cy + 3], fill=a)


def glyph_heart(d, cx, cy, a):
    d.polygon([(cx, cy + 22), (cx - 26, cy - 4), (cx - 14, cy - 20), (cx, cy - 8), (cx + 14, cy - 20), (cx + 26, cy - 4)], outline=a, width=3)


def glyph_news(d, cx, cy, a):
    d.rounded_rectangle([cx - 26, cy - 28, cx + 26, cy + 28], 4, outline=a, width=3)
    for i in range(4):
        y = cy - 16 + i * 12
        d.line([(cx - 16, y), (cx + 16, y)], fill=a, width=2)


def glyph_tv(d, cx, cy, a):
    d.rounded_rectangle([cx - 30, cy - 20, cx + 30, cy + 16], 4, outline=a, width=3)
    d.line([(cx - 10, cy + 16), (cx - 16, cy + 28)], fill=a, width=3)
    d.line([(cx + 10, cy + 16), (cx + 16, cy + 28)], fill=a, width=3)
    d.line([(cx - 18, cy + 28), (cx + 18, cy + 28)], fill=a, width=3)


def glyph_home(d, cx, cy, a):
    d.polygon([(cx, cy - 28), (cx + 28, cy - 4), (cx + 18, cy - 4), (cx + 18, cy + 24), (cx - 18, cy + 24), (cx - 18, cy - 4), (cx - 28, cy - 4)], outline=a, width=3)


def glyph_bolt(d, cx, cy, a):
    d.polygon([(cx + 4, cy - 28), (cx - 12, cy + 2), (cx + 2, cy + 2), (cx - 4, cy + 28), (cx + 16, cy - 4), (cx + 2, cy - 4)], fill=a)


def glyph_tip(d, cx, cy, a):
    d.ellipse([cx - 20, cy - 28, cx + 20, cy + 12], outline=a, width=3)
    d.line([(cx, cy + 14), (cx, cy + 24)], fill=a, width=3)
    d.ellipse([cx - 4, cy + 26, cx + 4, cy + 34], fill=a)


def glyph_mic(d, cx, cy, a):
    d.rounded_rectangle([cx - 10, cy - 28, cx + 10, cy + 4], 8, outline=a, width=3)
    d.arc([cx - 20, cy - 10, cx + 20, cy + 20], 0, 180, fill=a, width=3)
    d.line([(cx, cy + 20), (cx, cy + 30)], fill=a, width=3)


def glyph_podcast(d, cx, cy, a):
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=a)
    d.arc([cx - 20, cy - 20, cx + 20, cy + 20], 200, 340, fill=a, width=3)
    d.arc([cx - 30, cy - 30, cx + 30, cy + 30], 200, 340, fill=a, width=3)


def glyph_book(d, cx, cy, a):
    d.rounded_rectangle([cx - 24, cy - 28, cx + 24, cy + 28], 4, outline=a, width=3)
    d.line([(cx, cy - 26), (cx, cy + 26)], fill=a, width=2)


def glyph_chart(d, cx, cy, a):
    d.line([(cx - 28, cy + 24), (cx + 28, cy + 24)], fill=a, width=2)
    d.line([(cx - 28, cy + 24), (cx - 28, cy - 24)], fill=a, width=2)
    pts = [(cx - 20, cy + 10), (cx - 4, cy - 8), (cx + 10, cy + 4), (cx + 24, cy - 20)]
    d.line(pts, fill=a, width=3)


def glyph_radar(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=2)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=a, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=a)
    d.line([(cx, cy), (cx + 22, cy - 12)], fill=a, width=2)


def glyph_note(d, cx, cy, a):
    d.rounded_rectangle([cx - 22, cy - 28, cx + 22, cy + 28], 4, outline=a, width=3)
    for i in range(3):
        d.line([(cx - 12, cy - 12 + i * 12), (cx + 12, cy - 12 + i * 12)], fill=a, width=2)


def glyph_check(d, cx, cy, a):
    d.rounded_rectangle([cx - 26, cy - 26, cx + 26, cy + 26], 6, outline=a, width=3)
    d.line([(cx - 14, cy), (cx - 4, cy + 12), (cx + 16, cy - 14)], fill=a, width=4)


def glyph_plane(d, cx, cy, a):
    d.polygon([(cx, cy - 28), (cx + 10, cy - 4), (cx + 28, cy + 4), (cx + 8, cy + 6), (cx + 4, cy + 28), (cx, cy + 12), (cx - 4, cy + 28), (cx - 8, cy + 6), (cx - 28, cy + 4), (cx - 10, cy - 4)], outline=a, width=2)


def glyph_watch(d, cx, cy, a):
    d.rounded_rectangle([cx - 18, cy - 28, cx + 18, cy + 28], 8, outline=a, width=3)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=a, width=2)


def glyph_paperplane(d, cx, cy, a):
    d.polygon([(cx - 28, cy + 8), (cx + 28, cy - 20), (cx + 4, cy + 4), (cx - 8, cy + 24)], fill=a)


def glyph_globe(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=3)
    d.ellipse([cx - 12, cy - 28, cx + 12, cy + 28], outline=a, width=2)
    d.line([(cx - 28, cy), (cx + 28, cy)], fill=a, width=2)


def glyph_x(d, cx, cy, a):
    d.line([(cx - 18, cy - 18), (cx + 18, cy + 18)], fill=a, width=5)
    d.line([(cx + 18, cy - 18), (cx - 18, cy + 18)], fill=a, width=5)


def glyph_f(d, cx, cy, a):
    font = try_font(56)
    d.text((cx - 12, cy - 32), "f", fill=a, font=font)


def glyph_ghost(d, cx, cy, a):
    d.ellipse([cx - 20, cy - 28, cx + 20, cy + 4], outline=a, width=3)
    d.polygon([(cx - 20, cy - 4), (cx - 20, cy + 24), (cx - 10, cy + 14), (cx, cy + 24), (cx + 10, cy + 14), (cx + 20, cy + 24), (cx + 20, cy - 4)], outline=a, width=3)


def glyph_ruler(d, cx, cy, a):
    d.rounded_rectangle([cx - 30, cy - 10, cx + 30, cy + 10], 3, outline=a, width=3)
    for i in range(7):
        x = cx - 24 + i * 8
        d.line([(x, cy - 8), (x, cy - 2 if i % 2 else cy + 2)], fill=a, width=2)


def glyph_translate(d, cx, cy, a):
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=a, width=3)
    font = try_font(22)
    d.text((cx - 18, cy - 20), "A", fill=a, font=font)
    d.text((cx + 2, cy), "文", fill=a, font=font)


GLYPHS = {
    "phone": glyph_phone, "chat": glyph_chat, "mail": glyph_mail, "video": glyph_video,
    "person": glyph_person, "compass": glyph_compass, "camera": glyph_camera, "photo": glyph_photo,
    "gear": glyph_gear, "clock": glyph_clock, "calendar": glyph_calendar, "map": glyph_map,
    "music": glyph_music, "folder": glyph_folder, "store": glyph_store, "cloud": glyph_cloud,
    "calc": glyph_calc, "wallet": glyph_wallet, "heart": glyph_heart, "news": glyph_news,
    "tv": glyph_tv, "home": glyph_home, "bolt": glyph_bolt, "tip": glyph_tip,
    "mic": glyph_mic, "podcast": glyph_podcast, "book": glyph_book, "chart": glyph_chart,
    "radar": glyph_radar, "note": glyph_note, "check": glyph_check, "plane": glyph_plane,
    "watch": glyph_watch, "paperplane": glyph_paperplane, "globe": glyph_globe, "x": glyph_x,
    "f": glyph_f, "ghost": glyph_ghost, "ruler": glyph_ruler, "translate": glyph_translate,
}


def render_icon(bundle_id: str, glyph: str, variant: str = VARIANT_DEFAULT) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    accent = accent_for(bundle_id, variant)
    draw_base(draw, accent)
    fn = GLYPHS.get(glyph, glyph_bolt)
    fn(draw, SIZE // 2, SIZE // 2 + 4, accent)
    return img


def write_svg(path: Path, bundle_id: str, glyph: str, variant: str) -> None:
    accent = accent_for(bundle_id, variant)
    ah = "#{:02x}{:02x}{:02x}".format(*accent)
    # Minimal editable SVG companion (glyph simplified as circle + label)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">
  <rect width="180" height="180" fill="{PAL["obsidian"]}"/>
  <rect x="10" y="10" width="160" height="160" rx="22" fill="{PAL["graphite"]}"/>
  <rect x="18" y="16" width="144" height="4" fill="{ah}"/>
  <circle cx="90" cy="96" r="36" fill="none" stroke="{ah}" stroke-width="3"/>
  <text x="90" y="104" text-anchor="middle" fill="{ah}" font-family="monospace" font-size="14">{glyph}</text>
  <text x="90" y="168" text-anchor="middle" fill="{PAL["text"]}" font-family="monospace" font-size="8">{bundle_id}</text>
</svg>
'''
    path.write_text(svg)


def build_theme(variant: str = VARIANT_DEFAULT) -> Path:
    theme_name = TOKENS["snowboard"]["theme_folder"]
    if variant != "spectrum":
        theme_name = theme_name.replace(".theme", f"-{variant.capitalize()}.theme")
    out = ROOT / "theme" / theme_name
    bundles = out / "IconBundles"
    bundles.mkdir(parents=True, exist_ok=True)
    svg_dir = ROOT / "assets" / "svg" / variant
    svg_dir.mkdir(parents=True, exist_ok=True)

    coverage = []
    for app in APPS["icons"]:
        bid = app["bundle_id"]
        glyph = app["glyph"]
        img = render_icon(bid, glyph, variant)
        png_name = f"{bid}-large.png"
        img.save(bundles / png_name, "PNG")
        write_svg(svg_dir / f"{bid}.svg", bid, glyph, variant)
        coverage.append({"bundle_id": bid, "name": app["name"], "file": png_name, "variant": variant})

    # Info.plist
    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PackageName</key>
	<string>{TOKENS["package_name"]}{" [" + variant + "]" if variant != "spectrum" else ""}</string>
	<key>ThemeType</key>
	<string>Icons</string>
</dict>
</plist>
'''
    (out / "Info.plist").write_text(plist)
    return out, coverage


def contact_sheet(paths: list[Path], dest: Path, cols: int = 8) -> None:
    if not paths:
        return
    imgs = [Image.open(p).convert("RGBA") for p in paths[:48]]
    w = h = SIZE
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w, rows * h), OBS + (255,))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h), im)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "PNG")


def main() -> int:
    variants = ["spectrum", "green", "blue"]
    all_cov = []
    for v in variants:
        theme_dir, cov = build_theme(v)
        all_cov.extend(cov)
        pngs = sorted((theme_dir / "IconBundles").glob("*-large.png"))
        contact_sheet(pngs, ROOT / "assets" / "previews" / f"contact-{v}.png")
        print(f"[ok] {v}: {len(cov)} icons -> {theme_dir}")

    report = {
        "theme": TOKENS["theme_name"],
        "icon_count_per_variant": len(APPS["icons"]),
        "variants": variants,
        "total_pngs": len(all_cov),
        "icons": all_cov,
    }
    (ROOT / "manifests" / "coverage-report.json").write_text(json.dumps(report, indent=2))
    print(f"[ok] coverage report: {len(APPS['icons'])} unique apps x {len(variants)} variants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
