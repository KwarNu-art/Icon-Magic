#!/usr/bin/env python3
"""Offline fallback icon generator from user-supplied app list (JSON/CSV)."""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

# Reuse renderer
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_icons import render_icon, SIZE  # type: ignore

def load_apps(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, dict) and "icons" in data:
            return data["icons"]
        if isinstance(data, list):
            return data
        raise SystemExit("JSON must be list or {icons: [...]}")
    # CSV: bundle_id,name,category,glyph
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "bundle_id": row["bundle_id"].strip(),
                "name": row.get("name", row["bundle_id"]).strip(),
                "category": row.get("category", "other").strip(),
                "glyph": row.get("glyph", "bolt").strip() or "bolt",
            })
    return rows

def main():
    ap = argparse.ArgumentParser(description="Generate fallback SnowBoard icons from a local app list")
    ap.add_argument("input", type=Path, help="JSON or CSV of apps")
    ap.add_argument("-o", "--out", type=Path, default=Path("generated-IconBundles"))
    ap.add_argument("--variant", default="spectrum", choices=["spectrum", "green", "blue"])
    args = ap.parse_args()
    apps = load_apps(args.input)
    args.out.mkdir(parents=True, exist_ok=True)
    n = 0
    for app in apps:
        bid = app["bundle_id"]
        if not bid or ".." in bid or "/" in bid:
            print(f"[skip] unsafe id: {bid!r}")
            continue
        glyph = app.get("glyph") or "bolt"
        img = render_icon(bid, glyph, args.variant)
        dest = args.out / f"{bid}-large.png"
        img.save(dest, "PNG")
        n += 1
        print(f"[ok] {dest.name}")
    print(f"Generated {n} icons into {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
