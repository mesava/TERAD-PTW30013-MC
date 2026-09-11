#!/usr/bin/env python3
"""Stage 3F spectrum-model sensitivity for the Czarnecki 2020 benchmark.

The published benchmark spectra were generated with SpekCalc. Stage 3E showed
that using the paper filtration and explicit Emin cut improves agreement, but
our surrogate was still generated with the SpekPy-v2 kqp model.

This script generates otherwise identical published-filtration/Emin spectra
with three SpekPy 2.5.4 physics models:
  - kqp        : current Stage 3E surrogate baseline
  - spekcalc   : legacy SpekCalc-compatible model; highest-priority test
  - spekpy-v1  : older SpekPy model, used as an additional spectral-shape test

No HVL refit is performed in Stage 3F. The point is to isolate the spectrum
engine/shape while retaining the paper's nominal filtration and Emin.
"""
from __future__ import annotations

import csv
import tempfile
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import spekpy as sp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "czarnecki2020_spectrum_parameters.csv"
OUTROOT = ROOT / "spectra" / "benchmark_czarnecki2020_stage3f"
RESULTS = ROOT / "results"

ANODE_ANGLE_DEG = 30.0
BIN_WIDTH_KEV = 0.5
DISTANCE_CM = 100.0
AIR_GAP_MM = 500.0
MODES = {
    "kqp": {"physics": "kqp", "mu_data_source": None},
    "spekcalc": {"physics": "spekcalc", "mu_data_source": "nist"},
    "spekpy_v1": {"physics": "spekpy-v1", "mu_data_source": "nist"},
}


def make_model(kvp: float, al_mm: float, cu_mm: float, mode: str):
    cfg = MODES[mode]
    kwargs = dict(
        kvp=kvp, th=ANODE_ANGLE_DEG, dk=BIN_WIDTH_KEV,
        physics=cfg["physics"], targ="W", x=0.0, y=0.0,
        z=DISTANCE_CM, mas=1.0, brem=True, char=True,
    )
    if cfg["mu_data_source"] is not None:
        kwargs["mu_data_source"] = cfg["mu_data_source"]
    s = sp.Spek(**kwargs)
    s.filter("Air", AIR_GAP_MM)
    if al_mm > 0:
        s.filter("Al", float(al_mm))
    if cu_mm > 0:
        s.filter("Cu", float(cu_mm))
    return s


def arrays(s, emin_keV: float):
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    keep = e >= float(emin_keV)
    e, y = e[keep], y[keep]
    if len(e) < 2 or not np.any(y > 0):
        raise RuntimeError("Empty/invalid spectrum after Emin truncation")
    return e, y


def external_spek(e: np.ndarray, y: np.ndarray):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)
        np.savetxt(tf, np.column_stack([e, y]), delimiter=",")
    try:
        return sp.Spek.load_from_file(
            str(tmp), ",", z=DISTANCE_CM, mas=1.0, mu_data_source="nist"
        )
    finally:
        tmp.unlink(missing_ok=True)


def write_ensrc(path: Path, beam: str, mode: str, e: np.ndarray, y: np.ndarray):
    de = float(np.median(np.diff(e)))
    if not np.allclose(np.diff(e), de, rtol=1e-6, atol=1e-9):
        raise RuntimeError(f"{beam}/{mode}: non-uniform energy grid")
    lower = max(0.0, float(e[0] - de / 2.0))
    upper = e + de / 2.0
    widths_mev = np.diff(np.concatenate(([lower], upper))) / 1000.0
    density_mev = y * 1000.0
    density_mev /= float(np.sum(density_mev * widths_mev))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            f"Czarnecki2020 Stage3F {beam}/{mode}: SpekPy {package_version('spekpy')}, "
            f"W {ANODE_ANGLE_DEG:g}deg, first {AIR_GAP_MM:g}mm Air, published filters/Emin\n"
        )
        f.write(f"{len(e)}, {lower/1000.0:.10e}, 1\n")
        for edge, p in zip(upper, density_mev):
            f.write(f"{edge/1000.0:.10e}, {p:.12e}\n")


def mean_energy(e: np.ndarray, y: np.ndarray) -> float:
    return float(np.sum(e * y) / np.sum(y))


def main() -> None:
    OUTROOT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    summary = []

    for r in rows:
        beam = r["beam_id"]
        if beam not in {"CCRI100", "CCRI250"}:
            continue
        kvp = float(r["kvp"])
        emin = float(r["emin_keV"])
        al = float(r["filter_al_mm"])
        cu = float(r["filter_cu_mm"])
        target_hvl = float(r["target_hvl_cu_mm"])
        published_mean = float(r["published_kerma_mean_keV"])

        for mode in MODES:
            s = make_model(kvp, al, cu, mode)
            e, y = arrays(s, emin)
            ext = external_spek(e, y)
            hvl = float(ext.get_hvl1(matl="Cu", to="air"))
            emean = mean_energy(e, y)
            outdir = OUTROOT / mode
            write_ensrc(outdir / f"{beam}.ensrc", beam, mode, e, y)
            with (outdir / f"{beam}_spekpy.csv").open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["energy_keV_midbin", "fluence_ph_cm-2_keV-1"])
                for ee, yy in zip(e, y):
                    w.writerow([f"{float(ee):.8f}", f"{float(yy):.12e}"])
            summary.append({
                "beam_id": beam,
                "mode": mode,
                "physics": MODES[mode]["physics"],
                "kvp": kvp,
                "emin_keV": emin,
                "al_mm": al,
                "cu_mm": cu,
                "target_hvl_cu_mm": target_hvl,
                "calculated_hvl_cu_mm": hvl,
                "hvl_error_percent": 100.0 * (hvl / target_hvl - 1.0),
                "published_kerma_mean_keV": published_mean,
                "fluence_mean_energy_keV": emean,
                "nbins": len(e),
            })
            print(
                f"{beam}/{mode}: Emin={emin:g} keV, Al={al:g} mm, Cu={cu:g} mm, "
                f"HVL={hvl:.6f} mm Cu ({100*(hvl/target_hvl-1):+.3f}%), "
                f"fluence-mean E={emean:.3f} keV"
            )

    out = RESULTS / "czarnecki_stage3f_spectrum_summary.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader(); w.writerows(summary)


if __name__ == "__main__":
    main()
