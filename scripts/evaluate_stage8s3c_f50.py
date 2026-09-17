#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path

BEAMS = ("Q120", "Q140", "Q150", "Q200")
VARIANTS = (
    "be0p7_a20_hvlfit",
    "be0p9_a20_hvlfit",
    "kvp_low_fixedfiltration",
    "kvp_high_fixedfiltration",
    "be0p8_a25_hvlfit",
    "be0p8_a30_hvlfit",
)
FAMILY = {
    "be0p7_a20_hvlfit": "be_window",
    "be0p9_a20_hvlfit": "be_window",
    "kvp_low_fixedfiltration": "kvp_accuracy",
    "kvp_high_fixedfiltration": "kvp_accuracy",
    "be0p8_a25_hvlfit": "anode_angle_model",
    "be0p8_a30_hvlfit": "anode_angle_model",
}


def read_single_rows(pattern: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in glob.glob(pattern):
        with open(p, newline="") as f:
            rr = list(csv.DictReader(f))
        if len(rr) != 1:
            raise SystemExit(f"Expected one row in {p}, found {len(rr)}")
        rows.append(rr[0])
    return rows


def weighted_rco(path: str) -> tuple[float, float]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    r = next((x for x in rows if x["estimate"] == "weighted"), None)
    if r is None:
        raise SystemExit("Missing weighted R_Co row")
    return float(r["R_Co"]), float(r["u_pct"])


def nominal_finite(path: str) -> dict[str, dict[str, float]]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        if r["source_model"] == "finite_7p5mm" and r["spectrum_variant"] == "hw_be0p8_a20":
            out[r["beam"]] = {
                "K": float(r["K_Qg_Co_RW3_to_water"]),
                "R": float(r["R_direct_RW3_to_water"]),
                "u_R_pct": float(r["u_R_direct_pct"]),
                "u_K_pct": float(r["u_K_pct"]),
            }
    if set(out) != set(BEAMS):
        raise SystemExit(f"Incomplete Stage 8S3b finite-source baseline: {sorted(out)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--points-glob", required=True)
    ap.add_argument("--rco", required=True)
    ap.add_argument("--nominal", required=True)
    ap.add_argument("--spectrum-summary", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--gate-output", required=True)
    args = ap.parse_args()

    points = read_single_rows(args.points_glob)
    idx = {(r["spectrum_variant"], r["beam"], r["medium"]): r for r in points}
    expected = {(v, b, m) for v in VARIANTS for b in BEAMS for m in ("water", "rw3")}
    if set(idx) != expected or len(points) != 48:
        missing = sorted(expected - set(idx))
        extra = sorted(set(idx) - expected)
        raise SystemExit(f"Point matrix mismatch n={len(points)} missing={missing} extra={extra}")

    with open(args.spectrum_summary, newline="") as f:
        spec_rows = list(csv.DictReader(f))
    spec = {(r["variant"], r["beam"]): r for r in spec_rows}

    rco, u_rco_pct = weighted_rco(args.rco)
    nominal = nominal_finite(args.nominal)
    out_rows: list[dict[str, object]] = []

    for v in VARIANTS:
        for b in BEAMS:
            w = idx[(v, b, "water")]
            r = idx[(v, b, "rw3")]
            if w["source_model"] != "finite_7p5mm" or r["source_model"] != "finite_7p5mm":
                raise SystemExit(f"Unexpected source model for {v}/{b}")
            dw = float(w["D_water_per_history"])
            u_dw = float(w["u_D_pct"])
            dcav = float(r["Dcav_RW3_per_history"])
            u_dcav = float(r["u_Dcav_pct"])
            if dw <= 0 or dcav <= 0:
                raise SystemExit(f"Non-positive score for {v}/{b}")
            rd = dw / dcav
            u_rd_pct = math.hypot(u_dw, u_dcav)
            k = rd / rco
            u_k_pct = math.hypot(u_rd_pct, u_rco_pct)
            nom = nominal[b]
            delta = 100.0 * (k / nom["K"] - 1.0)
            # R_Co is common and cancels in the variant/nominal ratio. The
            # uncertainty below is therefore based on the two independent
            # direct-transfer MC estimates only.
            u_ratio_pct = math.hypot(u_rd_pct, nom["u_R_pct"])
            sr = spec.get((v, b))
            if sr is None:
                raise SystemExit(f"Missing spectrum metadata for {v}/{b}")
            out_rows.append({
                "variant": v,
                "family": FAMILY[v],
                "beam": b,
                "geometry": "F50_8x10_SSD50",
                "source_model": "finite_7p5mm",
                "spectrum_mode": sr["mode"],
                "actual_kvp": sr["actual_kvp"],
                "be_mm": sr["be_mm"],
                "anode_angle_deg": sr["anode_angle_deg"],
                "residual_equivalent_al_mm": sr["residual_equivalent_al_mm"],
                "final_hvl1_cu_mm": sr["final_hvl1_cu_mm"],
                "hvl_rel_error_pct": sr["hvl_rel_error_pct"],
                "Dw_water_per_history": dw,
                "u_Dw_water_pct": u_dw,
                "Dcav_RW3_per_history": dcav,
                "u_Dcav_RW3_pct": u_dcav,
                "R_direct_RW3_to_water": rd,
                "u_R_direct_pct": u_rd_pct,
                "R_Co": rco,
                "K_Qg_Co_RW3_to_water": k,
                "u_K_pct": u_k_pct,
                "K_nominal_stage8s3b_finite": nom["K"],
                "delta_K_vs_nominal_finite_pct": delta,
                "u_variant_to_nominal_ratio_pct": u_ratio_pct,
                "precision_gate": str(u_rd_pct <= 1.0).lower(),
            })

    with Path(args.output).open("w", newline="") as f:
        fields = list(out_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    max_u = max(float(r["u_R_direct_pct"]) for r in out_rows)
    max_abs = max(abs(float(r["delta_K_vs_nominal_finite_pct"])) for r in out_rows)
    gate = len(out_rows) == 24 and max_u <= 1.0

    family_stats = {}
    for fam in ("be_window", "kvp_accuracy", "anode_angle_model"):
        vals = [float(r["delta_K_vs_nominal_finite_pct"]) for r in out_rows if r["family"] == fam]
        family_stats[fam] = (min(vals), max(vals), max(abs(x) for x in vals))

    lines = [
        f"gate_pass={str(gate).lower()}",
        f"k_rows={len(out_rows)}/24",
        f"transport_points={len(points)}/48",
        f"max_u_R_direct_pct={max_u:.6f}",
        f"max_abs_delta_K_vs_nominal_finite_pct={max_abs:.6f}",
        "source_model=finite_7p5mm",
        "geometry=F50_8x10_SSD50",
        "nominal_reference=Stage8S3b hw_be0p8_a20 finite_7p5mm",
    ]
    for fam, (lo, hi, ma) in family_stats.items():
        lines += [
            f"{fam}_min_shift_pct={lo:.6f}",
            f"{fam}_max_shift_pct={hi:.6f}",
            f"{fam}_max_abs_shift_pct={ma:.6f}",
        ]
    lines += [
        "note_be=HVL-constrained model-form endpoints; no probability distribution assigned",
        "note_kvp=+/-0.25% operational endpoints with nominal filtration held fixed; no residual-Al refit",
        "note_angle=25/30-deg model-form probes only; not TERAD specifications or formal uncertainty bounds",
    ]
    text = "\n".join(lines) + "\n"
    Path(args.gate_output).write_text(text)
    print(text, end="")
    if not gate:
        raise SystemExit("Stage 8S3c precision/completeness gate failed")


if __name__ == "__main__":
    main()
