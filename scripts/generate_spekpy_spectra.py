#!/usr/bin/env python3
"""Generate first-pass TERAD spectra with SpekPy and match measured Cu HVL.

Scientific intent
-----------------
This is a *beam-spectrum model*, not a claim about the physical inherent
filtration of the TERAD tube. For each measured beam quality, a tungsten
reflection-target spectrum is generated with a nominal 20 degree anode angle
and SpekPy's kqp physics model. The known added filtration is applied first.
An additional equivalent-Al thickness is then fitted so that the calculated
first HVL in copper matches the measured HVL.

The fitted Al thickness is therefore a nuisance/model parameter that absorbs
unknown inherent filtration/window/tube-head effects in this first-pass model.
It must not be interpreted as a measured physical Al thickness.
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
DATA = ROOT / "data" / "beam_qualities.csv"
SPECTRA_DIR = ROOT / "spectra"
RESULTS_DIR = ROOT / "results"

ANODE_ANGLE_DEG = 20.0          # nominal first-pass value, not a TERAD specification
PHYSICS = "kqp"
BIN_WIDTH_KEV = 0.5
TARGET = "W"
DISTANCE_CM = 100.0
MAS = 1.0
HVL_TOL_REL = 0.005             # 0.5 % acceptance for the generated spectrum
MAX_EQ_AL_MM = 100.0


def make_base_spectrum(kvp: float, known_mat: str, known_mm: float):
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
    if known_mm > 0:
        s.filter(known_mat, known_mm)
    return s


def hvl_cu_with_extra_al(base, extra_al_mm: float) -> float:
    s = base.clone()
    if extra_al_mm > 0:
        s.filter("Al", float(extra_al_mm))
    return float(s.get_hvl1(matl="Cu", to="air"))


def fit_extra_al(base, target_hvl_cu_mm: float) -> tuple[float, float]:
    initial = hvl_cu_with_extra_al(base, 0.0)
    if initial > target_hvl_cu_mm * (1.0 + HVL_TOL_REL):
        raise RuntimeError(
            f"Known-filter model is already harder than measured beam: "
            f"initial Cu HVL={initial:.6f} mm, target={target_hvl_cu_mm:.6f} mm. "
            "Positive equivalent-Al filtration cannot soften the spectrum."
        )

    if math.isclose(initial, target_hvl_cu_mm, rel_tol=HVL_TOL_REL, abs_tol=1e-8):
        return 0.0, initial

    def f(t: float) -> float:
        return hvl_cu_with_extra_al(base, t) - target_hvl_cu_mm

    hi = 0.25
    while hi <= MAX_EQ_AL_MM and f(hi) < 0:
        hi *= 2.0
    if hi > MAX_EQ_AL_MM:
        raise RuntimeError(
            f"Could not bracket the measured Cu HVL={target_hvl_cu_mm:.6f} mm "
            f"with <= {MAX_EQ_AL_MM:g} mm equivalent Al."
        )

    fitted = float(brentq(f, 0.0, hi, xtol=1e-7, rtol=1e-10, maxiter=100))
    return fitted, hvl_cu_with_extra_al(base, fitted)


def write_csv_spectrum(path: Path, beam_id: str, s) -> tuple[np.ndarray, np.ndarray]:
    energy_kev, fluence_per_kev = s.get_spectrum(edges=False, flu=True, diff=True)
    energy_kev = np.asarray(energy_kev, dtype=float)
    fluence_per_kev = np.asarray(fluence_per_kev, dtype=float)

    if energy_kev.ndim != 1 or fluence_per_kev.ndim != 1 or len(energy_kev) != len(fluence_per_kev):
        raise RuntimeError(f"Unexpected SpekPy spectrum arrays for {beam_id}")
    if len(energy_kev) < 2 or np.any(~np.isfinite(energy_kev)) or np.any(~np.isfinite(fluence_per_kev)):
        raise RuntimeError(f"Invalid spectrum values for {beam_id}")
    if np.any(fluence_per_kev < 0):
        raise RuntimeError(f"Negative spectral fluence encountered for {beam_id}")

    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
        for e, y in zip(energy_kev, fluence_per_kev):
            w.writerow([f"{e:.8f}", f"{y:.12e}"])

    return energy_kev, fluence_per_kev


def write_egsnrc_ensrc(path: Path, beam_id: str, energy_kev: np.ndarray, fluence_per_kev: np.ndarray) -> None:
    """Write an EGSnrc histogram spectrum file using MODE=1 (counts/MeV).

    EGSnrc file convention:
      title
      NENSRC, ENMIN, MODE
      upper_edge_1(MeV), probability_density_1(/MeV)
      ...

    SpekPy returns mid-bin energies and differential fluence /keV. We infer
    bin edges from the uniform grid, convert density to /MeV, and normalize
    the histogram integral to unity. Absolute normalization is irrelevant for
    the kQ dose-ratio calculation.
    """
    diffs = np.diff(energy_kev)
    dk = float(np.median(diffs))
    if not np.allclose(diffs, dk, rtol=1e-6, atol=1e-9):
        raise RuntimeError(f"Non-uniform SpekPy energy grid for {beam_id}")

    lower_edge_kev = float(energy_kev[0] - dk / 2.0)
    upper_edges_kev = energy_kev + dk / 2.0
    if lower_edge_kev < -1e-9:
        raise RuntimeError(f"Negative inferred lower energy edge for {beam_id}")
    lower_edge_kev = max(0.0, lower_edge_kev)

    # Convert photons/(cm2 keV) -> proportional density per MeV.
    density_per_mev = fluence_per_kev * 1000.0
    widths_mev = np.diff(np.concatenate(([lower_edge_kev], upper_edges_kev))) / 1000.0
    integral = float(np.sum(density_per_mev * widths_mev))
    if not np.isfinite(integral) or integral <= 0:
        raise RuntimeError(f"Non-positive spectrum integral for {beam_id}")
    density_per_mev = density_per_mev / integral

    with path.open("w") as f:
        f.write(
            f"TERAD {beam_id}: SpekPy {package_version('spekpy')}, W target, "
            f"{ANODE_ANGLE_DEG:g} deg nominal, {PHYSICS}, HVL-fitted equivalent Al\n"
        )
        f.write(f"{len(energy_kev)}, {lower_edge_kev / 1000.0:.10e}, 1\n")
        for edge_kev, p in zip(upper_edges_kev, density_per_mev):
            f.write(f"{edge_kev / 1000.0:.10e}, {p:.12e}\n")


def main() -> None:
    SPECTRA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(DATA.open()))
    summary = []

    for row in rows:
        beam_id = row["beam_id"]
        kvp = float(row["kvp"])
        target_hvl = float(row["hvl_cu_mm"])
        known_mat = row["known_filter_material"]
        known_mm = float(row["known_filter_mm"])

        print(f"\n=== {beam_id}: {kvp:g} kV, target HVL={target_hvl:g} mm Cu ===")
        base = make_base_spectrum(kvp, known_mat, known_mm)
        initial_hvl = float(base.get_hvl1(matl="Cu", to="air"))
        extra_al, fitted_hvl = fit_extra_al(base, target_hvl)

        final = base.clone()
        if extra_al > 0:
            final.filter("Al", extra_al)

        hvl1_cu = float(final.get_hvl1(matl="Cu", to="air"))
        hvl2_cu = float(final.get_hvl2(matl="Cu", to="air"))
        hc_cu = float(final.get_hc(matl="Cu", to="air"))
        emean = float(final.get_emean())
        eeff_cu = float(final.get_eeff(matl="Cu", to="air"))
        rel_err = (hvl1_cu / target_hvl - 1.0)

        print(f"Initial Cu HVL       : {initial_hvl:.6f} mm")
        print(f"Equivalent Al fitted : {extra_al:.6f} mm")
        print(f"Final Cu HVL         : {hvl1_cu:.6f} mm")
        print(f"Relative HVL error   : {100.0 * rel_err:+.5f} %")
        print(f"Mean energy          : {emean:.4f} keV")

        if abs(rel_err) > HVL_TOL_REL:
            raise RuntimeError(
                f"{beam_id} HVL mismatch {100*rel_err:+.3f}% exceeds {100*HVL_TOL_REL:.2f}%"
            )

        energy, fluence = write_csv_spectrum(SPECTRA_DIR / f"{beam_id}_spekpy.csv", beam_id, final)
        write_egsnrc_ensrc(SPECTRA_DIR / f"{beam_id}.ensrc", beam_id, energy, fluence)

        summary.append({
            "beam_id": beam_id,
            "kvp": f"{kvp:g}",
            "spekpy_version": package_version("spekpy"),
            "target": TARGET,
            "anode_angle_deg_nominal": f"{ANODE_ANGLE_DEG:g}",
            "physics": PHYSICS,
            "bin_width_keV": f"{BIN_WIDTH_KEV:g}",
            "known_filter_material": known_mat,
            "known_filter_mm": f"{known_mm:g}",
            "target_hvl1_cu_mm": f"{target_hvl:.6f}",
            "initial_hvl1_cu_mm": f"{initial_hvl:.6f}",
            "fitted_equivalent_al_mm": f"{extra_al:.6f}",
            "final_hvl1_cu_mm": f"{hvl1_cu:.6f}",
            "relative_hvl_error_percent": f"{100.0 * rel_err:.6f}",
            "hvl2_cu_mm": f"{hvl2_cu:.6f}",
            "homogeneity_coefficient_cu": f"{hc_cu:.6f}",
            "mean_energy_keV": f"{emean:.6f}",
            "effective_energy_cu_keV": f"{eeff_cu:.6f}",
        })

    fieldnames = list(summary[0].keys())
    summary_path = RESULTS_DIR / "spekpy_fit_summary.csv"
    with summary_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(summary)

    print(f"\nWrote {summary_path}")
    print(f"Wrote {len(summary)} EGSnrc spectra to {SPECTRA_DIR}")


if __name__ == "__main__":
    main()
