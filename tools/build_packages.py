#!/usr/bin/env python3
"""Build rootful and rootless .deb packages for Icon-Magic themes.

Works on Windows/macOS/Linux. Uses system `ar` when available; otherwise
writes a valid ar archive in pure Python (no GNU binutils required).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "manifests" / "design-tokens.json").read_text(encoding="utf-8"))
VERSION = TOKENS["version"]
PKG_ID = TOKENS["package_id"]
DEPENDS = TOKENS["snowboard"]["depends"]


def slug(s: str) -> str:
    s = s.replace(".theme", "")
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()


def write_control(path: Path, pkg: str, name: str, arch: str, desc: str) -> None:
    path.write_text(
        f"Package: {pkg}\n"
        f"Name: {name}\n"
        f"Version: {VERSION}\n"
        f"Architecture: {arch}\n"
        f"Description: {desc}\n"
        f"Maintainer: Icon-Magic <iconmagic@local>\n"
        f"Author: Icon-Magic / Kwar Nu\n"
        f"Section: Themes\n"
        f"Depends: {DEPENDS}\n",
        encoding="utf-8",
    )


def write_ar_archive(deb_path: Path, members: list[tuple[str, bytes]]) -> None:
    """System V ar archive (.deb compatible) without GNU ar."""
    parts: list[bytes] = [b"!<arch>\n"]
    for name, data in members:
        n = name[:16]
        header = f"{n:<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(data):<10}`\n".encode("ascii")
        parts.append(header)
        parts.append(data)
        if len(data) % 2 == 1:
            parts.append(b"\n")
    deb_path.write_bytes(b"".join(parts))


def build_deb(
    theme_dir: Path,
    install_prefix: str,
    arch: str,
    pkg: str,
    name: str,
    out_dir: Path,
) -> Path:
    work = Path(tempfile.mkdtemp(prefix="iconmagic-"))
    try:
        data_root = work / "data"
        dest = data_root / install_prefix / theme_dir.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(theme_dir, dest)

        control_file = work / "control"
        write_control(
            control_file,
            pkg,
            name,
            arch,
            "Cyber Spectrum icon theme for SnowBoard. Original free assets.",
        )

        data_tar = work / "data.tar.gz"
        control_tar = work / "control.tar.gz"
        with tarfile.open(data_tar, "w:gz") as tar:
            tar.add(data_root, arcname=".")
        with tarfile.open(control_tar, "w:gz") as tar:
            tar.add(control_file, arcname="control")

        out_dir.mkdir(parents=True, exist_ok=True)
        deb_name = f"{pkg}_{VERSION}_{arch}.deb"
        deb_path = out_dir / deb_name
        if deb_path.exists():
            deb_path.unlink()

        members = [
            ("debian-binary", b"2.0\n"),
            ("control.tar.gz", control_tar.read_bytes()),
            ("data.tar.gz", data_tar.read_bytes()),
        ]

        if shutil.which("ar"):
            deb_bin = work / "debian-binary"
            deb_bin.write_bytes(b"2.0\n")
            subprocess.check_call(
                ["ar", "r", str(deb_path), str(deb_bin), str(control_tar), str(data_tar)]
            )
        else:
            print("[info] GNU ar not found — using pure-Python .deb writer")
            write_ar_archive(deb_path, members)

        sha = hashlib.sha256(deb_path.read_bytes()).hexdigest()
        (out_dir / f"{deb_name}.sha256").write_text(f"{sha}  {deb_name}\n", encoding="utf-8")
        print(f"[ok] {deb_path.name} ({deb_path.stat().st_size} bytes, sha256={sha[:12]}…)")
        return deb_path
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    out = ROOT / "packaging" / "dist"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    themes = sorted((ROOT / "theme").glob("*.theme"))
    if not themes:
        raise SystemExit("No themes found — run: python3 tools/render_icons.py")

    for theme in themes:
        s = slug(theme.name)
        label = theme.name.replace(".theme", "")
        build_deb(
            theme,
            "Library/Themes",
            "iphoneos-arm",
            f"{PKG_ID}.{s}",
            f"Icon-Magic {label}",
            out,
        )
        build_deb(
            theme,
            "var/jb/Library/Themes",
            "iphoneos-arm64",
            f"{PKG_ID}.{s}.rootless",
            f"Icon-Magic {label} (rootless)",
            out,
        )

    print(f"\nDone. Packages in: {out}")
    for p in sorted(out.glob("*.deb")):
        print(f"  {p.name}  ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
