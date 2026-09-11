#!/usr/bin/env python3
"""Stage 1R-2: tube-informed TERAD spectrum audit.

Use the TERAD-200 hardware constraints (W anode, Be exit window 0.8 +/- 0.1 mm)
and a 30-degree target-angle candidate consistent with common 225-kV tubes whose
published specifications match the TERAD tube envelope (NDI-226 / MXR-226).

This is diagnostic only. The known clinical removable filter is held fixed.
No equivalent filtration is fitted and measured HVLs are never altered.
"""
from __future__ import annotations

import csv
from importlib.metadata import version as package_version
from pathlib import Path

import spekpy as sp

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "terad_input_baseline.csv"
RESULTS = ROOT / "results"
PHYSICS_MODES = ("kqp", "spekcalc", "spekpy-v1")
BE_WINDOWS_MM = (0.0, 0.7, 0.8, 0.9)
TARGET_ANGLE_DEG = 30.0
BIN_WIDTH_KEV = 0.5
DISTANCE_CM = 100.0


def build(kvp: float, physics: str, be_mm: float, fmat: str, fmm: float):
    s = sp.Spek(
        kvp=kvp, th=TARGET_ANGLE_DEG, dk=BIN_WIDTH_KEV, physics=physics,
        targ="W", x=0.0, y=0.0, z=DISTANCE_CM, mas=1.0,
        brem=True, char=True,
    )
    if be_mm > 0:
        s.filter("Be", be_mm)
    if fmm > 0:
        s.filter(fmat, fmm)
    return s


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    beams = list(csv.DictReader(BASELINE.open()))
    rows=[]
    for b in beams:
        target=float(b["hvl_cu_mm"])
        for physics in PHYSICS_MODES:
            for be in BE_WINDOWS_MM:
                r={
                    "beam_id":b["beam_id"],"kvp":b["kvp"],
                    "target_hvl_cu_mm":f"{target:.6f}",
                    "physics":physics,"target_angle_deg":f"{TARGET_ANGLE_DEG:g}",
                    "be_window_mm":f"{be:g}",
                    "known_filter_material":b["known_filter_material"],
                    "known_filter_mm":b["known_filter_mm"],
                    "spekpy_version":package_version("spekpy"),
                }
                try:
                    s=build(float(b["kvp"]),physics,be,b["known_filter_material"],float(b["known_filter_mm"]))
                    h1=float(s.get_hvl1(matl="Cu",to="air"))
                    h2=float(s.get_hvl2(matl="Cu",to="air"))
                    hc=float(s.get_hc(matl="Cu",to="air"))
                    em=float(s.get_emean())
                    r.update({
                        "model_hvl1_cu_mm":f"{h1:.6f}",
                        "model_hvl2_cu_mm":f"{h2:.6f}",
                        "hc_cu":f"{hc:.6f}","mean_energy_keV":f"{em:.6f}",
                        "delta_hvl1_pct":f"{100*(h1/target-1):+.3f}",
                        "status":"too_hard" if h1>target else "not_too_hard",
                        "error":"",
                    })
                except Exception as e:
                    r.update({"model_hvl1_cu_mm":"NA","model_hvl2_cu_mm":"NA","hc_cu":"NA","mean_energy_keV":"NA","delta_hvl1_pct":"NA","status":"engine_error","error":repr(e)})
                rows.append(r)

    fields=["beam_id","kvp","target_hvl_cu_mm","physics","target_angle_deg","be_window_mm","known_filter_material","known_filter_mm","spekpy_version","model_hvl1_cu_mm","model_hvl2_cu_mm","hc_cu","mean_energy_keV","delta_hvl1_pct","status","error"]
    csv_path=RESULTS/"stage1r_tube_informed_scan.csv"
    with csv_path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    lines=[]
    for b in beams:
        beam=b["beam_id"]; target=float(b["hvl_cu_mm"])
        rr=[r for r in rows if r["beam_id"]==beam and r["status"]!="engine_error"]
        lines.append(f"[{beam}] measured HVL1={target:.6f} mm Cu")
        for physics in PHYSICS_MODES:
            r0=next(r for r in rr if r["physics"]==physics and r["be_window_mm"]=="0")
            r8=next(r for r in rr if r["physics"]==physics and r["be_window_mm"]=="0.8")
            lines.append(
                f"  {physics}: no-Be {r0['model_hvl1_cu_mm']} ({r0['delta_hvl1_pct']}%), "
                f"0.8mm-Be {r8['model_hvl1_cu_mm']} ({r8['delta_hvl1_pct']}%), "
                f"meanE@0.8Be={r8['mean_energy_keV']} keV"
            )
        best=min(rr,key=lambda r:abs(float(r["model_hvl1_cu_mm"])-target))
        lines.append(
            f"  closest tube-informed case: {best['physics']}, Be={best['be_window_mm']} mm, "
            f"HVL={best['model_hvl1_cu_mm']} mm, delta={best['delta_hvl1_pct']}%, status={best['status']}"
        )
        lines.append("")
    summary=RESULTS/"stage1r_tube_informed_summary.txt"
    summary.write_text("\n".join(lines))
    print(summary.read_text())
    print(f"Wrote {csv_path}")


if __name__=="__main__":
    main()
