#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--summaries-glob', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--baseline-histories', type=int, default=50_000_000)
    ap.add_argument('--target-p95-pct', type=float, default=5.0)
    ap.add_argument('--safety-factor', type=float, default=1.15)
    args = ap.parse_args()

    rows = []
    for fn in glob.glob(args.summaries_glob):
        with open(fn, newline='') as f:
            r = next(csv.DictReader(f))
        p95 = float(r['p95_rel_u_active_bins_pct'])
        multiplier = max(1.0, (p95 / args.target_p95_pct) ** 2 * args.safety_factor)
        recommended = int(math.ceil(args.baseline_histories * multiplier / 1_000_000.0) * 1_000_000)
        rows.append({
            'beam': r['beam'],
            'medium': r['medium'],
            'depth_cm': float(r['depth_cm']),
            'p95_rel_u_active_bins_pct': p95,
            'passes_5pct': p95 <= args.target_p95_pct,
            'recommended_histories': recommended,
            'history_multiplier_vs_50M': recommended / args.baseline_histories,
            'integrated_fluence_cm-2': r.get('integrated_fluence_cm-2', ''),
            'mean_energy_MeV': r.get('mean_energy_MeV', ''),
        })

    if len(rows) != 24:
        raise SystemExit(f'Expected 24 Stage 8S2 summaries, found {len(rows)}')

    rows.sort(key=lambda r: r['p95_rel_u_active_bins_pct'], reverse=True)
    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    failed = [r for r in rows if not r['passes_5pct']]
    maxrow = rows[0]
    lines = [
        f'points=24',
        f'failed_points={len(failed)}',
        f'target_p95_pct={args.target_p95_pct:.3f}',
        f'max_p95_pct={maxrow["p95_rel_u_active_bins_pct"]:.6f}',
        f'worst_point={maxrow["beam"]},{maxrow["medium"]},depth={maxrow["depth_cm"]}cm',
        '',
        'Points requiring additional histories:',
    ]
    for r in failed:
        lines.append(
            f'{r["beam"]},{r["medium"]},depth={r["depth_cm"]}cm: '
            f'p95={r["p95_rel_u_active_bins_pct"]:.4f}%, '
            f'recommended_histories={r["recommended_histories"]}'
        )
    if not failed:
        lines.append('none')
    Path(args.report).write_text('\n'.join(lines) + '\n')
    print(Path(args.report).read_text())


if __name__ == '__main__':
    main()
