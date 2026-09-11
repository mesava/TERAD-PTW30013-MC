#!/usr/bin/env python3
"""Stage 1R-1: map TERAD spectrum-model feasibility against authoritative HVLs.

This is a diagnostic, not a production spectrum generator.
For each TERAD beam from data/terad_input_baseline.csv, hold the known clinical
added filter fixed and scan SpekPy physics families and anode-angle assumptions.

A candidate is called ``fit_possible`` only when the known-filter-only spectrum
is not harder than the measured Cu HVL. In that case a non-negative equivalent
Al nuisance thickness is fitted to the target HVL. If the base model is already
harder than measurement, the case is ``too_hard`` and no unphysical negative
filtration is attempted.
"""
from __future__ import annotations

import csv
import math
from importlib.metadata import version as package_version
from pathlib import Path

import spekpy as sp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "terad_input_baseline.csv"
RESULTS = ROOT / "results"

PHYSICS_MODES = ("kqp", "spekcalc", "spekpy-v1")
ANGLES_DEG = (5, 10, 15, 20, 25, 30, 35, 40, 45)
BIN_WIDTH_KEV = 0.5
DISTANCE_CM = 100.0
TARGET = "W"
MAS = 1.0
MAX_EQ_AL_MM = 50.0
HVL_MATCH_REL = 5e-4  # numerical fit target, 0.05%; not final experimental acceptance


def make_spectrum(kvp: float, physics: str, angle: float, filter_mat: str, filter_mm: float):
    s = sp.Spek(
        kvp=kvp, th=angle, dk=BIN_WIDTH_KEV, physics=physics, targ=TARGET,
        x=0.0, y=0.0, z=DISTANCE_CM, mas=MAS, brem=True, char=True,
    )
    if filter_mm > 0:
        s.filter(filter_mat, filter_mm)
    return s


def clone(s):
    return sp.Spek.clone(s)


def hvl_with_extra_al(base, al_mm: float) -> float:
    s = clone(base)
    if al_mm > 0:
        s.filter("Al", float(al_mm))
    return float(s.get_hvl1(matl="Cu", to="air"))


def fit_positive_al(base, target_hvl: float) -> tuple[float, float] | None:
    h0 = hvl_with_extra_al(base, 0.0)
    if h0 > target_hvl * (1 + HVL_MATCH_REL):
        return None
    if math.isclose(h0, target_hvl, rel_tol=HVL_MATCH_REL, abs_tol=1e-9):
        return 0.0, h0
    def f(x: float) -> float:
        return hvl_with_extra_al(base, x) - target_hvl
    hi = 0.1
    while hi <= MAX_EQ_AL_MM and f(hi) < 0:
        hi *= 2
    if hi > MAX_EQ_AL_MM:
        return None
    x = float(brentq(f, 0.0, hi, xtol=1e-8, rtol=1e-10, maxiter=100))
    return x, hvl_with_extra_al(base, x)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    beams = list(csv.DictReader(BASELINE.open()))
    rows = []
    for b in beams:
        beam = b["beam_id"]
        kvp = float(b["kvp"])
        target_hvl = float(b["hvl_cu_mm"])
        fmat = b["known_filter_material"]
        fmm = float(b["known_filter_mm"])
        for physics in PHYSICS_MODES:
            for angle in ANGLES_DEG:
                record = {
                    "beam_id": beam,
                    "kvp": f"{kvp:g}",
                    "target_hvl_cu_mm": f"{target_hvl:.6f}",
                    "known_filter_material": fmat,
                    "known_filter_mm": f"{fmm:g}",
                    "physics": physics,
                    "anode_angle_deg": f"{angle:g}",
                    "spekpy_version": package_version("spekpy"),
                }
                try:
                    base = make_spectrum(kvp, physics, angle, fmat, fmm)
                    base_hvl = float(base.get_hvl1(matl="Cu", to="air"))
                    record["base_hvl_cu_mm"] = f"{base_hvl:.6f}"
                    record["base_minus_target_pct"] = f"{100*(base_hvl/target_hvl-1):+.3f}"
                    fit = fit_positive_al(base, target_hvl)
                    if fit is None:
                        record.update({
                            "status": "too_hard" if base_hvl > target_hvl else "no_positive_al_solution",
                            "fitted_eq_al_mm": "NA", "final_hvl_cu_mm": "NA",
                            "mean_energy_keV": "NA", "hvl2_cu_mm": "NA", "hc_cu": "NA",
                        })
                    else:
                        al, final_hvl = fit
                        final = clone(base)
                        if al > 0:
                            final.filter("Al", al)
                        record.update({
                            "status": "fit_possible",
                            "fitted_eq_al_mm": f"{al:.6f}",
                            "final_hvl_cu_mm": f"{final_hvl:.6f}",
                            "mean_energy_keV": f"{float(final.get_emean()):.6f}",
                            "hvl2_cu_mm": f"{float(final.get_hvl2(matl='Cu', to='air')):.6f}",
                            "hc_cu": f"{float(final.get_hc(matl='Cu', to='air')):.6f}",
                        })
                except Exception as e:
                    record.update({
                        "base_hvl_cu_mm": "NA", "base_minus_target_pct": "NA",
                        "status": "engine_error", "fitted_eq_al_mm": "NA",
                        "final_hvl_cu_mm": "NA", "mean_energy_keV": "NA",
                        "hvl2_cu_mm": "NA", "hc_cu": "NA", "error": repr(e),
                    })
                rows.append(record)

    fields = [
        "beam_id","kvp","target_hvl_cu_mm","known_filter_material","known_filter_mm",
        "physics","anode_angle_deg","spekpy_version","base_hvl_cu_mm",
        "base_minus_target_pct","status","fitted_eq_al_mm","final_hvl_cu_mm",
        "mean_energy_keV","hvl2_cu_mm","hc_cu","error",
    ]
    out = RESULTS / "stage1r_feasibility_scan.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    # Compact per-beam summary: closest base model and all fit-capable candidates.
    summary = RESULTS / "stage1r_feasibility_summary.txt"
    lines = []
    for beam in [b["beam_id"] for b in beams]:
        rr = [r for r in rows if r["beam_id"] == beam and r["base_hvl_cu_mm"] != "NA"]
        target = float(next(b["hvl_cu_mm"] for b in beams if b["beam_id"] == beam))
        rr_sorted = sorted(rr, key=lambda r: abs(float(r["base_hvl_cu_mm"])-target))
        fits = [r for r in rr if r["status"] == "fit_possible"]
        lines.append(f"[{beam}] target={target:.6f} mm Cu")
        if rr_sorted:
            r = rr_sorted[0]
            lines.append(
                f"closest base: {r['physics']} th={r['anode_angle_deg']} deg, "
                f"HVL={r['base_hvl_cu_mm']} mm, delta={r['base_minus_target_pct']}%"
            )
        lines.append(f"fit-capable candidates: {len(fits)} / {len(rr)}")
        for r in sorted(fits, key=lambda x: float(x["fitted_eq_al_mm"]))[:8]:
            lines.append(
                f"  {r['physics']} th={r['anode_angle_deg']} deg -> "
                f"eqAl={r['fitted_eq_al_mm']} mm, meanE={r['mean_energy_keV']} keV, HC={r['hc_cu']}"
            )
        lines.append("")
    summary.write_text("\n".join(lines))
    print(summary.read_text())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
