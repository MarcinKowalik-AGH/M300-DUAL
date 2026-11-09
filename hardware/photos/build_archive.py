#!/usr/bin/env python3
"""Build one validated 48-image M300 Dual photo archive (PNG, no metadata).

Requires the 27 originals in hardware/photos/incoming/*.jpg|*.jpeg|*.png.
Does not overwrite or falsely mark incomplete archives as complete.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import hashlib
import io
import json
import math
import re
import zipfile

BASE = Path(__file__).resolve().parent
INITIAL = BASE / "M300_Dual_Photos_21_PNG_GitHub_compact.zip"
INCOMING = BASE / "incoming"
DEST = BASE / "M300_Dual_Photos_48_PNG.zip"
SHEET = BASE / "contact_sheet_48.png"
NEW = {8997, 8998, 8999, *range(9001, 9025)}
OLD = set(range(8956, 8977))
MAX_SIZE = (950, 950)

def clean_png(source: Path) -> bytes:
    with Image.open(source) as opened:
        opened = ImageOps.exif_transpose(opened)
        img = opened.convert("RGB")
        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        fresh = Image.new("RGB", img.size)
        fresh.paste(img)
        # No exif=, pnginfo=, ICC profile or ancillary metadata copied.
        buf = io.BytesIO()
        fresh.quantize(colors=128, method=Image.Quantize.MEDIANCUT,
                       dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        with Image.open(io.BytesIO(data)) as check:
            assert check.info == {}, f"PNG metadata present: {source.name}: {check.info}"
        return data

def load_initial() -> dict[int, bytes]:
    result = {}
    with zipfile.ZipFile(INITIAL) as z:
        for name in z.namelist():
            match = re.fullmatch(r"IMG_(\d{4})\.png", Path(name).name)
            if not match:
                continue
            number = int(match.group(1))
            if number in result:
                raise ValueError(f"Duplicate archived image: {number}")
            result[number] = z.read(name)
    if set(result) != OLD:
        raise ValueError(f"Existing archive incomplete: {sorted(OLD - set(result))}")
    return result

def load_new() -> dict[int, bytes]:
    result = {}
    candidates = sorted(
        p for p in INCOMING.iterdir()
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")
    ) if INCOMING.exists() else []
    for p in candidates:
        m = re.match(r"^IMG_(\d{4})(?:\b|[_ (.-])", p.name)
        if not m:
            raise ValueError(f"Unexpected photo name: {p.name}")
        number = int(m.group(1))
        if number not in NEW:
            raise ValueError(f"Unexpected photo number: {number}")
        if number in result:
            raise ValueError(f"Duplicate photo number: {number}")
        result[number] = clean_png(p)
    if set(result) != NEW:
        raise ValueError(f"Missing new photos: {sorted(NEW - set(result))}")
    return result

def main() -> None:
    photos = {**load_initial(), **load_new()}
    if set(photos) != (OLD | NEW) or len(photos) != 48:
        raise ValueError("Photo verification failed")
    manifest = []
    for n, raw in sorted(photos.items()):
        with Image.open(io.BytesIO(raw)) as im:
            if im.format != "PNG" or im.info:
                raise ValueError(f"Unexpected format or metadata: IMG_{n}.png")
            size = im.size
        manifest.append(dict(file=f"IMG_{n}.png",
                             width=size[0], height=size[1],
                             bytes=len(raw),
                             sha256=hashlib.sha256(raw).hexdigest()))
    temp = DEST.with_suffix(".zip.partial")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as z:
        for n, data in sorted(photos.items()):
            z.writestr(f"IMG_{n}.png", data)
        z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        z.writestr("README.md",
                   "# Zortrax M300 Dual PCB photos\n\n"
                   "48 PNG photographs with image metadata removed.\n"
                   "Images were reduced to fit a GitHub-sized archive.\n")
    with zipfile.ZipFile(temp) as z:
        if z.testzip() is not None or len([n for n in z.namelist() if n.endswith(".png")]) != 48:
            raise ValueError("ZIP verification failed")
    temp.replace(DEST)
    print(f"PASS: {len(photos)} photos, ZIP {DEST.stat().st_size:,} bytes")
    print(f"SHA256: {hashlib.sha256(DEST.read_bytes()).hexdigest()}")
    if DEST.stat().st_size > 95_000_000:
        raise ValueError("GitHub file size limit: image archive too large")
    # Optional visual contact sheet, also stripped of metadata.
    w, h, cols = 240, 210, 6
    sheet = Image.new("RGB", (cols*w, math.ceil(len(photos)/cols)*h), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (n, raw) in enumerate(sorted(photos.items())):
        with Image.open(io.BytesIO(raw)) as src:
            frame = src.convert("RGB")
            frame.thumbnail((w-16, h-34))
        x = (i % cols)*w + (w-frame.width)//2
        y = (i // cols)*h
        sheet.paste(frame, (x,y))
        draw.text((i % cols*w+12, y+h-25), f"IMG_{n}", fill="black")
    sheet.save(SHEET, "PNG", optimize=True)
    with Image.open(SHEET) as check:
        assert check.info == {}

if __name__ == "__main__":
    main()
