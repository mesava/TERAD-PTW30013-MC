#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def read_agr(path: Path):
    rows=[]
    for line in path.read_text().splitlines():
        s=line.strip()
        if not s or s.startswith(('#','@','&')):
            continue
        p=s.split()
        if len(p) < 3:
            continue
        try:
            e,phi,u = map(float,p[:3])
        except ValueError:
            continue
        rows.append((e,phi,u))
    if len(rows) < 10:
        raise SystemExit(f'Could not parse spectrum from {path}')
    return rows


def quantile(rows, q, de):
    total=sum(phi*de for _,phi,_ in rows)
    target=q*total
    c=0.0
    for e,phi,_ in rows:
        c += phi*de
        if c >= target:
            return e
    return rows[-1][0]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--agr', required=True)
    ap.add_argument('--output-spectrum', required=True)
    ap.add_argument('--output-summary', required=True)
    ap.add_argument('--beam', required=True)
    ap.add_argument('--medium', required=True, choices=('water','rw3'))
    ap.add_argument('--depth-cm', required=True, type=float)
    ap.add_argument('--ncase', required=True)
    args=ap.parse_args()

    rows=read_agr(Path(args.agr))
    energies=[r[0] for r in rows]
    diffs=[energies[i+1]-energies[i] for i in range(len(energies)-1)]
    de=sum(diffs)/len(diffs)
    if abs(de-0.001) > 5e-6:
        raise SystemExit(f'Unexpected Stage 8S2 bin width: {de}')

    total=sum(phi*de for _,phi,_ in rows)
    eflu=sum(e*phi*de for e,phi,_ in rows)
    if total <= 0:
        raise SystemExit('Non-positive integrated fluence')
    mean_e=eflu/total
    q10=quantile(rows,0.10,de)
    q25=quantile(rows,0.25,de)
    q50=quantile(rows,0.50,de)
    q75=quantile(rows,0.75,de)
    q90=quantile(rows,0.90,de)

    def frac_below(limit_mev):
        return sum(phi*de for e,phi,_ in rows if e < limit_mev)/total

    maxphi=max(phi for _,phi,_ in rows)
    relus=[]
    for _,phi,u in rows:
        if phi >= 0.01*maxphi and phi > 0:
            relus.append(100.0*u/phi)
    relus.sort()
    p95_u = relus[min(len(relus)-1, math.ceil(0.95*len(relus))-1)] if relus else float('inf')

    with Path(args.output_spectrum).open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['energy_MeV','differential_fluence_per_MeV_cm2','u_abs'])
        w.writerows(rows)

    with Path(args.output_summary).open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow([
            'beam','medium','depth_cm','ncase','bin_width_MeV','integrated_fluence_cm-2',
            'energy_fluence_MeV_cm-2','mean_energy_MeV','E10_MeV','E25_MeV','E50_MeV',
            'E75_MeV','E90_MeV','fraction_below_20keV','fraction_below_30keV',
            'fraction_below_50keV','p95_rel_u_active_bins_pct'
        ])
        w.writerow([
            args.beam,args.medium,args.depth_cm,args.ncase,de,total,eflu,mean_e,q10,q25,q50,q75,q90,
            frac_below(0.020),frac_below(0.030),frac_below(0.050),p95_u
        ])

    print(Path(args.output_summary).read_text())


if __name__=='__main__':
    main()
