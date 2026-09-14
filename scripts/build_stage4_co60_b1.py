#!/usr/bin/env python3
"""Build the fixed benchmark-validated PTW30013 Model B1 for Co-60 anchor.

Reference geometry used by this project:
- chamber reference point at z = 0;
- source-to-reference distance SDD = 100 cm;
- water surface at z = -5 cm (SSD = 95 cm, 5 cm water depth);
- 10 x 10 cm2 field at the chamber reference plane;
- 30 x 30 x 30 cm3 water phantom downstream of the surface;
- 95 cm of air between source and water surface is transported explicitly;
- Co-60 primary spectrum is an inline two-line spectrum using the evaluated
  1173.228 and 1332.492 keV emissions.

The accepted Model B1 chamber geometry is copied exactly from Stage 3H-4/5.
No chamber parameter is fitted or changed here.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ncase", required=True)
    ap.add_argument("--nbatch", required=True)
    ap.add_argument("--xcse", required=True)
    ap.add_argument("--rr", required=True)
    ap.add_argument("--seed1", required=True)
    ap.add_argument("--seed2", required=True)
    args = ap.parse_args()

    text = Path(args.template).read_text()

    # ------------------------------------------------------------------
    # Fixed benchmark-validated Model B1 geometry (identical to Stage 3H-4/5).
    # ------------------------------------------------------------------
    if text.count("thickness = 0.03") != 2:
        raise SystemExit("Unexpected Model A end-gap structure")
    text = text.replace("thickness = 0.03", "thickness = 0.09")
    text = text.replace("axis = 2.09 0 0  -1 0 0", "axis = 2.15 0 0  -1 0 0", 1)
    text = text.replace("positions = -1.09 1.09", "positions = -1.15 1.15", 1)

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

    marker = "geometry name = chamber_in_water"
    head, chamber = text.split(marker, 1)
    body, tail = chamber.split(":stop calculation geometry:", 1)
    token = "@@XCSE@@"
    if body.count(token) != 15:
        raise SystemExit(f"Unexpected chamber enhancement count: {body.count(token)}")
    pos = body.rfind(token) + len(token)
    body = body[:pos] + " \\\n                      @@XCSE@@ @@XCSE@@" + body[pos:]
    text = head + marker + body + ":stop calculation geometry:" + tail

    rho_air = 1.2048e-3
    r, L, re, Le = 0.305, 2.30, 0.0575, 2.12
    net = math.pi * r * r * L - math.pi * re * re * Le
    mass = net * rho_air
    if "cavity mass = 7.410453757123e-4" not in text:
        raise SystemExit("Model A cavity mass anchor missing")
    text = text.replace(
        "cavity mass = 7.410453757123e-4",
        f"cavity mass = {mass:.15e}",
        1,
    )

    # ------------------------------------------------------------------
    # Co-60 reference phantom: 30x30x30 cm3 water, depth 5 cm, SDD 100 cm.
    # Region 0 = explicit source-to-surface air, region 1 = water.
    # ------------------------------------------------------------------
    marker = "name = water_phantom"
    if marker not in text:
        raise SystemExit("water phantom missing")
    head, tail = text.split(marker, 1)
    tail = tail.replace("x-planes = -10 10", "x-planes = -15 15", 1)
    tail = tail.replace("y-planes = -10 10", "y-planes = -15 15", 1)
    if "z-planes = -2 18" not in tail:
        raise SystemExit("water z-plane anchor missing")
    tail = tail.replace("z-planes = -2 18", "z-planes = -100 -5 25", 1)
    oldmedia = "media = WATER_1KEV\n        :stop media input:"
    newmedia = "media = AIR_1KEV WATER_1KEV\n            set medium = 1 1\n        :stop media input:"
    if oldmedia not in tail:
        raise SystemExit("water phantom media anchor missing")
    tail = tail.replace(oldmedia, newmedia, 1)
    text = head + marker + tail

    # Co-60 requires cross-section tables extending above 1.33 MeV.
    text = text.replace("ue = 0.811", "ue = 2.000", 1)
    text = text.replace("up = 0.300", "up = 1.500", 1)

    # ------------------------------------------------------------------
    # Source: point at z=-100 cm, 10x10 cm2 at z=0, two-line Co-60 spectrum.
    # Evaluated absolute gamma intensities 99.85 and 99.9826 per 100 decays
    # are normalized here to probabilities summing to one.
    # ------------------------------------------------------------------
    old_target = """        :start target shape:
            library = egs_circle
            radius = 5.25
        :stop target shape:
"""
    new_target = """        :start target shape:
            library = egs_rectangle
            rectangle = -5 -5 5 5
        :stop target shape:
"""
    if old_target not in text:
        raise SystemExit("benchmark circular target anchor missing")
    text = text.replace(old_target, new_target, 1)

    old_spectrum = """        :start spectrum:
            type = tabulated spectrum
            spectrum file = $EGS_HOME/egs_chamber/@@BEAM@@.ensrc
        :stop spectrum:
"""
    new_spectrum = """        :start spectrum:
            type = tabulated spectrum
            energies = 1.173228 1.332492
            probabilities = 0.4996682223020668 0.5003317776979331
            spectrum mode = 2
        :stop spectrum:
"""
    if old_spectrum not in text:
        raise SystemExit("benchmark spectrum anchor missing")
    text = text.replace(old_spectrum, new_spectrum, 1)

    # Replace every template token, including tokens that only remain in
    # template comments.  The first Stage 4 engineering run failed because
    # @@BEAM@@ survived in the header comment after the physical spectrum
    # block had already been replaced correctly.
    replacements = {
        "@@BEAM@@": "Co60",
        "@@XCSE@@": args.xcse,
        "@@RR@@": args.rr,
        "@@NCASE@@": args.ncase,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("nbatch = 10", f"nbatch = {args.nbatch}", 1)

    rng = (
        ":start rng definition:\n"
        "    type = ranmar\n"
        f"    initial seeds = {args.seed1} {args.seed2}\n"
        ":stop rng definition:\n\n"
    )
    if ":start run control:" not in text:
        raise SystemExit("run control anchor missing")
    text = text.replace(":start run control:", rng + ":start run control:", 1)

    # Deterministic self-checks.
    checks = [
        "set label = chamber_cavity 10 16 20",
        "set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25",
        "z-planes = -100 -5 25",
        "rectangle = -5 -5 5 5",
        "energies = 1.173228 1.332492",
        "spectrum mode = 2",
        "ue = 2.000",
        "up = 1.500",
    ]
    for check in checks:
        if check not in text:
            raise SystemExit(f"Co-60 self-check failed: {check}")
    if "@@" in text:
        unresolved = sorted({part.split("@@", 1)[0] for part in text.split("@@")[1::2]})
        raise SystemExit(f"Unresolved template token remains: {unresolved}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"Wrote {out}")
    print("Co-60 geometry: SDD=100 cm, SSD=95 cm, depth=5 cm, field=10x10 cm2")
    print("Co-60 lines: 1.173228 / 1.332492 MeV")
    print(f"net cavity air volume = {net:.12f} cm3")
    print(f"cavity mass = {mass:.15e} g")


if __name__ == "__main__":
    main()
