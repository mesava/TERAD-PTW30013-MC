#!/usr/bin/env python3
"""Stage 3D spectrum sensitivity generator for the Czarnecki 2020 benchmark.

Generates three SpekPy 2.5.4 surrogate families:
  legacy          - Stage 3C behaviour: full spectrum, Al refit to published Cu HVL.
  published_emin  - published Al/Cu filtration and the paper's explicit Emin cut.
  emin_hvlfit     - explicit Emin cut, then Al refit to the published Cu HVL.

All families retain the paper's 30 deg W target and 50 cm air attenuation in the
spectrum model.  The additional 48 cm air transport from z=50 cm to the phantom
surface at z=98 cm is a GEOMETRY sensitivity handled by the Stage 3D workflow,
not folded into the spectrum here.
"""
from __future__ import annotations

import csv
import math
import tempfile
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import spekpy as sp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "czarnecki2020_spectrum_parameters.csv"
OUTROOT = ROOT / "spectra" / "benchmark_czarnecki2020_stage3d"
RESULTS = ROOT / "results"

ANODE_ANGLE_DEG = 30.0
PHYSICS = "kqp"
BIN_WIDTH_KEV = 0.5
DISTANCE_CM = 100.0
AIR_GAP_MM = 500.0
HVL_TOL_REL = 5e-4


def make_model(kvp: float, al_mm: float, cu_mm: float):
    s = sp.Spek(
        kvp=kvp,
        th=ANODE_ANGLE_DEG,
        dk=BIN_WIDTH_KEV,
        physics=PHYSICS,
        targ="W",
        x=0.0,
        y=0.0,
        z=DISTANCE_CM,
        mas=1.0,
        brem=True,
        char=True,
    )
    s.filter("Air", AIR_GAP_MM)
    if al_mm > 0:
        s.filter("Al", float(al_mm))
    if cu_mm > 0:
        s.filter("Cu", float(cu_mm))
    return s


def arrays(s, emin_keV: float | None = None):
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    if emin_keV is not None:
        keep = e >= float(emin_keV)
        e = e[keep]
        y = y[keep]
    if len(e) < 2 or not np.any(y > 0):
        raise RuntimeError("Empty/invalid spectrum after Emin truncation")
    return e, y


def external_spek(e: np.ndarray, y: np.ndarray):
    # SpekPy external spectra are two-column energy, differential fluence files.
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)
        np.savetxt(tf, np.column_stack([e, y]), delimiter=",")
    try:
        return sp.Spek.load_from_file(str(tmp), ",", z=DISTANCE_CM, mas=1.0, mu_data_source="nist")
    finally:
        tmp.unlink(missing_ok=True)


def truncated_hvl(kvp: float, al_mm: float, cu_mm: float, emin_keV: float) -> float:
    e, y = arrays(make_model(kvp, al_mm, cu_mm), emin_keV)
    ext = external_spek(e, y)
    return float(ext.get_hvl1(matl="Cu", to="air"))


def full_hvl(kvp: float, al_mm: float, cu_mm: float) -> float:
    return float(make_model(kvp, al_mm, cu_mm).get_hvl1(matl="Cu", to="air"))


def fit_al_full(kvp: float, al0: float, cu_mm: float, target: float) -> tuple[float, float]:
    initial = full_hvl(kvp, al0, cu_mm)
    if math.isclose(initial, target, rel_tol=HVL_TOL_REL, abs_tol=1e-8):
        return al0, initial
    lo, hi = 0.0, max(8.0, 2.0 * al0)
    f = lambda a: full_hvl(kvp, a, cu_mm) - target
    while f(lo) * f(hi) > 0 and hi < 100.0:
        hi *= 2.0
    if f(lo) * f(hi) > 0:
        raise RuntimeError(f"Cannot bracket full-spectrum HVL target for {kvp:g} kV")
    fitted = float(brentq(f, lo, hi, xtol=1e-8, rtol=1e-11, maxiter=100))
    return fitted, full_hvl(kvp, fitted, cu_mm)


def fit_al_emin(kvp: float, al0: float, cu_mm: float, emin_keV: float, target: float) -> tuple[float, float]:
    initial = truncated_hvl(kvp, al0, cu_mm, emin_keV)
    if math.isclose(initial, target, rel_tol=HVL_TOL_REL, abs_tol=1e-8):
        return al0, initial
    lo, hi = 0.0, max(8.0, 2.0 * al0)
    f = lambda a: truncated_hvl(kvp, a, cu_mm, emin_keV) - target
    flo, fhi = f(lo), f(hi)
    while flo * fhi > 0 and hi < 100.0:
        hi *= 2.0
        fhi = f(hi)
    if flo * fhi > 0:
        raise RuntimeError(
            f"Cannot bracket Emin-truncated HVL={target:g} mm Cu at {kvp:g} kV; "
            f"HVL(Al=0)={flo+target:.6f}, HVL(Al={hi:g})={fhi+target:.6f}"
        )
    fitted = float(brentq(f, lo, hi, xtol=1e-8, rtol=1e-11, maxiter=100))
    return fitted, truncated_hvl(kvp, fitted, cu_mm, emin_keV)


def write_ensrc(path: Path, beam: str, mode: str, e: np.ndarray, y: np.ndarray) -> int:
    de = float(np.median(np.diff(e)))
    if not np.allclose(np.diff(e), de, rtol=1e-6, atol=1e-9):
        raise RuntimeError(f"{beam}/{mode}: non-uniform energy grid")
    lower = max(0.0, float(e[0] - de / 2.0))
    upper = e + de / 2.0
    widths_mev = np.diff(np.concatenate(([lower], upper))) / 1000.0
    density_mev = y * 1000.0
    norm = float(np.sum(density_mev * widths_mev))
    density_mev /= norm
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            f"Czarnecki2020 Stage3D {beam}/{mode}: SpekPy {package_version('spekpy')}, "
            f"W {ANODE_ANGLE_DEG:g}deg, first {AIR_GAP_MM:g}mm Air in spectrum model\n"
        )
        f.write(f"{len(e)}, {lower/1000.0:.10e}, 1\n")
        for edge, p in zip(upper, density_mev):
            f.write(f"{edge/1000.0:.10e}, {p:.12e}\n")
    return len(e)


def write_csv(path: Path, e: np.ndarray, y: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
        for ee, yy in zip(e, y):
            w.writerow([f"{float(ee):.8f}", f"{float(yy):.12e}"])


def mean_energy(e: np.ndarray, y: np.ndarray) -> float:
    return float(np.sum(e * y) / np.sum(y))


def main() -> None:
    OUTROOT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    summary: list[dict[str, object]] = []

    for r in rows:
        beam = r["beam_id"]
        kvp = float(r["kvp"])
        emin = float(r["emin_keV"])
        al_pub = float(r["filter_al_mm"])
        cu = float(r["filter_cu_mm"])
        target = float(r["target_hvl_cu_mm"])
        ek_pub = float(r["published_kerma_mean_keV"])

        # 1) Exact Stage 3C spectral construction.
        al_legacy, hvl_legacy = fit_al_full(kvp, al_pub, cu, target)
        s = make_model(kvp, al_legacy, cu)
        e, y = arrays(s, None)
        modes = [("legacy", al_legacy, hvl_legacy, e, y)]

        # 2) Paper filtration + explicit paper Emin, no cross-code HVL refit.
        s_pub = make_model(kvp, al_pub, cu)
        e_pub, y_pub = arrays(s_pub, emin)
        hvl_pub = float(external_spek(e_pub, y_pub).get_hvl1(matl="Cu", to="air"))
        modes.append(("published_emin", al_pub, hvl_pub, e_pub, y_pub))

        # 3) Paper Emin retained, but Al is refit so SpekPy exactly matches paper HVL.
        al_fit, hvl_fit = fit_al_emin(kvp, al_pub, cu, emin, target)
        s_fit = make_model(kvp, al_fit, cu)
        e_fit, y_fit = arrays(s_fit, emin)
        modes.append(("emin_hvlfit", al_fit, hvl_fit, e_fit, y_fit))

        for mode, al_used, hvl, ee, yy in modes:
            outdir = OUTROOT / mode
            nbins = write_ensrc(outdir / f"{beam}.ensrc", beam, mode, ee, yy)
            write_csv(outdir / f"{beam}_spekpy.csv", ee, yy)
            rel = 100.0 * (hvl / target - 1.0)
            emean = mean_energy(ee, yy)
            print(
                f"{beam}/{mode}: Emin={ee[0]-BIN_WIDTH_KEV/2:.3f} keV, "
                f"Al={al_used:.6f} mm, Cu={cu:.6f} mm, HVL={hvl:.6f} mm Cu "
                f"({rel:+.3f}% vs target), fluence-mean E={emean:.3f} keV"
            )
            summary.append({
                "beam_id": beam,
                "mode": mode,
                "kvp": kvp,
                "paper_emin_keV": emin,
                "effective_lower_edge_keV": float(ee[0] - BIN_WIDTH_KEV / 2.0),
                "published_al_mm": al_pub,
                "al_used_mm": al_used,
                "cu_used_mm": cu,
                "target_hvl_cu_mm": target,
                "calculated_hvl_cu_mm": hvl,
                "hvl_error_percent": rel,
                "published_kerma_mean_keV": ek_pub,
                "fluence_mean_energy_keV": emean,
                "nbins": nbins,
            })

    out = RESULTS / "czarnecki_stage3d_spectrum_summary.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)


if __name__ == "__main__":
    main()
