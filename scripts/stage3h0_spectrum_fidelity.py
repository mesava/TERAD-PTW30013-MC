#!/usr/bin/env python3
"""Stage 3H-0: benchmark spectrum fidelity diagnostic.

Compare SpekPy surrogate families against *two* published Czarnecki 2020
beam-quality descriptors:
  1) Cu HVL
  2) kerma-weighted mean energy E_K, defined with water mu_en/rho.

The spectrum construction follows the Stage 3F convention: W target, 30 deg,
published filtration, 50 cm air included in the spectrum model, published Emin,
0.5 keV bins, z=100 cm. No HVL refit is performed.

E_K is evaluated without reaching into SpekPy internals. Because water kerma is
linear in fluence, for a spectrum Phi(E):
  K[Phi]       ~ integral E Phi(E) mu_en,w(E) dE
  K[E * Phi]   ~ integral E^2 Phi(E) mu_en,w(E) dE
therefore E_K = K[E*Phi] / K[Phi].
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import numpy as np
import spekpy as sp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "czarnecki2020_spectrum_parameters.csv"
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
        kvp=kvp,
        th=ANODE_ANGLE_DEG,
        dk=BIN_WIDTH_KEV,
        physics=cfg["physics"],
        targ="W",
        x=0.0,
        y=0.0,
        z=DISTANCE_CM,
        mas=1.0,
        brem=True,
        char=True,
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


def arrays_after_emin(s, emin_keV: float):
    e, y = s.get_spectrum(edges=False, flu=True, diff=True)
    e = np.asarray(e, dtype=float)
    y = np.asarray(y, dtype=float)
    keep = e >= float(emin_keV)
    e, y = e[keep], y[keep]
    if len(e) < 2 or not np.any(y > 0):
        raise RuntimeError("Empty spectrum after Emin truncation")
    return e, y


def external_spek(e: np.ndarray, y: np.ndarray):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
        p = Path(tf.name)
        np.savetxt(p, np.column_stack([e, y]), delimiter=",")
    try:
        return sp.Spek.load_from_file(
            str(p), ",", z=DISTANCE_CM, mas=1.0, mu_data_source="nist"
        )
    finally:
        p.unlink(missing_ok=True)


def water_kerma_weighted_mean_keV(e: np.ndarray, y: np.ndarray) -> float:
    base = external_spek(e, y)
    weighted = external_spek(e, y * e)
    k0 = float(base.get_kerma(to="water"))
    k1 = float(weighted.get_kerma(to="water"))
    if not (k0 > 0 and k1 > 0):
        raise RuntimeError(f"Invalid water kerma values K0={k0}, K1={k1}")
    return k1 / k0


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(DATA.open()))
    outrows = []

    for r in rows:
        beam = r["beam_id"]
        kvp = float(r["kvp"])
        emin = float(r["emin_keV"])
        al = float(r["filter_al_mm"])
        cu = float(r["filter_cu_mm"])
        hvl_pub = float(r["target_hvl_cu_mm"])
        ek_pub = float(r["published_kerma_mean_keV"])

        for mode in MODES:
            s = make_model(kvp, al, cu, mode)
            e, y = arrays_after_emin(s, emin)
            ext = external_spek(e, y)
            hvl = float(ext.get_hvl1(matl="Cu", to="air"))
            ek = water_kerma_weighted_mean_keV(e, y)
            emean = float(np.sum(e * y) / np.sum(y))

            row = {
                "beam_id": beam,
                "mode": mode,
                "kvp": f"{kvp:.6g}",
                "emin_keV": f"{emin:.6g}",
                "published_hvl_cu_mm": f"{hvl_pub:.6f}",
                "calculated_hvl_cu_mm": f"{hvl:.6f}",
                "hvl_error_percent": f"{100.0 * (hvl / hvl_pub - 1.0):+.4f}",
                "published_kerma_mean_keV": f"{ek_pub:.6f}",
                "calculated_kerma_mean_keV": f"{ek:.6f}",
                "kerma_mean_error_percent": f"{100.0 * (ek / ek_pub - 1.0):+.4f}",
                "fluence_mean_keV": f"{emean:.6f}",
                "nbins": str(len(e)),
            }
            outrows.append(row)
            print(
                f"{beam:7s} {mode:10s} "
                f"HVL={hvl:.6f} vs {hvl_pub:.6f} "
                f"({100*(hvl/hvl_pub-1):+.3f}%), "
                f"E_K={ek:.3f} vs {ek_pub:.3f} "
                f"({100*(ek/ek_pub-1):+.3f}%)"
            )

    out = RESULTS / "stage3h0_spectrum_fidelity.csv"
    fields = list(outrows[0].keys())
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(outrows)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
