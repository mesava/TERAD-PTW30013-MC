#!/usr/bin/env python3
"""Build one Stage 8 TERAD RW3 configuration with benchmark-validated PTW30013 Model B1.

RW3 geometry/material anchors:
- PTW RW3 manual D188.131.00/03;
- chamber plate 29672/U19 for PTW 30013;
- U19 chamber-axis offsets H1=7 mm and H2=13 mm in the 20 mm plate;
- in the user's actual setup the chamber axis is 7 mm below the upper face of U19,
  with an additional 13 mm RW3 slab stack placed above that face;
- therefore the physical surface-to-axis/reference-point depth is 13 + 7 = 20 mm;
- RW3 material is polystyrene (C8H8) with nominal 2% TiO2 by mass,
  density 1.045 g/cm3. The manufacturer tolerance 2.0 +/- 0.4% TiO2 is
  retained for later material sensitivity and is not fitted here.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

RW3_DENSITY = 1.045
RW3_H = 0.0759
RW3_C = 0.9041
RW3_O = 0.0080
RW3_TI = 0.0120
U19_H1_CM = 0.7
U19_H2_CM = 1.3
OVERLYING_RW3_CM = 1.3
CENTER_DEPTH_CM = OVERLYING_RW3_CM + U19_H1_CM  # 2.0 cm physical
DOWNSTREAM_Z_CM = 10.0  # canonical approximate downstream RW3 from chamber axis


def replace_section(text: str, start_anchor: str, end_anchor: str, transform) -> str:
    i = text.find(start_anchor)
    if i < 0:
        raise SystemExit(f"Missing section start anchor: {start_anchor}")
    j = text.find(end_anchor, i)
    if j < 0:
        raise SystemExit(f"Missing section end anchor: {end_anchor}")
    section = text[i:j]
    return text[:i] + transform(section) + text[j:]


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

    # Fixed benchmark-validated Model B1 geometry.
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

    if "set label = chamber_cavity 5 11 15" not in text:
        raise SystemExit("cavity label anchor missing")
    text = text.replace("set label = chamber_cavity 5 11 15", "set label = chamber_cavity 10 16 20", 1)

    old_xcse = "set label = chamber_xcse_zone 0 5 6 7 8 10 11 12 13 14 15 16 17 18 20"
    new_xcse = "set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25"
    if old_xcse not in text:
        raise SystemExit("XCSE label anchor missing")
    text = text.replace(old_xcse, new_xcse, 1)

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
    net_cavity_volume = math.pi * r * r * L - math.pi * re * re * Le
    cavity_mass = net_cavity_volume * rho_air
    if "cavity mass = 7.410453757123e-4" not in text:
        raise SystemExit("Model A cavity mass anchor missing")
    text = text.replace("cavity mass = 7.410453757123e-4", f"cavity mass = {cavity_mass:.15e}", 1)

    # PTW-manual nominal RW3 medium.
    rw3_media = f"""
    :start RW3_NOMINAL:
        elements = H, C, O, Ti
        mass fractions = {RW3_H:.4f}, {RW3_C:.4f}, {RW3_O:.4f}, {RW3_TI:.4f}
        bulk density = {RW3_DENSITY:.6f}
        bremsstrahlung correction = NRC
    :stop RW3_NOMINAL:
"""
    if ":stop media definition:" not in text:
        raise SystemExit("media definition end missing")
    text = text.replace(":stop media definition:", rw3_media + ":stop media definition:", 1)

    def chamber_to_rw3(section: str) -> str:
        return section.replace("WATER_1KEV", "RW3_NOMINAL")

    text = replace_section(
        text,
        "        name = ptw30013_modelA_xcse",
        "    # Exact cavity-envelope helper",
        chamber_to_rw3,
    )

    def score_to_rw3(section: str) -> str:
        section = section.replace("name = water_score_xcse", "name = rw3_score_xcse")
        section = section.replace("WATER_1KEV", "RW3_NOMINAL")
        section = section.replace("set label = water_score 2", "set label = rw3_score 2")
        section = section.replace("set label = water_xcse_zone 0 2 3 4", "set label = rw3_xcse_zone 0 2 3 4")
        return section

    text = replace_section(
        text,
        "        name = water_score_xcse",
        "    # Original Dw voxel as a helper cavity geometry",
        score_to_rw3,
    )

    text = replace_section(
        text,
        "        name = phsp_box",
        "    # Reference water phantom",
        lambda s: s.replace("WATER_1KEV", "RW3_NOMINAL"),
    )

    # Direct physical U19 RW3 geometry: 13 mm overlying slabs + 7 mm in U19 = 20 mm.
    surface_z = -CENTER_DEPTH_CM
    source_z = -(args.ssd + CENTER_DEPTH_CM)
    downstream_z = DOWNSTREAM_Z_CM

    if "name = water_phantom" not in text:
        raise SystemExit("water phantom anchor missing")
    text = text.replace("name = water_phantom", "name = rw3_phantom", 1)

    marker = "name = rw3_phantom"
    head, tail = text.split(marker, 1)
    tail = tail.replace("x-planes = -10 10", "x-planes = -15 15", 1)
    tail = tail.replace("y-planes = -10 10", "y-planes = -15 15", 1)
    if "z-planes = -2 18" not in tail:
        raise SystemExit("phantom z-plane anchor missing")
    tail = tail.replace("z-planes = -2 18", f"z-planes = {source_z:.4f} {surface_z:.4f} {downstream_z:.4f}", 1)
    oldmedia = "media = WATER_1KEV\n        :stop media input:"
    newmedia = "media = AIR_1KEV RW3_NOMINAL\n            set medium = 1 1\n        :stop media input:"
    if oldmedia not in tail:
        raise SystemExit("phantom media anchor missing")
    tail = tail.replace(oldmedia, newmedia, 1)
    text = head + marker + tail

    text = text.replace("base geometry = water_phantom", "base geometry = rw3_phantom")
    text = text.replace("name = chamber_in_water", "name = chamber_in_rw3")
    text = text.replace("name = dose_to_water", "name = dose_to_rw3")
    text = text.replace("inscribed geometries = water_score_xcse", "inscribed geometries = rw3_score_xcse")

    text = text.replace("geometry name = dose_to_water", "geometry name = dose_to_rw3")
    text = text.replace("cavity regions = water_score", "cavity regions = rw3_score")
    text = text.replace("enhance regions = water_xcse_zone", "enhance regions = rw3_xcse_zone")
    text = text.replace("geometry name = chamber_in_water", "geometry name = chamber_in_rw3")
    text = text.replace("correlated geometries = dose_to_water chamber_in_water", "correlated geometries = dose_to_rw3 chamber_in_rw3")

    rw3_score_mass = math.pi * 1.0 * 1.0 * 0.025 * RW3_DENSITY
    if "cavity mass = 7.853981633974483e-2" not in text:
        raise SystemExit("water score mass anchor missing")
    text = text.replace("cavity mass = 7.853981633974483e-2", f"cavity mass = {rw3_score_mass:.15e}", 1)

    text = text.replace("rejection range medium = WATER_1KEV", "rejection range medium = RW3_NOMINAL", 1)

    if "position = 0 0 -100" not in text:
        raise SystemExit("source position anchor missing")
    text = text.replace("position = 0 0 -100", f"position = 0 0 {source_z:.4f}", 1)

    sdd = args.ssd + CENTER_DEPTH_CM
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
        "name = rw3_phantom",
        "name = chamber_in_rw3",
        "name = dose_to_rw3",
        "set label = rw3_score 2",
        "set label = rw3_xcse_zone 0 2 3 4",
        "elements = H, C, O, Ti",
        f"bulk density = {RW3_DENSITY:.6f}",
        f"z-planes = {source_z:.4f} {surface_z:.4f} {downstream_z:.4f}",
        f"position = 0 0 {source_z:.4f}",
        f"spectrum file = $EGS_HOME/egs_chamber/{args.beam}.ensrc",
        f"cavity mass = {cavity_mass:.15e}",
        f"cavity mass = {rw3_score_mass:.15e}",
        "rejection range medium = RW3_NOMINAL",
    ]
    for check in checks:
        if check not in text:
            raise SystemExit(f"Stage 8 self-check failed: {check}")
    if "@@" in text:
        raise SystemExit("Unresolved template token remains")
    if not (source_z < surface_z < 0 < downstream_z):
        raise SystemExit("Invalid RW3 source/phantom z geometry")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)

    print(f"Wrote {out}")
    print(f"beam={args.beam}; SSD={args.ssd:g} cm; physical chamber-axis depth={CENTER_DEPTH_CM:.4f} cm")
    print(f"overlying RW3={OVERLYING_RW3_CM:.4f} cm + U19 H1={U19_H1_CM:.4f} cm = {CENTER_DEPTH_CM:.4f} cm")
    print(f"U19 H1={U19_H1_CM:.4f} cm; H2={U19_H2_CM:.4f} cm")
    print(f"surface field={args.field_x:g}x{args.field_y:g} cm2")
    print(f"reference-plane projected field={2*hx:.6f}x{2*hy:.6f} cm2")
    print(f"source z={source_z:.4f}; RW3 surface z={surface_z:.4f}; downstream z={downstream_z:.4f}")
    print(f"RW3 density={RW3_DENSITY:.6f} g/cm3; H/C/O/Ti={RW3_H}/{RW3_C}/{RW3_O}/{RW3_TI}")
    print(f"RW3 score mass={rw3_score_mass:.15e} g")
    print(f"cavity mass={cavity_mass:.15e} g")


if __name__ == "__main__":
    main()