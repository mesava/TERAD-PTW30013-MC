#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ANGLE_VARIANTS = {
    10.0: "be0p8_a10",
    15.0: "be0p8_a15",
    20.0: "hw_be0p8_a20",
    25.0: "be0p8_a25",
    30.0: "be0p8_a30",
}
BEAMS = ("Q120", "Q140", "Q150", "Q200")


def yes(v: str) -> bool:
    return str(v).strip() in {"1", "true", "True", "yes", "YES"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.summary).open()))
    by_variant: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for r in rows:
        by_variant[r["variant"]][r["beam"]] = r

    missing = []
    for v in {x.name if hasattr(x, 'name') else x for x in []}:
        pass
    for name in ["hw_be0p8_a20", "be0p7_a20", "be0p9_a20", "kvp_low_be0p8_a20", "kvp_high_be0p8_a20", *ANGLE_VARIANTS.values()]:
        for b in BEAMS:
            if b not in by_variant.get(name, {}):
                missing.append(f"{name}/{b}")
    if missing:
        raise SystemExit("Missing Stage 8S3 spectrum rows: " + ", ".join(sorted(set(missing))))

    nominal = by_variant["hw_be0p8_a20"]
    nominal_feasible = [b for b in BEAMS if yes(nominal[b]["feasible_nonnegative_residual_al"])]
    nominal_infeasible = [b for b in BEAMS if b not in nominal_feasible]

    common_angles = []
    for angle, variant in sorted(ANGLE_VARIANTS.items()):
        if all(yes(by_variant[variant][b]["feasible_nonnegative_residual_al"]) for b in BEAMS):
            common_angles.append(angle)

    # The nearest common feasible angle to the current 20-deg assumption is a
    # computational candidate only, never a claim about the true tube angle.
    nearest_common = None
    if common_angles:
        nearest_common = min(common_angles, key=lambda x: (abs(x - 20.0), x))

    lines = []
    lines.append("Stage 8S3a hardware-informed spectrum feasibility")
    lines.append("=================================================")
    lines.append(f"nominal_explicit_Be_0p8mm_angle20_feasible_beams={','.join(nominal_feasible) if nominal_feasible else 'NONE'}")
    lines.append(f"nominal_explicit_Be_0p8mm_angle20_infeasible_beams={','.join(nominal_infeasible) if nominal_infeasible else 'NONE'}")
    lines.append("common_feasible_screening_angles_deg=" + (",".join(f"{x:g}" for x in common_angles) if common_angles else "NONE"))
    lines.append("nearest_common_feasible_angle_to_20deg=" + (f"{nearest_common:g}" if nearest_common is not None else "NONE"))
    lines.append("note=screening angles are model-form probes, not TERAD specifications")
    lines.append("")

    for variant in ["hw_be0p8_a20", "be0p7_a20", "be0p9_a20", "kvp_low_be0p8_a20", "kvp_high_be0p8_a20", "be0p8_a10", "be0p8_a15", "be0p8_a25", "be0p8_a30"]:
        lines.append(f"[{variant}]")
        for b in BEAMS:
            r = by_variant[variant][b]
            lines.append(
                f"{b}: feasible={r['feasible_nonnegative_residual_al']}; "
                f"baseHVL={float(r['base_hvl1_cu_mm_after_Be_and_known_filter']):.6f} mm Cu; "
                f"target={float(r['target_hvl1_cu_mm']):.6f}; "
                f"residualAl={r['residual_equivalent_al_mm']}; "
                f"meanE={float(r['mean_energy_keV']):.3f} keV; status={r['status']}"
            )
        lines.append("")

    Path(args.output).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
