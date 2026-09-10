#!/usr/bin/env python3
"""Generate HVL-matched surrogate spectra for the Czarnecki 2020 PTW30013 benchmark.

The paper used SpekCalc with a W target, 30 deg anode angle and a 50 cm air gap.
Here we use SpekPy 2.5.4 with the same kVp, Cu filtration, 30 deg angle and
500 mm air attenuation. The Al thickness is allowed to vary slightly from the
published SpekCalc value so that the first Cu HVL matches the published beam
quality exactly. This isolates chamber/transport effects better than comparing
spectra with mismatched HVL.

The fitted Al thickness is a model parameter for this cross-code benchmark and
must not be interpreted as a correction to the published experiment.
"""
from __future__ import annotations

import csv
import math
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import spekpy as sp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "czarnecki2020_benchmark.csv"
OUTDIR = ROOT / "spectra" / "benchmark_czarnecki2020"
RESULTS = ROOT / "results"

ANODE_ANGLE_DEG = 30.0
PHYSICS = "kqp"
BIN_WIDTH_KEV = 0.5
DISTANCE_CM = 100.0
AIR_GAP_MM = 500.0
HVL_TOL_REL = 5e-4  # 0.05 % for generated benchmark spectra


def make_spectrum(kvp: float, al_mm: float, cu_mm: float):
    s = sp.Spek(
        kvp=kvp, th=ANODE_ANGLE_DEG, dk=BIN_WIDTH_KEV, physics=PHYSICS,
        targ="W", x=0.0, y=0.0, z=DISTANCE_CM, mas=1.0,
        brem=True, char=True,
    )
    # Czarnecki et al. included a 50 cm air gap behind the anode.
    s.filter("Air", AIR_GAP_MM)
    if al_mm > 0:
        s.filter("Al", float(al_mm))
    if cu_mm > 0:
        s.filter("Cu", float(cu_mm))
    return s


def hvl_for_al(kvp: float, al_mm: float, cu_mm: float) -> float:
    return float(make_spectrum(kvp, al_mm, cu_mm).get_hvl1(matl="Cu", to="air"))


def fit_al(kvp: float, published_al_mm: float, cu_mm: float, target_hvl: float) -> tuple[float, float]:
    initial = hvl_for_al(kvp, published_al_mm, cu_mm)
    if math.isclose(initial, target_hvl, rel_tol=HVL_TOL_REL, abs_tol=1e-8):
        return published_al_mm, initial

    # Search for total Al thickness that reproduces the published Cu HVL.
    lo, hi = 0.0, max(8.0, published_al_mm * 2.0)
    f_lo = hvl_for_al(kvp, lo, cu_mm) - target_hvl
    f_hi = hvl_for_al(kvp, hi, cu_mm) - target_hvl
    while f_lo * f_hi > 0 and hi < 100.0:
        hi *= 2.0
        f_hi = hvl_for_al(kvp, hi, cu_mm) - target_hvl
    if f_lo * f_hi > 0:
        raise RuntimeError(
            f"Cannot bracket target HVL={target_hvl:g} mm Cu at {kvp:g} kV; "
            f"HVL(Al=0)={f_lo+target_hvl:.6f}, HVL(Al={hi:g})={f_hi+target_hvl:.6f}"
        )
    fitted = float(brentq(lambda a: hvl_for_al(kvp, a, cu_mm) - target_hvl, lo, hi,
                           xtol=1e-8, rtol=1e-11, maxiter=100))
    return fitted, hvl_for_al(kvp, fitted, cu_mm)


def write_ensrc(path: Path, beam_id: str, s) -> tuple[float, int]:
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    de = float(np.median(np.diff(e)))
    if not np.allclose(np.diff(e), de, rtol=1e-6, atol=1e-9):
        raise RuntimeError(f"Non-uniform energy grid for {beam_id}")
    lower = max(0.0, float(e[0] - de/2.0))
    upper = e + de/2.0
    widths_mev = np.diff(np.concatenate(([lower], upper))) / 1000.0
    density_mev = y * 1000.0
    norm = float(np.sum(density_mev * widths_mev))
    density_mev /= norm
    with path.open("w") as f:
        f.write(
            f"Czarnecki2020 surrogate {beam_id}: SpekPy {package_version('spekpy')}, "
            f"W {ANODE_ANGLE_DEG:g}deg, {AIR_GAP_MM:g}mm Air, HVL-matched Al, published Cu\n"
        )
        f.write(f"{len(e)}, {lower/1000.0:.10e}, 1\n")
        for edge, p in zip(upper, density_mev):
            f.write(f"{edge/1000.0:.10e}, {p:.12e}\n")
    return float(s.get_emean()), len(e)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    summary = []
    for r in rows:
        bid = r["beam_id"]
        kvp = float(r["kvp"])
        al_pub = float(r["filter_al_mm"])
        cu = float(r["filter_cu_mm"])
        target = float(r["target_hvl_cu_mm"])
        initial = hvl_for_al(kvp, al_pub, cu)
        al_fit, final_hvl = fit_al(kvp, al_pub, cu, target)
        s = make_spectrum(kvp, al_fit, cu)
        rel = final_hvl/target - 1.0
        if abs(rel) > HVL_TOL_REL:
            raise RuntimeError(f"{bid}: HVL mismatch {100*rel:+.4f}%")
        mean_e, nbins = write_ensrc(OUTDIR / f"{bid}.ensrc", bid, s)
        e, y = s.get_spectrum(edges=False, flu=True, diff=True)
        with (OUTDIR / f"{bid}_spekpy.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
            for ee, yy in zip(e, y):
                w.writerow([f"{float(ee):.8f}", f"{float(yy):.12e}"])
        print(f"{bid}: target={target:.6f} mm Cu, published Al={al_pub:.6f} mm, "
              f"SpekPy initial={initial:.6f}, fitted Al={al_fit:.6f}, final={final_hvl:.6f}")
        summary.append({
            "beam_id": bid,
            "kvp": kvp,
            "published_al_mm": al_pub,
            "published_cu_mm": cu,
            "target_hvl_cu_mm": target,
            "spekpy_initial_hvl_cu_mm": initial,
            "fitted_al_mm": al_fit,
            "final_hvl_cu_mm": final_hvl,
            "relative_hvl_error_percent": 100*rel,
            "mean_energy_keV": mean_e,
            "nbins": nbins,
        })
    with (RESULTS / "czarnecki_spectrum_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader(); w.writerows(summary)


if __name__ == "__main__":
    main()
