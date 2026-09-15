#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path

RCO = 1.12016676
U_RCO_ABS = 0.00104473


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--points-glob', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--gate-output', required=True)
    args = ap.parse_args()

    baseline = {}
    with open(args.baseline, newline='') as f:
        for row in csv.DictReader(f):
            if row['applicator'] == 'F50':
                baseline[row['beam']] = row
    expected_beams = ('Q120', 'Q140', 'Q150', 'Q200')
    if set(baseline) != set(expected_beams):
        raise SystemExit('Missing Stage 8 F50 baseline rows')

    points = {}
    for fn in glob.glob(args.points_glob):
        with open(fn, newline='') as f:
            row = next(csv.DictReader(f))
            points[(row['beam'], row['variant'])] = row
    if len(points) != 8:
        raise SystemExit(f'Expected 8 sensitivity points, found {len(points)}')

    rows = []
    for beam in expected_beams:
        b = baseline[beam]
        k0 = float(b['k_Qg_Co_direct_RW3_to_water'])
        dw = float(b['Dw_water_per_history'])
        u_dw_pct = float(b['u_Dw_water_pct'])
        vals = {}
        for variant in ('low', 'high'):
            p = points[(beam, variant)]
            dc = float(p['Dcav_RW3_per_history'])
            u_dc_pct = float(p['u_Dcav_RW3_pct'])
            k = dw / dc / RCO
            shift_pct = 100.0 * (k / k0 - 1.0)
            u_k_pct = math.sqrt(
                u_dw_pct**2 + u_dc_pct**2 + (U_RCO_ABS / RCO * 100.0)**2
            )
            vals[variant] = (k, shift_pct, u_k_pct, u_dc_pct)

        low, high = vals['low'], vals['high']
        max_shift_pct = max(abs(low[1]), abs(high[1]))
        u_rect_material_pct = max_shift_pct / math.sqrt(3.0)
        endpoint_span_pct = 100.0 * (high[0] / low[0] - 1.0)
        u_span_pct = math.sqrt(low[2]**2 + high[2]**2)
        span_z_conservative = abs(endpoint_span_pct) / u_span_pct if u_span_pct else float('inf')
        rows.append([
            beam, k0,
            low[0], low[1],
            high[0], high[1],
            endpoint_span_pct,
            max_shift_pct,
            u_rect_material_pct,
            span_z_conservative,
            low[3], high[3],
        ])

    with Path(args.output).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow([
            'beam','k_nominal_F50','k_tio2_1p6','shift_low_pct','k_tio2_2p4','shift_high_pct',
            'endpoint_span_pct','max_abs_endpoint_shift_pct','u_rect_material_pct',
            'span_z_conservative','u_Dcav_low_pct','u_Dcav_high_pct'
        ])
        w.writerows(rows)

    max_u_dc = max(max(r[-2], r[-1]) for r in rows)
    max_u_mat = max(r[8] for r in rows)
    Path(args.gate_output).write_text(
        'screen_complete=true\n'
        'points=8\n'
        'criterion=max u(Dcav) <= 1.0%\n'
        f'max_u_Dcav_pct={max_u_dc:.5f}\n'
        f'max_u_rect_material_pct={max_u_mat:.5f}\n'
        'assumption=PTW +/-0.4 percentage-point TiO2 tolerance treated as rectangular bound for screening\n'
    )

    print(Path(args.output).read_text())
    print(Path(args.gate_output).read_text())


if __name__ == '__main__':
    main()
