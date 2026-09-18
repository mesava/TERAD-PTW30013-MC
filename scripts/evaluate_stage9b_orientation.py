#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import math
from pathlib import Path

BEAMS=('Q120','Q140','Q150','Q200')
ROTATED={
    'F40_15x4_SSD40': {'baseline_field':'4x15','rotated_field':'15x4'},
    'F40_8x6_SSD40': {'baseline_field':'6x8','rotated_field':'8x6'},
}


def read_single_rows(pattern: str) -> list[dict[str,str]]:
    rows=[]
    for p in glob.glob(pattern):
        with open(p,newline='') as f:
            rr=list(csv.DictReader(f))
        if len(rr)!=1:
            raise SystemExit(f'Expected one row in {p}, found {len(rr)}')
        rows.append(rr[0])
    return rows


def nominal_rows(path: str) -> dict[tuple[str,str],dict[str,str]]:
    with open(path,newline='') as f:
        rows=list(csv.DictReader(f))
    out={}
    for r in rows:
        if r['applicator']=='F40' and r['field_cm'] in ('4x15','6x8'):
            out[(r['beam'],r['field_cm'])]=r
    expected={(b,f) for b in BEAMS for f in ('4x15','6x8')}
    if set(out)!=expected:
        raise SystemExit(f'Incomplete Stage 8S3d F40 nominal baseline: missing={sorted(expected-set(out))}')
    return out


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--points-glob',required=True)
    ap.add_argument('--baseline',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--gate-output',required=True)
    args=ap.parse_args()

    pts=read_single_rows(args.points_glob)
    idx={(r['beam'],r['geometry'],r['medium']):r for r in pts}
    expected={(b,g,m) for b in BEAMS for g in ROTATED for m in ('water','rw3')}
    if set(idx)!=expected or len(pts)!=16:
        raise SystemExit(f'Orientation matrix mismatch: missing={sorted(expected-set(idx))} extra={sorted(set(idx)-expected)} n={len(pts)}')

    base=nominal_rows(args.baseline)
    rows=[]

    for b in BEAMS:
        for g,meta in ROTATED.items():
            w=idx[(b,g,'water')]; r=idx[(b,g,'rw3')]
            for rr in (w,r):
                if rr['source_model']!='finite_7p5mm' or rr['spectrum_variant']!='hw_be0p8_a20':
                    raise SystemExit(f'Unexpected model for {b}/{g}/{rr["medium"]}')
                if rr['chamber_longitudinal_axis']!='x':
                    raise SystemExit(f'Unexpected chamber axis convention for {b}/{g}')
                if rr['baseline_field_cm']!=meta['baseline_field'] or rr['rotated_field_cm']!=meta['rotated_field']:
                    raise SystemExit(f'Field metadata mismatch for {b}/{g}')

            dw=float(w['D_water_per_history']); u_dw=float(w['u_D_pct'])
            dc=float(r['Dcav_RW3_per_history']); u_dc=float(r['u_Dcav_pct'])
            rd=dw/dc
            u_rd_pct=math.hypot(u_dw,u_dc)

            br=base[(b,meta['baseline_field'])]
            rco=float(br['R_Co'])
            u_rco_pct=float(br['u_R_Co_pct'])
            k=rd/rco
            u_k_pct=math.hypot(u_rd_pct,u_rco_pct)

            k0=float(br['K_Qg_Co_RW3_to_water'])
            u_r0=float(br['u_R_direct_pct'])
            ratio=k/k0
            delta=100.0*(ratio-1.0)
            u_ratio_pct=math.hypot(u_rd_pct,u_r0)
            z=abs(delta)/u_ratio_pct if u_ratio_pct>0 else math.inf

            rows.append({
                'beam':b,
                'applicator':'F40',
                'ssd_cm':40.0,
                'baseline_field_x_by_y_cm':meta['baseline_field'],
                'rotated_field_x_by_y_cm':meta['rotated_field'],
                'chamber_longitudinal_axis':'x',
                'source_model':'finite_7p5mm',
                'spectrum_variant':'hw_be0p8_a20',
                'Dw_rotated_water_per_history':dw,
                'u_Dw_rotated_pct':u_dw,
                'Dcav_rotated_RW3_per_history':dc,
                'u_Dcav_rotated_pct':u_dc,
                'R_direct_rotated':rd,
                'u_R_direct_rotated_pct':u_rd_pct,
                'K_rotated':k,
                'u_K_rotated_pct':u_k_pct,
                'K_nominal_stage8s3d':k0,
                'u_R_direct_nominal_pct':u_r0,
                'rotated_over_nominal_ratio':ratio,
                'delta_K_orientation_pct':delta,
                'u_rotated_over_nominal_ratio_pct':u_ratio_pct,
                'z_orientation_shift':z,
                'R_Co_cancels_in_orientation_ratio':'true',
                'precision_gate':str(u_rd_pct<=1.0).lower(),
            })

    fields=list(rows[0].keys())
    with Path(args.output).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    max_u=max(float(r['u_R_direct_rotated_pct']) for r in rows)
    max_shift=max(abs(float(r['delta_K_orientation_pct'])) for r in rows)
    max_z=max(float(r['z_orientation_shift']) for r in rows)
    gate=(len(rows)==8 and len(pts)==16 and max_u<=1.0 and all(r['precision_gate']=='true' for r in rows))
    Path(args.gate_output).write_text(
        f'gate_pass={str(gate).lower()}\n'
        f'orientation_comparisons={len(rows)}/8\n'
        f'new_transport_points={len(pts)}/16\n'
        f'max_u_R_direct_rotated_pct={max_u:.6f}\n'
        f'max_abs_delta_K_orientation_pct={max_shift:.6f}\n'
        f'max_z_orientation_shift={max_z:.6f}\n'
        'chamber_longitudinal_axis=x\n'
        'baseline_fields=4x15,6x8\n'
        'rotated_fields=15x4,8x6\n'
        'source_model=finite_7p5mm\n'
        'spectrum_variant=hw_be0p8_a20\n'
        'note=R_Co cancels in rotated/nominal comparison; baseline transport is reused from Stage 8S3d\n'
    )
    print(Path(args.gate_output).read_text(),end='')
    if not gate:
        raise SystemExit('Stage 9B completeness/precision gate failed')


if __name__=='__main__':
    main()
