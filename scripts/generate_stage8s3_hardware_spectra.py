#!/usr/bin/env python3
"""Stage 8S3a: hardware-informed TERAD spectrum feasibility screen.

This stage does NOT replace the accepted idealized Stage-1 spectra. It asks a
more constrained question: once known tube hardware is made explicit, can the
measured Cu HVL still be reproduced without unphysical negative filtration?

Hardware anchors supplied for the clinical tube:
- W target;
- Be exit window 0.8 +/- 0.1 mm;
- tube-voltage accuracy 0.25%;
- clinical added Al/Cu filters from data/beam_qualities.csv;
- physical anode angle remains unknown.

For every variant we apply, in this order:
    W SpekPy spectrum -> explicit Be -> known clinical Al/Cu filter
and only then fit a NON-NEGATIVE residual equivalent-Al thickness to the
measured Cu HVL. If the explicit-hardware spectrum is already harder than the
measured HVL, the variant is marked infeasible instead of using negative Al.

The anode-angle values in this screen are model-form probes, not TERAD specs.
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
OUTDIR = ROOT / "stage8s3_spectra"
RESULTS = ROOT / "stage8s3_spectrum_feasibility.csv"

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
    be_mm: float
    anode_angle_deg: float
    kvp_scale: float
    family: str
    note: str


# 20 deg is the existing idealized-model assumption, not a measured tube value.
# 10/15/25/30 deg are screening probes only; they are not uncertainty bounds.
VARIANTS = [
    Variant("hw_be0p8_a20", 0.8, 20.0, 1.0, "hardware_candidate", "explicit nominal Be; current nominal angle"),
    Variant("be0p7_a20", 0.7, 20.0, 1.0, "be_window", "manufacturer low Be endpoint"),
    Variant("be0p9_a20", 0.9, 20.0, 1.0, "be_window", "manufacturer high Be endpoint"),
    Variant("kvp_low_be0p8_a20", 0.8, 20.0, 0.9975, "kvp", "-0.25% tube-voltage endpoint"),
    Variant("kvp_high_be0p8_a20", 0.8, 20.0, 1.0025, "kvp", "+0.25% tube-voltage endpoint"),
    Variant("be0p8_a10", 0.8, 10.0, 1.0, "anode_angle", "model-form screening angle; not a TERAD specification"),
    Variant("be0p8_a15", 0.8, 15.0, 1.0, "anode_angle", "model-form screening angle; not a TERAD specification"),
    Variant("be0p8_a25", 0.8, 25.0, 1.0, "anode_angle", "model-form screening angle; not a TERAD specification"),
    Variant("be0p8_a30", 0.8, 30.0, 1.0, "anode_angle", "model-form screening angle; not a TERAD specification"),
]


def make_spectrum(kvp: float, angle: float, be_mm: float, known_mat: str, known_mm: float):
    s = sp.Spek(
        kvp=kvp,
        th=angle,
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
    if be_mm > 0:
        s.filter("Be", float(be_mm))
    if known_mm > 0:
        s.filter(known_mat, float(known_mm))
    return s


def clone(s):
    return sp.Spek.clone(s)


def hvl_cu(s) -> float:
    return float(s.get_hvl1(matl="Cu", to="air"))


def fit_residual_al(base, target_hvl: float) -> tuple[bool, float, float, str]:
    initial = hvl_cu(base)
    # A non-negative residual filter can only harden. Do not hide an
    # over-hard model behind negative equivalent filtration.
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


def spectrum_arrays(s):
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(e) < 2 or len(e) != len(y) or np.any(~np.isfinite(e)) or np.any(~np.isfinite(y)) or np.any(y < 0):
        raise RuntimeError("Invalid SpekPy spectrum arrays")
    return e, y


def write_csv(path: Path, e: np.ndarray, y: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
        for ee, yy in zip(e, y):
            w.writerow([f"{ee:.8f}", f"{yy:.12e}"])


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


def weighted_fraction_below(e: np.ndarray, y: np.ndarray, threshold_kev: float) -> float:
    den = float(np.trapz(y, e))
    if den <= 0:
        return math.nan
    mask = e < threshold_kev
    if np.count_nonzero(mask) < 2:
        return 0.0
    return float(np.trapz(y[mask], e[mask]) / den)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    summary: list[dict[str, object]] = []

    for v in VARIANTS:
        for row in rows:
            beam = row["beam_id"]
            nominal_kvp = float(row["kvp"])
            kvp = nominal_kvp * v.kvp_scale
            target_hvl = float(row["hvl_cu_mm"])
            known_mat = row["known_filter_material"]
            known_mm = float(row["known_filter_mm"])

            base = make_spectrum(kvp, v.anode_angle_deg, v.be_mm, known_mat, known_mm)
            base_hvl = hvl_cu(base)
            feasible, residual_al, final_hvl, status = fit_residual_al(base, target_hvl)

            final = clone(base)
            if feasible and residual_al > 0:
                final.filter("Al", residual_al)

            e, y = spectrum_arrays(final)
            variant_dir = OUTDIR / v.name
            write_csv(variant_dir / f"{beam}.csv", e, y)
            if feasible:
                write_ensrc(
                    variant_dir / f"{beam}.ensrc",
                    f"TERAD {beam} Stage8S3 {v.name}: W, Be={v.be_mm:g}mm, th={v.anode_angle_deg:g}deg, kvp={kvp:g}, residual-Al HVL fit",
                    e,
                    y,
                )

            emean = float(final.get_emean())
            hvl2 = float(final.get_hvl2(matl="Cu", to="air"))
            hc = float(final.get_hc(matl="Cu", to="air"))
            rel_err = (final_hvl / target_hvl - 1.0) * 100.0
            summary.append({
                "variant": v.name,
                "family": v.family,
                "note": v.note,
                "beam": beam,
                "nominal_kvp": nominal_kvp,
                "actual_kvp": kvp,
                "kvp_scale": v.kvp_scale,
                "anode_angle_deg": v.anode_angle_deg,
                "be_mm": v.be_mm,
                "known_filter_material": known_mat,
                "known_filter_mm": known_mm,
                "target_hvl1_cu_mm": target_hvl,
                "base_hvl1_cu_mm_after_Be_and_known_filter": base_hvl,
                "feasible_nonnegative_residual_al": int(feasible),
                "residual_equivalent_al_mm": residual_al,
                "final_hvl1_cu_mm": final_hvl,
                "final_hvl_rel_error_pct": rel_err,
                "hvl2_cu_mm": hvl2,
                "homogeneity_coefficient_cu": hc,
                "mean_energy_keV": emean,
                "fluence_fraction_below_20keV": weighted_fraction_below(e, y, 20.0),
                "fluence_fraction_below_30keV": weighted_fraction_below(e, y, 30.0),
                "fluence_fraction_below_50keV": weighted_fraction_below(e, y, 50.0),
                "status": status,
                "spekpy_version": package_version("spekpy"),
            })
            print(
                f"{v.name:24s} {beam}: kVp={kvp:.4f}, th={v.anode_angle_deg:g}, Be={v.be_mm:g} mm, "
                f"baseHVL={base_hvl:.6f}, target={target_hvl:.6f}, feasible={feasible}, "
                f"resAl={residual_al if feasible else float('nan'):.6f}, final={final_hvl:.6f}"
            )

    fields = list(summary[0].keys())
    with RESULTS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary)

    # A hard gate applies only to spectra that are labelled feasible.
    for r in summary:
        if int(r["feasible_nonnegative_residual_al"]):
            if abs(float(r["final_hvl_rel_error_pct"])) > 100.0 * HVL_TOL_REL + 1e-6:
                raise RuntimeError(f"Feasible spectrum missed HVL gate: {r['variant']} {r['beam']}")

    print(f"Wrote {RESULTS}")
    print(f"Wrote feasible EGSnrc spectra under {OUTDIR}/")


if __name__ == "__main__":
    main()
