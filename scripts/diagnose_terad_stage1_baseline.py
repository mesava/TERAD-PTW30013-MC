#!/usr/bin/env python3
"""Diagnose whether the legacy Stage 1 SpekPy model can represent the authoritative TERAD HVLs.

This script does not generate production spectra. It evaluates the known-filter-only
SpekPy model and reports whether the old one-parameter positive equivalent-Al fit
can physically reach the measured HVL. If the base spectrum is already harder
than the measured beam, the old model family is declared non-representative.
"""
from __future__ import annotations

import csv
from importlib.metadata import version as package_version
from pathlib import Path

import spekpy as sp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "beam_qualities.csv"
OUT = ROOT / "results" / "terad_stage1_baseline_diagnostic.csv"

ANODE_ANGLE_DEG = 20.0
PHYSICS = "kqp"
BIN_WIDTH_KEV = 0.5
TARGET = "W"
DISTANCE_CM = 100.0
MAS = 1.0


def make_base(kvp: float, mat: str, thickness_mm: float):
    s = sp.Spek(
        kvp=kvp,
        th=ANODE_ANGLE_DEG,
        dk=BIN_WIDTH_KEV,
        physics=PHYSICS,
        targ=TARGET,
        x=0.0,
        y=0.0,
        z=DISTANCE_CM,
        mas=MAS,
        brem=True,
        char=True,
    )
    if thickness_mm > 0:
        s.filter(mat, thickness_mm)
    return s


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    summary = []

    for r in rows:
        beam = r["beam_id"]
        kvp = float(r["kvp"])
        target_hvl = float(r["hvl_cu_mm"])
        mat = r["known_filter_material"]
        thick = float(r["known_filter_mm"])
        s = make_base(kvp, mat, thick)
        base_hvl = float(s.get_hvl1(matl="Cu", to="air"))
        delta_pct = 100.0 * (base_hvl / target_hvl - 1.0)
        representable = base_hvl <= target_hvl
        status = "positive_Al_fit_possible" if representable else "model_already_too_hard"
        summary.append({
            "beam_id": beam,
            "kvp": f"{kvp:g}",
            "tube_current_ma": r.get("tube_current_ma", ""),
            "known_filter_material": mat,
            "known_filter_mm": f"{thick:g}",
            "measured_hvl_cu_mm": f"{target_hvl:.6f}",
            "legacy_base_hvl_cu_mm": f"{base_hvl:.6f}",
            "base_minus_measured_percent": f"{delta_pct:+.3f}",
            "legacy_positive_al_fit_status": status,
            "spekpy_version": package_version("spekpy"),
            "physics": PHYSICS,
            "nominal_anode_angle_deg": f"{ANODE_ANGLE_DEG:g}",
        })
        print(
            f"{beam}: measured={target_hvl:.6f} mm Cu, base={base_hvl:.6f} mm Cu, "
            f"delta={delta_pct:+.2f}%, {status}"
        )

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
