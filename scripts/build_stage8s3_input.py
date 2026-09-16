#!/usr/bin/env python3
"""Build Stage 8S3 matched-water or RW3 inputs with point/finite source.

The dosimetric geometry and PTW30013 Model B1 are delegated to the already
validated Stage 5 and Stage 8 builders. The only source-geometry change made
here is the optional replacement of the point source by a uniform circular
source surrogate with physical diameter 7.5 mm.

The 7.5-mm diameter is a tube technical characteristic supplied for this
project. A uniform disk is still a surrogate for the unknown focal-intensity
distribution; therefore this is a source-size sensitivity, not a proprietary
focal-spot reconstruction.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

FOCAL_DIAMETER_CM = 0.75
FOCAL_RADIUS_CM = FOCAL_DIAMETER_CM / 2.0
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--medium", required=True, choices=("water", "rw3"))
    ap.add_argument("--source-model", required=True, choices=("point", "finite_7p5mm"))
    ap.add_argument("--beam", required=True, choices=("Q120", "Q140", "Q150", "Q200"))
    ap.add_argument("--ssd", required=True, type=float)
    ap.add_argument("--field-x", required=True, type=float)
    ap.add_argument("--field-y", required=True, type=float)
    ap.add_argument("--ncase", required=True)
    ap.add_argument("--nbatch", required=True)
    ap.add_argument("--xcse", required=True)
    ap.add_argument("--rr", required=True)
    ap.add_argument("--seed1", required=True)
    ap.add_argument("--seed2", required=True)
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    builder = ROOT / "scripts" / (
        "build_stage5_terad_water_b1.py" if args.medium == "water" else "build_stage8_terad_rw3_b1.py"
    )
    cmd = [
        sys.executable, str(builder),
        "--template", args.template,
        "--output", str(out),
        "--beam", args.beam,
        "--ssd", f"{args.ssd:g}",
        "--field-x", f"{args.field_x:g}",
        "--field-y", f"{args.field_y:g}",
        "--ncase", str(args.ncase),
        "--nbatch", str(args.nbatch),
        "--xcse", str(args.xcse),
        "--rr", str(args.rr),
        "--seed1", str(args.seed1),
        "--seed2", str(args.seed2),
    ]
    subprocess.run(cmd, check=True)

    text = out.read_text()
    source_z = -(args.ssd + 2.0)

    # Confirm the delegated builder made the canonical clinical geometry.
    if args.medium == "water" and "name = chamber_in_water" not in text:
        raise SystemExit("Stage 8S3 water builder lost chamber_in_water")
    if args.medium == "rw3" and "name = chamber_in_rw3" not in text:
        raise SystemExit("Stage 8S3 RW3 builder lost chamber_in_rw3")

    point_pattern = re.compile(
        r"(?P<indent>\s*):start source shape:\s*\n"
        r"(?P=indent)\s*type\s*=\s*point\s*\n"
        r"(?P=indent)\s*position\s*=\s*0\s+0\s+(?P<z>[-+0-9.eE]+)\s*\n"
        r"(?P=indent):stop source shape:",
        re.M,
    )
    m = point_pattern.search(text)
    if not m:
        raise SystemExit("Could not locate delegated point-source block")
    z_found = float(m.group("z"))
    if abs(z_found - source_z) > 1e-6:
        raise SystemExit(f"Unexpected source z: found {z_found}, expected {source_z}")

    if args.source_model == "finite_7p5mm":
        indent = m.group("indent")
        repl = (
            f"{indent}:start source shape:\n"
            f"{indent}    library = egs_circle\n"
            f"{indent}    radius = {FOCAL_RADIUS_CM:.6f}\n"
            f"{indent}    :start transformation:\n"
            f"{indent}        translation = 0 0 {source_z:.6f}\n"
            f"{indent}    :stop transformation:\n"
            f"{indent}:stop source shape:"
        )
        text = text[:m.start()] + repl + text[m.end():]
        if f"radius = {FOCAL_RADIUS_CM:.6f}" not in text or f"translation = 0 0 {source_z:.6f}" not in text:
            raise SystemExit("Finite-source replacement self-check failed")
    else:
        if "type = point" not in text:
            raise SystemExit("Point-source self-check failed")

    out.write_text(text)
    print(f"Wrote {out}")
    print(
        f"medium={args.medium}; beam={args.beam}; SSD={args.ssd:g} cm; source_model={args.source_model}; "
        f"source_z={source_z:g} cm; focal_diameter={FOCAL_DIAMETER_CM:g} cm"
    )


if __name__ == "__main__":
    main()
