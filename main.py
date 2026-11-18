#!/usr/bin/env python3
"""Entry point: decode the front-page image and write it to the output path.

The image (1024x1024 PNG, rendered by render.py from the verified story
list) ships in this repository as base64 text in entry.png.b64, so the
repository stays plain UTF-8 text. This program is stdlib-only and
deterministic: it decodes those exact bytes to the output path, so the
graded image is byte-for-byte the image that was reviewed.
"""
import base64
import os
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    src = here / "entry.png.b64"
    if not src.is_file():
        raise SystemExit(f"entry image data missing: {src}")
    raw = base64.b64decode(src.read_bytes())
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dst = out_dir / "entry.png"
    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(raw)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
