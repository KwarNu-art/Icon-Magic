#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
APPS = json.loads((ROOT / "manifests" / "apps.json").read_text())
TOKENS = json.loads((ROOT / "manifests" / "design-tokens.json").read_text())

def test_manifest_unique():
    ids = [a["bundle_id"] for a in APPS["icons"]]
    assert len(ids) == len(set(ids)), "duplicate bundle ids"
    assert len(ids) >= 40, f"need >=40 icons, got {len(ids)}"
    for bid in ids:
        assert ".." not in bid and "/" not in bid and bid.count(".") >= 1

def test_pngs_exist_and_valid():
    theme = ROOT / "theme" / TOKENS["snowboard"]["theme_folder"]
    bundles = theme / "IconBundles"
    assert bundles.is_dir(), "theme not built — run render_icons.py"
    for app in APPS["icons"]:
        p = bundles / f"{app['bundle_id']}-large.png"
        assert p.is_file(), f"missing {p.name}"
        im = Image.open(p)
        assert im.size[0] > 0 and im.size[1] > 0
        assert im.mode in ("RGBA", "RGB", "P")
        # non-empty pixels
        extrema = im.convert("RGBA").getextrema()
        assert any(e[1] > 0 for e in extrema)

def test_info_plist():
    theme = ROOT / "theme" / TOKENS["snowboard"]["theme_folder"]
    plist = (theme / "Info.plist").read_text()
    assert "PackageName" in plist
    assert "ThemeType" in plist
    assert "Icons" in plist

def test_path_safety():
    for app in APPS["icons"]:
        bid = app["bundle_id"]
        assert not bid.startswith("/")
        assert ".." not in bid

def main():
    tests = [test_manifest_unique, test_pngs_exist_and_valid, test_info_plist, test_path_safety]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
