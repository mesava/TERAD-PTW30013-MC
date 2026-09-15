#!/usr/bin/env python3
"""Build a Stage 8-equivalent RW3 input with perturbed TiO2 mass fraction.

This is a sensitivity wrapper around the accepted Stage 8 builder. It changes only the
RW3 elemental composition corresponding to a requested TiO2 mass fraction and leaves
geometry, chamber Model B1, density, beam spectrum and transport settings unchanged.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Atomic weights used only to decompose polystyrene and TiO2 into elemental mass fractions.
AW_H = 1.008
AW_C = 12.011
AW_O = 15.999
AW_TI = 47.867


def elemental_fractions(tio2_mass_fraction: float) -> tuple[float, float, float, float]:
    if not (0.0 < tio2_mass_fraction < 0.10):
        raise SystemExit("TiO2 mass fraction must be between 0 and 0.10")

    mw_ps = 8.0 * AW_C + 8.0 * AW_H
    h_ps = 8.0 * AW_H / mw_ps
    c_ps = 8.0 * AW_C / mw_ps

    mw_tio2 = AW_TI + 2.0 * AW_O
    ti_tio2 = AW_TI / mw_tio2
    o_tio2 = 2.0 * AW_O / mw_tio2

    f = tio2_mass_fraction
    h = (1.0 - f) * h_ps
    c = (1.0 - f) * c_ps
    o = f * o_tio2
    ti = f * ti_tio2

    total = h + c + o + ti
    if abs(total - 1.0) > 1e-12:
        raise SystemExit(f"Elemental fractions do not sum to unity: {total}")
    return h, c, o, ti


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
    ap.add_argument("--tio2-mass-fraction", required=True, type=float)
    args = ap.parse_args()

    builder = Path(__file__).with_name("build_stage8_terad_rw3_b1.py")
    cmd = [
        sys.executable, str(builder),
        "--template", args.template,
        "--output", args.output,
        "--beam", args.beam,
        "--ssd", str(args.ssd),
        "--field-x", str(args.field_x),
        "--field-y", str(args.field_y),
        "--ncase", str(args.ncase),
        "--nbatch", str(args.nbatch),
        "--xcse", str(args.xcse),
        "--rr", str(args.rr),
        "--seed1", str(args.seed1),
        "--seed2", str(args.seed2),
    ]
    subprocess.run(cmd, check=True)

    h, c, o, ti = elemental_fractions(args.tio2_mass_fraction)
    fractions = f"{h:.8f}, {c:.8f}, {o:.8f}, {ti:.8f}"

    out = Path(args.output)
    text = out.read_text()
    pattern = r"(:start RW3_NOMINAL:.*?mass fractions = )[^\n]+"
    text2, n = re.subn(pattern, rf"\g<1>{fractions}", text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"Expected one RW3_NOMINAL mass-fraction replacement, got {n}")
    if "bulk density = 1.045000" not in text2:
        raise SystemExit("Sensitivity run must keep RW3 density fixed at 1.045 g/cm3")
    if fractions not in text2:
        raise SystemExit("Perturbed elemental fractions were not written")
    if abs(sum((h, c, o, ti)) - 1.0) > 1e-12:
        raise SystemExit("Mass-fraction self-check failed")

    out.write_text(text2)
    print(f"TiO2 mass fraction={args.tio2_mass_fraction:.6f} ({100*args.tio2_mass_fraction:.3f}%)")
    print(f"RW3 elemental H/C/O/Ti={fractions}")
    print("RW3 density remains fixed at 1.045000 g/cm3")
    print("Geometry and chamber model are inherited unchanged from accepted Stage 8 builder")


if __name__ == "__main__":
    main()
