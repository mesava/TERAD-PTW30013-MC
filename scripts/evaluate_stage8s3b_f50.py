#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path

BEAMS = ('Q120','Q140','Q150','Q200')
SOURCES = ('point','finite_7p5mm')


def read_single_rows(pattern: str) -> list[dict[str,str]]:
    rows=[]
    for p in glob.glob(pattern):
        with open(p, newline='') as f:
            rr=list(csv.DictReader(f))
        if len(rr) != 1:
            raise SystemExit(f'Expected one row in {p}, found {len(rr)}')
        rows.append(rr[0])
    return rows


def weighted_rco(path: str) -> tuple[float,float,float]:
    with open(path, newline='') as f:
        rows=list(csv.DictReader(f))
    r=next((x for x in rows if x['estimate']=='weighted'),None)
    if r is None:
        raise SystemExit('Missing weighted R_Co row')
    return float(r['R_Co']),float(r['u_abs']),float(r['u_pct'])


def f50_baselines(path: str) -> dict[str,float]:
    with open(path, newline='') as f:
        rows=list(csv.DictReader(f))
    out={}
    for r in rows:
        if r['applicator']=='F50' and r['field_cm']=='8x10':
            out[r['beam']]=float(r['k_Qg_Co_direct_RW3_to_water'])
    if set(out)!=set(BEAMS):
        raise SystemExit(f'Incomplete idealized F50 baseline: {out.keys()}')
    return out


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--points-glob', required=True)
    ap.add_argument('--rco', required=True)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--gate-output', required=True)
    args=ap.parse_args()

    points=read_single_rows(args.points_glob)
    idx={(r['beam'],r['source_model'],r['medium']):r for r in points}
    expected={(b,s,m) for b in BEAMS for s in SOURCES for m in ('water','rw3')}
    missing=expected-set(idx)
    extra=set(idx)-expected
    if missing or extra or len(points)!=16:
        raise SystemExit(f'Point matrix mismatch: missing={sorted(missing)} extra={sorted(extra)} n={len(points)}')

    rco,u_rco_abs,u_rco_pct=weighted_rco(args.rco)
    baseline=f50_baselines(args.baseline)
    rows=[]
    k_by={}

    for b in BEAMS:
        for s in SOURCES:
            w=idx[(b,s,'water')]
            r=idx[(b,s,'rw3')]
            if w['spectrum_variant']!='hw_be0p8_a20' or r['spectrum_variant']!='hw_be0p8_a20':
                raise SystemExit(f'Unexpected spectrum variant for {b}/{s}')
            dw=float(w['D_water_per_history'])
            u_dw=float(w['u_D_pct'])
            dcav=float(r['Dcav_RW3_per_history'])
            u_dcav=float(r['u_Dcav_pct'])
            if dw<=0 or dcav<=0:
                raise SystemExit(f'Non-positive dose score for {b}/{s}')
            rd=dw/dcav
            u_rd_pct=math.hypot(u_dw,u_dcav)
            u_rd_abs=rd*u_rd_pct/100.0
            k=rd/rco
            u_k_pct=math.hypot(u_rd_pct,u_rco_pct)
            u_k_abs=k*u_k_pct/100.0
            delta_baseline=100.0*(k/baseline[b]-1.0)
            k_by[(b,s)]=k
            rows.append({
                'beam':b,'geometry':'F50_8x10_SSD50','spectrum_variant':'hw_be0p8_a20',
                'source_model':s,'Dw_water_per_history':dw,'u_Dw_water_pct':u_dw,
                'Dcav_RW3_per_history':dcav,'u_Dcav_RW3_pct':u_dcav,
                'R_direct_RW3_to_water':rd,'u_R_direct_abs':u_rd_abs,'u_R_direct_pct':u_rd_pct,
                'R_Co':rco,'u_R_Co_pct':u_rco_pct,'K_Qg_Co_RW3_to_water':k,
                'u_K_abs':u_k_abs,'u_K_pct':u_k_pct,
                'K_idealized_stage8_F50':baseline[b],
                'delta_vs_idealized_pct':delta_baseline,
                'finite_vs_hardware_point_pct':'',
                'point_gate':str(u_rd_pct<=1.0).lower(),
            })

    for row in rows:
        b=row['beam']
        finite_effect=100.0*(k_by[(b,'finite_7p5mm')]/k_by[(b,'point')]-1.0)
        row['finite_vs_hardware_point_pct']=finite_effect

    fields=list(rows[0].keys())
    with Path(args.output).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    max_u=max(float(r['u_R_direct_pct']) for r in rows)
    max_abs_hw=max(abs(float(r['delta_vs_idealized_pct'])) for r in rows if r['source_model']=='point')
    max_abs_focus=max(abs(float(r['finite_vs_hardware_point_pct'])) for r in rows)
    gate=len(rows)==8 and max_u<=1.0
    text=(
        f'gate_pass={str(gate).lower()}\n'
        f'points={len(rows)}/8\n'
        f'max_u_R_direct_pct={max_u:.6f}\n'
        f'max_abs_hardware_point_vs_idealized_pct={max_abs_hw:.6f}\n'
        f'max_abs_finite_vs_hardware_point_pct={max_abs_focus:.6f}\n'
        'spectrum_variant=hw_be0p8_a20\n'
        'geometry=F50_8x10_SSD50\n'
        'note=hardware spectrum uses explicit Be 0.8 mm, nominal 20-deg screening angle, nonnegative residual-Al HVL constraint\n'
    )
    Path(args.gate_output).write_text(text)
    print(text,end='')
    if not gate:
        raise SystemExit('Stage 8S3b precision/completeness gate failed')


if __name__=='__main__':
    main()
