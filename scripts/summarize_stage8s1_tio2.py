#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def score(text: str, label: str) -> tuple[float, float]:
    m = re.search(rf'^{label}\s+([0-9.+Ee-]+)\s+\+/-\s*([0-9.+Ee-]+)\s+%', text, re.M)
    if not m:
        raise SystemExit(f'Missing score: {label}')
    return float(m.group(1)), float(m.group(2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--beam', required=True)
    ap.add_argument('--variant', required=True, choices=('low', 'high'))
    ap.add_argument('--tio2', required=True, type=float)
    ap.add_argument('--ncase', required=True)
    ap.add_argument('--seed1', required=True)
    ap.add_argument('--seed2', required=True)
    args = ap.parse_args()

    text = Path(args.log).read_text()
    d, u_d = score(text, 'dose_to_rw3')
    c, u_c = score(text, 'chamber_in_rw3')
    m = re.search(r'^dose_to_rw3\s+chamber_in_rw3\s+-\s+([0-9.+Ee-]+)\s+\+/-\s*([0-9.+Ee-]+)', text, re.M)
    if not m:
        raise SystemExit('Missing correlated R_RW3')
    r, u_r = float(m.group(1)), float(m.group(2))
    if u_c > 1.0:
        raise SystemExit(f'Dcav precision gate failed: {u_c}%')

    with Path(args.output).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['beam','variant','tio2_mass_fraction','ncase','seed1','seed2','D_RW3_per_history','u_D_RW3_pct','Dcav_RW3_per_history','u_Dcav_RW3_pct','R_RW3','u_R_RW3_abs'])
        w.writerow([args.beam,args.variant,args.tio2,args.ncase,args.seed1,args.seed2,d,u_d,c,u_c,r,u_r])


if __name__ == '__main__':
    main()
