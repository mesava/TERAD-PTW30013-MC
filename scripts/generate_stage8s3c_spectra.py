#!/usr/bin/env python3
"""Generate Stage 8S3c TERAD hardware-spectrum sensitivity variants.

Stage 8S3c deliberately separates two different physical questions.

1) Be-window and anode-angle MODEL-FORM sensitivity:
   measured Cu HVL remains an experimental constraint, so the unknown
   non-negative residual equivalent-Al filtration is re-fitted for each
   hardware hypothesis. These variants probe spectral ambiguity at (nearly)
   the same measured beam quality.

2) kVp OPERATIONAL sensitivity:
   the nominal hardware model is calibrated first at the nominal kVp. Then
   kVp is changed by the manufacturer accuracy endpoints (+/-0.25%) while Be,
   clinical filtration and the fitted residual-Al thickness are held fixed.
   Re-fitting residual Al after changing kVp would artificially compensate the
   voltage error and is therefore intentionally NOT done.

The real TERAD anode angle is still unknown. 25 and 30 deg are model-form
probes that passed the Stage 8S3a non-negative-filtration feasibility screen;
they are not claimed to be uncertainty bounds or tube specifications.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import spekpy as sp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "beam_qualities.csv"
OUTDIR = ROOT / "stage8s3c_spectra"
SUMMARY = ROOT / "stage8s3c_spectrum_summary.csv"

PHYSICS = "kqp"
BIN_WIDTH_KEV = 0.5
TARGET = "W"
DISTANCE_CM = 100.0
MAS = 1.0
HVL_TOL_REL = 0.005
MAX_RESIDUAL_AL_MM = 100.0


@dataclass(frozen=True)
class Variant:
    name: str
    family: str
    mode: str
    be_mm: float
    angle_deg: float
    kvp_scale: float
    note: str


PRODUCTION_VARIANTS = [
    Variant("be0p7_a20_hvlfit", "be_window", "hvl_refit", 0.7, 20.0, 1.0,
            "Be low endpoint; residual Al re-fit to measured HVL"),
    Variant("be0p9_a20_hvlfit", "be_window", "hvl_refit", 0.9, 20.0, 1.0,
            "Be high endpoint; residual Al re-fit to measured HVL"),
    Variant("kvp_low_fixedfiltration", "kvp_accuracy", "fixed_nominal_filtration", 0.8, 20.0, 0.9975,
            "-0.25% kVp; Be/clinical/residual filtration fixed at nominal calibration"),
    Variant("kvp_high_fixedfiltration", "kvp_accuracy", "fixed_nominal_filtration", 0.8, 20.0, 1.0025,
            "+0.25% kVp; Be/clinical/residual filtration fixed at nominal calibration"),
    Variant("be0p8_a25_hvlfit", "anode_angle_model", "hvl_refit", 0.8, 25.0, 1.0,
            "25-deg model-form probe; not a TERAD specification"),
    Variant("be0p8_a30_hvlfit", "anode_angle_model", "hvl_refit", 0.8, 30.0, 1.0,
            "30-deg model-form probe; not a TERAD specification"),
]


def make_spectrum(kvp: float, angle: float, be_mm: float, known_mat: str, known_mm: float):
    s = sp.Spek(
        kvp=kvp, th=angle, dk=BIN_WIDTH_KEV, physics=PHYSICS, targ=TARGET,
        x=0.0, y=0.0, z=DISTANCE_CM, mas=MAS, brem=True, char=True,
    )
    if be_mm > 0:
        s.filter("Be", float(be_mm))
    if known_mm > 0:
        s.filter(known_mat, float(known_mm))
    return s


def clone(s):
    return sp.Spek.clone(s)


def hvl_cu(s) -> float:
    return float(s.get_hvl1(matl="Cu", to="air"))


def fit_nonnegative_residual_al(base, target_hvl: float) -> tuple[bool, float, float, str]:
    initial = hvl_cu(base)
    if initial > target_hvl * (1.0 + HVL_TOL_REL):
        return False, math.nan, initial, "base_harder_than_measured"
    if math.isclose(initial, target_hvl, rel_tol=HVL_TOL_REL, abs_tol=1e-8):
        return True, 0.0, initial, "within_hvl_tolerance_without_residual_Al"

    def f(t: float) -> float:
        s = clone(base)
        if t > 0:
            s.filter("Al", float(t))
        return hvl_cu(s) - target_hvl

    hi = 0.25
    while hi <= MAX_RESIDUAL_AL_MM and f(hi) < 0:
        hi *= 2.0
    if hi > MAX_RESIDUAL_AL_MM:
        return False, math.nan, initial, "could_not_bracket_with_nonnegative_residual_Al"
    fitted = float(brentq(f, 0.0, hi, xtol=1e-7, rtol=1e-10, maxiter=100))
    s = clone(base)
    if fitted > 0:
        s.filter("Al", fitted)
    return True, fitted, hvl_cu(s), "fit_nonnegative_residual_Al"


def arrays(s):
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(e) < 2 or len(e) != len(y) or np.any(~np.isfinite(e)) or np.any(~np.isfinite(y)) or np.any(y < 0):
        raise RuntimeError("Invalid SpekPy spectrum arrays")
    return e, y


def write_ensrc(path: Path, title: str, e: np.ndarray, y: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    diffs = np.diff(e)
    dk = float(np.median(diffs))
    if not np.allclose(diffs, dk, rtol=1e-6, atol=1e-9):
        raise RuntimeError("Non-uniform spectrum grid")
    lower = max(0.0, float(e[0] - dk / 2.0))
    upper = e + dk / 2.0
    density_per_mev = y * 1000.0
    widths_mev = np.diff(np.concatenate(([lower], upper))) / 1000.0
    integral = float(np.sum(density_per_mev * widths_mev))
    if not np.isfinite(integral) or integral <= 0:
        raise RuntimeError("Non-positive spectrum integral")
    density_per_mev /= integral
    with path.open("w") as f:
        f.write(title + "\n")
        f.write(f"{len(e)}, {lower / 1000.0:.10e}, 1\n")
        for edge, p in zip(upper, density_per_mev):
            f.write(f"{edge / 1000.0:.10e}, {p:.12e}\n")


def write_csv(path: Path, e: np.ndarray, y: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
        for ee, yy in zip(e, y):
            w.writerow([f"{ee:.8f}", f"{yy:.12e}"])


def nominal_residual(row: dict[str, str]) -> tuple[float, float]:
    kvp = float(row["kvp"])
    target_hvl = float(row["hvl_cu_mm"])
    base = make_spectrum(kvp, 20.0, 0.8, row["known_filter_material"], float(row["known_filter_mm"]))
    feasible, residual, final_hvl, status = fit_nonnegative_residual_al(base, target_hvl)
    if not feasible:
        raise RuntimeError(f"Nominal hardware candidate became infeasible for {row['beam_id']}: {status}")
    return residual, final_hvl


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    beam_rows = list(csv.DictReader(DATA.open()))
    summary: list[dict[str, object]] = []

    for row in beam_rows:
        beam = row["beam_id"]
        nominal_kvp = float(row["kvp"])
        target_hvl = float(row["hvl_cu_mm"])
        known_mat = row["known_filter_material"]
        known_mm = float(row["known_filter_mm"])
        nominal_al, nominal_hvl = nominal_residual(row)

        summary.append({
            "variant": "nominal_reference_hw_be0p8_a20",
            "family": "nominal_reference",
            "mode": "hvl_refit",
            "beam": beam,
            "nominal_kvp": nominal_kvp,
            "actual_kvp": nominal_kvp,
            "kvp_scale": 1.0,
            "anode_angle_deg": 20.0,
            "be_mm": 0.8,
            "known_filter_material": known_mat,
            "known_filter_mm": known_mm,
            "residual_equivalent_al_mm": nominal_al,
            "target_hvl1_cu_mm": target_hvl,
            "final_hvl1_cu_mm": nominal_hvl,
            "hvl_rel_error_pct": 100.0 * (nominal_hvl / target_hvl - 1.0),
            "feasible": 1,
            "note": "Stage 8S3b nominal spectrum reconstruction; transport baseline is reused, not recalculated",
            "spekpy_version": package_version("spekpy"),
        })

        for v in PRODUCTION_VARIANTS:
            actual_kvp = nominal_kvp * v.kvp_scale
            base = make_spectrum(actual_kvp, v.angle_deg, v.be_mm, known_mat, known_mm)
            feasible = True
            status = ""

            if v.mode == "hvl_refit":
                feasible, residual, final_hvl, status = fit_nonnegative_residual_al(base, target_hvl)
                final = clone(base)
                if feasible and residual > 0:
                    final.filter("Al", residual)
            elif v.mode == "fixed_nominal_filtration":
                residual = nominal_al
                final = clone(base)
                if residual > 0:
                    final.filter("Al", residual)
                final_hvl = hvl_cu(final)
                status = "nominal_residual_Al_held_fixed_no_refit"
            else:
                raise RuntimeError(f"Unknown mode {v.mode}")

            if not feasible:
                raise RuntimeError(f"Production variant infeasible: {v.name} {beam}: {status}")

            e, y = arrays(final)
            vdir = OUTDIR / v.name
            write_csv(vdir / f"{beam}.csv", e, y)
            write_ensrc(
                vdir / f"{beam}.ensrc",
                f"TERAD {beam} Stage8S3c {v.name}: Be={v.be_mm:g}mm, th={v.angle_deg:g}deg, kVp={actual_kvp:g}, mode={v.mode}",
                e, y,
            )

            hvl_err = 100.0 * (final_hvl / target_hvl - 1.0)
            if v.mode == "hvl_refit" and abs(hvl_err) > 100.0 * HVL_TOL_REL + 1e-6:
                raise RuntimeError(f"HVL-constrained variant missed gate: {v.name} {beam}: {hvl_err}%")

            summary.append({
                "variant": v.name,
                "family": v.family,
                "mode": v.mode,
                "beam": beam,
                "nominal_kvp": nominal_kvp,
                "actual_kvp": actual_kvp,
                "kvp_scale": v.kvp_scale,
                "anode_angle_deg": v.angle_deg,
                "be_mm": v.be_mm,
                "known_filter_material": known_mat,
                "known_filter_mm": known_mm,
                "residual_equivalent_al_mm": residual,
                "target_hvl1_cu_mm": target_hvl,
                "final_hvl1_cu_mm": final_hvl,
                "hvl_rel_error_pct": hvl_err,
                "feasible": 1,
                "note": v.note + "; " + status,
                "spekpy_version": package_version("spekpy"),
            })
            print(
                f"{v.name:28s} {beam}: kVp={actual_kvp:.4f}, Be={v.be_mm:.3f}, th={v.angle_deg:.1f}, "
                f"resAl={residual:.6f}, HVL={final_hvl:.6f} mmCu ({hvl_err:+.4f}%)"
            )

    fields = list(summary[0].keys())
    with SUMMARY.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary)

    expected = 4 * (1 + len(PRODUCTION_VARIANTS))
    if len(summary) != expected:
        raise RuntimeError(f"Summary row count {len(summary)} != {expected}")
    print(f"Wrote {SUMMARY} ({len(summary)} rows)")


if __name__ == "__main__":
    main()
