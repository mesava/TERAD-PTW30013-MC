#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path

BEAMS=('Q120','Q140','Q150','Q200')
F40_GEOMS={
    'F40_4x15_SSD40': ('F40',40.0,'4x15'),
    'F40_6x8_SSD40': ('F40',40.0,'6x8'),
}
F50_GEOM='F50_8x10_SSD50'


def read_single_rows(pattern: str) -> list[dict[str,str]]:
    rows=[]
    for p in glob.glob(pattern):
        with open(p,newline='') as f:
            rr=list(csv.DictReader(f))
        if len(rr)!=1:
            raise SystemExit(f'Expected one row in {p}, found {len(rr)}')
        rows.append(rr[0])
    return rows


def weighted_rco(path: str) -> tuple[float,float]:
    with open(path,newline='') as f:
        rows=list(csv.DictReader(f))
    r=next((x for x in rows if x['estimate']=='weighted'),None)
    if r is None:
        raise SystemExit('Missing weighted R_Co row')
    return float(r['R_Co']),float(r['u_pct'])


def idealized_baselines(path: str) -> dict[tuple[str,str,str],float]:
    with open(path,newline='') as f:
        rows=list(csv.DictReader(f))
    out={}
    for r in rows:
        out[(r['beam'],r['applicator'],r['field_cm'])]=float(r['k_Qg_Co_direct_RW3_to_water'])
    return out


def f50_finite_rows(path: str) -> dict[str,dict[str,str]]:
    with open(path,newline='') as f:
        rows=list(csv.DictReader(f))
    out={}
    for r in rows:
        if r['geometry']==F50_GEOM and r['source_model']=='finite_7p5mm' and r['spectrum_variant']=='hw_be0p8_a20':
            out[r['beam']]=r
    if set(out)!=set(BEAMS):
        raise SystemExit(f'Incomplete Stage 8S3b finite F50 baseline: {sorted(out)}')
    return out


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--points-glob',required=True)
    ap.add_argument('--rco',required=True)
    ap.add_argument('--idealized-baseline',required=True)
    ap.add_argument('--f50-hardware',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--gate-output',required=True)
    args=ap.parse_args()

    points=read_single_rows(args.points_glob)
    idx={(r['beam'],r['geometry'],r['medium']):r for r in points}
    expected={(b,g,m) for b in BEAMS for g in F40_GEOMS for m in ('water','rw3')}
    if set(idx)!=expected or len(points)!=16:
        raise SystemExit(f'F40 matrix mismatch: missing={sorted(expected-set(idx))} extra={sorted(set(idx)-expected)} n={len(points)}')

    rco,u_rco_pct=weighted_rco(args.rco)
    ideal=idealized_baselines(args.idealized_baseline)
    f50=f50_finite_rows(args.f50_hardware)
    rows=[]

    for b in BEAMS:
        for g,(app,ssd,field) in F40_GEOMS.items():
            w=idx[(b,g,'water')]; r=idx[(b,g,'rw3')]
            for rr in (w,r):
                if rr['source_model']!='finite_7p5mm' or rr['spectrum_variant']!='hw_be0p8_a20':
                    raise SystemExit(f'Unexpected model for {b}/{g}/{rr["medium"]}')
            dw=float(w['D_water_per_history']); u_dw=float(w['u_D_pct'])
            dc=float(r['Dcav_RW3_per_history']); u_dc=float(r['u_Dcav_pct'])
            rd=dw/dc
            u_rd_pct=math.hypot(u_dw,u_dc)
            k=rd/rco
            u_k_pct=math.hypot(u_rd_pct,u_rco_pct)
            kb=ideal[(b,app,field)]
            rows.append({
                'beam':b,'applicator':app,'ssd_cm':ssd,'field_cm':field,'geometry':g,
                'source_model':'finite_7p5mm','spectrum_variant':'hw_be0p8_a20',
                'Dw_water_per_history':dw,'u_Dw_water_pct':u_dw,
                'Dcav_RW3_per_history':dc,'u_Dcav_RW3_pct':u_dc,
                'R_direct_RW3_to_water':rd,'u_R_direct_pct':u_rd_pct,
                'R_Co':rco,'u_R_Co_pct':u_rco_pct,
                'K_Qg_Co_RW3_to_water':k,'u_K_pct':u_k_pct,
                'K_idealized_stage8':kb,'delta_vs_idealized_pct':100*(k/kb-1),
                'row_source':'stage8s3d_new_f40',
                'precision_gate':str(u_rd_pct<=1.0).lower(),
            })

        fr=f50[b]
        kb=ideal[(b,'F50','8x10')]
        rows.append({
            'beam':b,'applicator':'F50','ssd_cm':50.0,'field_cm':'8x10','geometry':F50_GEOM,
            'source_model':'finite_7p5mm','spectrum_variant':'hw_be0p8_a20',
            'Dw_water_per_history':fr['Dw_water_per_history'],'u_Dw_water_pct':fr['u_Dw_water_pct'],
            'Dcav_RW3_per_history':fr['Dcav_RW3_per_history'],'u_Dcav_RW3_pct':fr['u_Dcav_RW3_pct'],
            'R_direct_RW3_to_water':fr['R_direct_RW3_to_water'],'u_R_direct_pct':fr['u_R_direct_pct'],
            'R_Co':fr['R_Co'],'u_R_Co_pct':fr['u_R_Co_pct'],
            'K_Qg_Co_RW3_to_water':fr['K_Qg_Co_RW3_to_water'],'u_K_pct':fr['u_K_pct'],
            'K_idealized_stage8':kb,'delta_vs_idealized_pct':100*(float(fr['K_Qg_Co_RW3_to_water'])/kb-1),
            'row_source':'stage8s3b_reused_f50',
            'precision_gate':str(float(fr['u_R_direct_pct'])<=1.0).lower(),
        })

    order={'4x15':0,'6x8':1,'8x10':2}
    rows.sort(key=lambda r:(BEAMS.index(r['beam']),order[r['field_cm']]))
    fields=list(rows[0].keys())
    with Path(args.output).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    max_u=max(float(r['u_R_direct_pct']) for r in rows)
    max_shift=max(abs(float(r['delta_vs_idealized_pct'])) for r in rows)
    gate=(len(rows)==12 and len(points)==16 and max_u<=1.0 and all(r['precision_gate']=='true' for r in rows))
    Path(args.gate_output).write_text(
        f'gate_pass={str(gate).lower()}\n'
        f'clinical_K_rows={len(rows)}/12\n'
        f'new_f40_transport_points={len(points)}/16\n'
        f'reused_f50_rows=4/4\n'
        f'max_u_R_direct_pct={max_u:.6f}\n'
        f'max_abs_delta_vs_idealized_stage8_pct={max_shift:.6f}\n'
        'source_model=finite_7p5mm\n'
        'spectrum_variant=hw_be0p8_a20\n'
        'note=F50 is reused from Stage 8S3b; Stage 8S3d computes only the eight missing F40 K values\n'
    )
    print(Path(args.gate_output).read_text(),end='')
    if not gate:
        raise SystemExit('Stage 8S3d completeness/precision gate failed')


if __name__=='__main__':
    main()
