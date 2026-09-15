#!/usr/bin/env python3
"""Build one Stage 5 TERAD water configuration using benchmark-validated PTW30013 Model B1.

Canonical geometry:
- chamber reference point at z=0;
- water surface at z=-2 cm (2 cm chamber-centre depth);
- SSD is source-to-phantom-surface distance supplied by the clinical applicator;
- source therefore sits at z=-(SSD+2) cm;
- applicator field size is defined at the phantom surface and projected to z=0;
- water phantom transverse size 30x30 cm2;
- 10 cm water downstream of the chamber reference point;
- explicit air transport between source and water surface.

Important limitation:
The supplied project data define applicator SSD and aperture size, but not applicator-wall
material/thickness/internal geometry. Stage 5 therefore models the clinical aperture/SSD
geometry, not hardware scatter from a proprietary applicator body.

For rectangular apertures, the computational convention is field_x x field_y = first x
second listed dimension, with x parallel to the chamber axis/stem direction. This convention
is documented for later orientation sensitivity if the physical applicator orientation is
not independently confirmed.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--output", required=True)
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

    text = Path(args.template).read_text()

    # ------------------------------------------------------------------
    # Fixed benchmark-validated Model B1 geometry (identical to Stage 3H-4/5 and Stage 4).
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
    text = text.replace("cavity mass = 7.410453757123e-4", f"cavity mass = {mass:.15e}", 1)

    # ------------------------------------------------------------------
    # Matched water phantom for the real TERAD measurement geometry.
    # Source-to-surface SSD is supplied; chamber is 2 cm below surface.
    # Air is explicitly transported from source plane to water surface.
    # ------------------------------------------------------------------
    source_z = -(args.ssd + 2.0)
    water_surface_z = -2.0
    water_downstream_z = 10.0

    marker = "name = water_phantom"
    if marker not in text:
        raise SystemExit("water phantom missing")
    head, tail = text.split(marker, 1)
    tail = tail.replace("x-planes = -10 10", "x-planes = -15 15", 1)
    tail = tail.replace("y-planes = -10 10", "y-planes = -15 15", 1)
    if "z-planes = -2 18" not in tail:
        raise SystemExit("water z-plane anchor missing")
    tail = tail.replace("z-planes = -2 18", f"z-planes = {source_z:g} -2 10", 1)
    oldmedia = "media = WATER_1KEV\n        :stop media input:"
    newmedia = "media = AIR_1KEV WATER_1KEV\n            set medium = 1 1\n        :stop media input:"
    if oldmedia not in tail:
        raise SystemExit("water phantom media anchor missing")
    tail = tail.replace(oldmedia, newmedia, 1)
    text = head + marker + tail

    # ------------------------------------------------------------------
    # Point source + clinical applicator aperture.
    # Field is specified at the phantom surface, so project it to z=0.
    # ------------------------------------------------------------------
    if "position = 0 0 -100" not in text:
        raise SystemExit("source position anchor missing")
    text = text.replace("position = 0 0 -100", f"position = 0 0 {source_z:g}", 1)

    sdd = args.ssd + 2.0
    scale = sdd / args.ssd
    hx = 0.5 * args.field_x * scale
    hy = 0.5 * args.field_y * scale
    old_target = """        :start target shape:
            library = egs_circle
            radius = 5.25
        :stop target shape:
"""
    new_target = f"""        :start target shape:
            library = egs_rectangle
            rectangle = {-hx:.8f} {-hy:.8f} {hx:.8f} {hy:.8f}
        :stop target shape:
"""
    if old_target not in text:
        raise SystemExit("benchmark target anchor missing")
    text = text.replace(old_target, new_target, 1)

    replacements = {
        "@@BEAM@@": args.beam,
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

    checks = [
        "set label = chamber_cavity 10 16 20",
        "set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25",
        f"z-planes = {source_z:g} -2 10",
        f"position = 0 0 {source_z:g}",
        f"spectrum file = $EGS_HOME/egs_chamber/{args.beam}.ensrc",
        f"cavity mass = {mass:.15e}",
    ]
    for check in checks:
        if check not in text:
            raise SystemExit(f"Stage 5 self-check failed: {check}")
    if "@@" in text:
        raise SystemExit("Unresolved template token remains")
    if not (source_z < water_surface_z < 0 < water_downstream_z):
        raise SystemExit("Invalid TERAD source/phantom z geometry")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"Wrote {out}")
    print(f"beam={args.beam}; SSD={args.ssd:g} cm; SDD={sdd:g} cm; depth=2 cm")
    print(f"surface field={args.field_x:g}x{args.field_y:g} cm2")
    print(f"reference-plane projected field={2*hx:.6f}x{2*hy:.6f} cm2")
    print(f"source z={source_z:g} cm; water z=-2..10 cm; explicit air={args.ssd:g} cm")
    print(f"net cavity air volume={net:.12f} cm3; cavity mass={mass:.15e} g")


if __name__ == "__main__":
    main()
