#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimasi panel webtoon: PNG/JPEG -> WebP lossy (kualitas 80) atau JPEG q=82.

Usage:
  python compact_panels.py <folder> [--format webp|jpeg] [--quality 80] [--max-width 1024]
Dengan --in-place, file sumber dihapus setelah konversi. Default: tulis .webp di samping file, sumber dibiarkan.
"""
import argparse
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow belum terpasang. Jalankan: pip install pillow")


def optimize(folder: Path, fmt: str, quality: int, max_width: int, in_place: bool) -> int:
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    total_before = 0
    total_after = 0
    converted = 0
    os.makedirs(folder, exist_ok=True)
    for f in sorted(folder.iterdir()):
        if not f.is_file() or f.suffix.lower() not in exts:
            continue
        if f.suffix.lower() == f".{fmt}":
            continue
        size_before = f.stat().st_size
        try:
            with Image.open(f) as im:
                im = im.convert("RGB")
                if im.width > max_width:
                    h = round(im.height * max_width / im.width)
                    im = im.resize((max_width, h), Image.LANCZOS)
                out = f.with_suffix(f".{fmt}")
                if fmt == "webp":
                    im.save(out, "WEBP", quality=quality, method=6)
                else:
                    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
        except Exception as e:
            print(f"  SKIP {f.name}: {e}")
            continue
        size_after = out.stat().st_size
        pct = 100 * (1 - size_after / size_before) if size_before else 0
        print(f"  OK  {f.name} {size_before/1024:.0f}KB -> {size_after/1024:.0f}KB (-{pct:.0f}%)")
        total_before += size_before
        total_after += size_after
        converted += 1
        if in_place:
            f.unlink()
    if converted:
        print(f"Total: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB "
              f"(-{100*(1-total_after/total_before):.0f}%) | {converted} file")
    else:
        print("Tidak ada file yang perlu dikonversi.")
    return converted


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--format", choices=["webp", "jpeg"], default="webp")
    ap.add_argument("--quality", type=int, default=80)
    ap.add_argument("--max-width", type=int, default=1024)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()
    optimize(args.folder, args.format, args.quality, args.max_width, args.in_place)