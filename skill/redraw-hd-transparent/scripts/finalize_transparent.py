#!/usr/bin/env python3
"""Resize a transparent image onto an exact canvas and verify its metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--dpi", type=float, default=300)
    parser.add_argument(
        "--fit",
        choices=("contain", "cover", "stretch"),
        default="contain",
    )
    return parser.parse_args()


def resized_rgba(
    image: Image.Image, width: int, height: int, fit: str
) -> Image.Image:
    source = image.convert("RGBA")
    if fit == "stretch":
        return source.resize((width, height), Image.Resampling.LANCZOS)

    scale_x = width / source.width
    scale_y = height / source.height
    scale = min(scale_x, scale_y) if fit == "contain" else max(scale_x, scale_y)
    resized_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    resized = source.resize(resized_size, Image.Resampling.LANCZOS)

    if fit == "contain":
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        offset = ((width - resized.width) // 2, (height - resized.height) // 2)
        canvas.alpha_composite(resized, offset)
        return canvas

    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def main() -> None:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.dpi <= 0:
        raise SystemExit("width, height, and dpi must be positive")
    if not args.input.is_file():
        raise SystemExit(f"input does not exist: {args.input}")
    if args.output.exists():
        raise SystemExit(f"output already exists: {args.output}")

    with Image.open(args.input) as source:
        result = resized_rgba(source, args.width, args.height, args.fit)

    alpha = result.getchannel("A")
    extrema = alpha.getextrema()
    if extrema is None or extrema[0] == 255:
        raise SystemExit("input/result has no transparent pixels")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, format="PNG", dpi=(args.dpi, args.dpi), optimize=True)

    with Image.open(args.output) as check:
        report = {
            "output": str(args.output.resolve()),
            "width": check.width,
            "height": check.height,
            "dpi": [round(value, 3) for value in check.info.get("dpi", ())],
            "mode": check.mode,
            "has_alpha": "A" in check.getbands(),
            "alpha_extrema": list(check.getchannel("A").getextrema()),
            "fit": args.fit,
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
