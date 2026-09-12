#!/usr/bin/env python3
"""Build the predeclared nominal PTW30013 Model B1 input for Stage 3H-4.

This is a high-stat confirmation of the already selected 1.5 mm PMMA tip surrogate.
It does not fit any geometry parameter to the published benchmark.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--beam", required=True, choices=["CCRI100", "CCRI250"])
    ap.add_argument("--ncase", required=True)
    ap.add_argument("--nbatch", required=True)
    ap.add_argument("--xcse", required=True)
    ap.add_argument("--rr", required=True)
    ap.add_argument("--seed1", required=True)
    ap.add_argument("--seed2", required=True)
    args = ap.parse_args()

    p = Path(args.template)
    text = p.read_text()

    # B0: public sensitive length 23.0 mm instead of Model A 21.8 mm.
    if text.count("thickness = 0.03") != 2:
        raise SystemExit("Unexpected Model A end-gap structure")
    text = text.replace("thickness = 0.03", "thickness = 0.09")
    text = text.replace("axis = 2.09 0 0  -1 0 0", "axis = 2.15 0 0  -1 0 0", 1)
    text = text.replace("positions = -1.09 1.09", "positions = -1.15 1.15", 1)

    # B1 nominal: 1.5 mm PMMA tip surrogate, fixed a priori from
    # 13.0 mm public reference-point distance - 23.0/2 mm sensitive half-length.
    tip = 0.15
    old_layer = """        :start layer:
            thickness = 1.0
            top radii    = 1.3475
            bottom radii = 1.3475
            media = WATER_1KEV
        :stop layer:

        :start layer:
            thickness = 0.09
"""
    new_layer = """        :start layer:
            thickness = 0.85
            top radii    = 1.3475
            bottom radii = 1.3475
            media = WATER_1KEV
        :stop layer:

        :start layer:
            thickness = 0.15
            top radii    = 0.3475 1.3475
            bottom radii = 0.3475 1.3475
            media = PMMA_1KEV WATER_1KEV
        :stop layer:

        :start layer:
            thickness = 0.09
"""
    if old_layer not in text:
        raise SystemExit("Could not insert nominal B1 tip layer")
    text = text.replace(old_layer, new_layer, 1)

    # Correct EGS_ConeStack labels for nmax=5 after adding the two-region tip layer.
    old = "set label = chamber_cavity 5 11 15"
    new = "set label = chamber_cavity 10 16 20"
    if old not in text:
        raise SystemExit("cavity label anchor missing")
    text = text.replace(old, new, 1)

    old = "set label = chamber_xcse_zone 0 5 6 7 8 10 11 12 13 14 15 16 17 18 20"
    new = "set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25"
    if old not in text:
        raise SystemExit("XCSE label anchor missing")
    text = text.replace(old, new, 1)

    # Expand chamber enhancement list from 15 to 17 values.
    marker = "geometry name = chamber_in_water"
    if marker not in text:
        raise SystemExit("chamber calculation geometry missing")
    head, chamber = text.split(marker, 1)
    body, tail = chamber.split(":stop calculation geometry:", 1)
    if "enhance regions = chamber_xcse_zone" not in body:
        raise SystemExit("chamber XCSE scoring block missing")
    token = "@@XCSE@@"
    if body.count(token) != 15:
        raise SystemExit(f"Unexpected chamber enhancement count: {body.count(token)}")
    pos = body.rfind(token) + len(token)
    body = body[:pos] + " \\\n                      @@XCSE@@ @@XCSE@@" + body[pos:]
    if body.count(token) != 17:
        raise SystemExit("Could not expand chamber enhancement list to 17 values")
    text = head + marker + body + ":stop calculation geometry:" + tail

    # B0 cavity mass retained for the 23.0 mm sensitive volume.
    rho_air = 1.2048e-3
    r, L, re, Le = 0.305, 2.30, 0.0575, 2.12
    net = math.pi * r * r * L - math.pi * re * re * Le
    mass = net * rho_air
    old = "cavity mass = 7.410453757123e-4"
    new = f"cavity mass = {mass:.15e}"
    if old not in text:
        raise SystemExit("Model A cavity mass anchor missing")
    text = text.replace(old, new, 1)

    # Paper-faithful air geometry: first 50 cm folded into spectrum,
    # remaining 48 cm explicitly transported to water surface z=-2 cm.
    marker = "name = water_phantom"
    if marker not in text:
        raise SystemExit("water phantom missing")
    head, tail = text.split(marker, 1)
    if "z-planes = -2 18" not in tail:
        raise SystemExit("water z-plane anchor missing")
    tail = tail.replace("z-planes = -2 18", "z-planes = -50 -2 18", 1)
    oldmedia = "media = WATER_1KEV\n        :stop media input:"
    newmedia = "media = AIR_1KEV WATER_1KEV\n            set medium = 1 1\n        :stop media input:"
    if oldmedia not in tail:
        raise SystemExit("water phantom media anchor missing")
    tail = tail.replace(oldmedia, newmedia, 1)
    text = head + marker + tail

    replacements = {
        "@@BEAM@@": args.beam,
        "@@XCSE@@": args.xcse,
        "@@RR@@": args.rr,
        "@@NCASE@@": args.ncase,
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    text = text.replace("nbatch = 10", f"nbatch = {args.nbatch}", 1)

    rng = (
        ":start rng definition:\n"
        "    type = ranmar\n"
        f"    initial seeds = {args.seed1} {args.seed2}\n"
        ":stop rng definition:\n\n"
    )
    marker = ":start run control:"
    if marker not in text:
        raise SystemExit("run control anchor missing")
    text = text.replace(marker, rng + marker, 1)

    if "@@" in text:
        raise SystemExit("Unresolved template token remains")
    if "set label = chamber_cavity 10 16 20" not in text:
        raise SystemExit("Nominal B1 cavity labels missing")
    if "set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25" not in text:
        raise SystemExit("Nominal B1 XCSE labels missing")
    if "z-planes = -50 -2 18" not in text:
        raise SystemExit("air48 geometry missing")
    if abs((1.15 + tip) - 1.30) > 1e-12:
        raise SystemExit("Nominal public-derived tip position check failed")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"Wrote {out}")
    print(f"nominal tip = {tip:.2f} cm; external tip position = {1.15 + tip:.2f} cm")
    print(f"net cavity air volume = {net:.12f} cm3")
    print(f"cavity mass = {mass:.15e} g")


if __name__ == "__main__":
    main()
