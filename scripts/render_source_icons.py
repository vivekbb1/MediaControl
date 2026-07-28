#!/usr/bin/env python3
"""Build stb / usb_c / whiteboard brand icons from official reference PNGs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from potrace import Bitmap

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT_SIZE = 512
BEZIER_STEPS = 16

ICONS = {
    "stb": "stb-icon-ref.png",
    "usb_c": "usb-c-icon-ref.png",
    "whiteboard": "whiteboard-icon-ref.png",
}


def import_official_brand(ref: Path, png_path: Path, size: int = OUT_SIZE) -> None:
    """Invert official black-on-transparent refs to white brand PNGs."""
    im = Image.open(ref).convert("RGBA")
    arr = np.array(im)
    alpha = arr[..., 3].astype(np.uint8)
    white = np.zeros_like(arr)
    white[..., :3] = 255
    white[..., 3] = alpha
    icon = Image.fromarray(white, "RGBA")

    w, h = icon.size
    scale = size / max(w, h)
    out_w, out_h = max(1, round(w * scale)), max(1, round(h * scale))
    icon = icon.resize((out_w, out_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(icon, ((size - out_w) // 2, (size - out_h) // 2))
    canvas.save(png_path, "PNG", optimize=True)

def load_alpha_mask(path: Path) -> tuple[np.ndarray, int, int]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    arr = np.array(im)
    dark = (arr[..., 3] > 32) & (arr[..., 0] + arr[..., 1] + arr[..., 2] < 640)
    return dark, w, h


def trace_paths(mask: np.ndarray):
    return Bitmap(mask.astype(bool)).trace(turdsize=0)


def curve_to_svg_d(curve) -> str:
    parts = [f"M {curve.start_point.x:.3f} {curve.start_point.y:.3f}"]
    for segment in curve.segments:
        if segment.is_corner:
            parts.append(f"L {segment.c.x:.3f} {segment.c.y:.3f}")
            parts.append(f"L {segment.end_point.x:.3f} {segment.end_point.y:.3f}")
        else:
            parts.append(
                f"C {segment.c1.x:.3f} {segment.c1.y:.3f} "
                f"{segment.c2.x:.3f} {segment.c2.y:.3f} "
                f"{segment.end_point.x:.3f} {segment.end_point.y:.3f}"
            )
    parts.append("Z")
    return " ".join(parts)


def _bezier_points(p0, p1, p2, p3, steps: int = BEZIER_STEPS) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        s = 1 - t
        points.append(
            (
                s**3 * p0[0] + 3 * s**2 * t * p1[0] + 3 * s * t**2 * p2[0] + t**3 * p3[0],
                s**3 * p0[1] + 3 * s**2 * t * p1[1] + 3 * s * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return points


def curve_to_polygon(curve, steps: int = BEZIER_STEPS) -> list[tuple[float, float]]:
    points = [(curve.start_point.x, curve.start_point.y)]
    current = curve.start_point
    for segment in curve.segments:
        if segment.is_corner:
            points.append((segment.c.x, segment.c.y))
            points.append((segment.end_point.x, segment.end_point.y))
            current = segment.end_point
        else:
            bpts = _bezier_points(
                (current.x, current.y),
                (segment.c1.x, segment.c1.y),
                (segment.c2.x, segment.c2.y),
                (segment.end_point.x, segment.end_point.y),
                steps,
            )
            points.extend(bpts[1:])
            current = segment.end_point
    return points


def rasterize_paths_to_png(paths, src_w: int, src_h: int, out_path: Path, size: int = OUT_SIZE) -> None:
    scale = size / max(src_w, src_h)
    out_w = max(1, round(src_w * scale))
    out_h = max(1, round(src_h * scale))

    layer = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for curve in paths:
        polygon = [(x * scale, y * scale) for x, y in curve_to_polygon(curve)]
        draw.polygon(polygon, fill=(255, 255, 255, 255))

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ox = (size - out_w) // 2
    oy = (size - out_h) // 2
    canvas.paste(layer, (ox, oy), layer)
    canvas.save(out_path, "PNG", optimize=True)


def build_svg(paths, src_w: int, src_h: int) -> str:
    body = "\n  ".join(f'<path fill="#FFFFFF" d="{d}"/>' for d in paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {src_w} {src_h}" '
        f'aria-hidden="true" shape-rendering="geometricPrecision">\n  {body}\n</svg>'
    )


def brand_name(key: str) -> str:
    return key.replace("_", "-")


def process_icon(key: str, ref_name: str, mode: str) -> None:
    ref = ASSETS / ref_name
    if not ref.exists():
        raise FileNotFoundError(ref)
    name = brand_name(key)
    png_path = ASSETS / f"{name}-brand.png"
    if mode == "import":
        import_official_brand(ref, png_path)
        print(f"{key}: imported {ref.name} -> {png_path.name} ({OUT_SIZE}px)")
        return

    mask, w, h = load_alpha_mask(ref)
    traced = trace_paths(mask)
    if not traced:
        raise RuntimeError(f"No paths traced for {key} from {ref}")
    svg_paths = [curve_to_svg_d(curve) for curve in traced]
    svg = build_svg(svg_paths, w, h)
    svg_path = ASSETS / f"{name}-brand.svg"
    svg_path.write_text(svg, encoding="utf-8")
    rasterize_paths_to_png(traced, w, h, png_path)
    print(f"{key}: {len(traced)} paths -> {svg_path.name}; hi-res {png_path.name} ({OUT_SIZE}px)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--icon", choices=[*ICONS.keys(), "all"], default="all")
    parser.add_argument(
        "--mode",
        choices=["import", "trace"],
        default="import",
        help="import official refs to white PNGs (default), or potrace to SVG+PNG",
    )
    args = parser.parse_args()
    keys = ICONS if args.icon == "all" else {args.icon: ICONS[args.icon]}
    for key, ref in keys.items():
        process_icon(key, ref, args.mode)


if __name__ == "__main__":
    main()
