#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def score(text: str, label: str) -> tuple[float, float]:
    m = re.search(rf'^{re.escape(label)}\s+([0-9.+Ee-]+)\s+\+/-\s*([0-9.+Ee-]+)\s+%', text, re.M)
    if not m:
        raise SystemExit(f'Missing score: {label}')
    return float(m.group(1)), float(m.group(2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--beam', required=True)
    ap.add_argument('--medium', required=True, choices=('water','rw3'))
    ap.add_argument('--source-model', required=True, choices=('point','finite_7p5mm'))
    ap.add_argument('--spectrum-variant', required=True)
    ap.add_argument('--ncase', required=True)
    ap.add_argument('--seed1', required=True)
    ap.add_argument('--seed2', required=True)
    args = ap.parse_args()

    text = Path(args.log).read_text()
    if args.medium == 'water':
        d, u_d = score(text, 'dose_to_water')
        c, u_c = score(text, 'chamber_in_water')
        dose_label = 'D_water_per_history'
        cavity_label = 'Dcav_water_per_history'
    else:
        d, u_d = score(text, 'dose_to_rw3')
        c, u_c = score(text, 'chamber_in_rw3')
        dose_label = 'D_RW3_per_history'
        cavity_label = 'Dcav_RW3_per_history'

    if u_d > 1.0 or u_c > 1.0:
        raise SystemExit(f'Precision gate failed: uD={u_d}%, uC={u_c}%')

    with Path(args.output).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow([
            'beam','medium','source_model','spectrum_variant','ncase','seed1','seed2',
            dose_label,'u_D_pct',cavity_label,'u_Dcav_pct'
        ])
        w.writerow([
            args.beam,args.medium,args.source_model,args.spectrum_variant,args.ncase,args.seed1,args.seed2,
            d,u_d,c,u_c
        ])


if __name__ == '__main__':
    main()
