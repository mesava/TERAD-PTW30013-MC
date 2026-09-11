#!/usr/bin/env python3
"""Stage 1R-3: infer the effective constant-potential kVp required to match TERAD HVL.

Diagnostic only. The physical tube candidate is fixed to W target, 30-degree target
angle, 0.8 mm Be window and the authoritative clinical removable filter. For each
SpekPy physics family we solve for the constant-potential kVp whose Cu HVL equals
the measured TERAD HVL. The inferred value is NOT interpreted as the machine's
actual kVp; it quantifies how far an idealized constant-potential model must move
from nominal to reproduce beam quality.
"""
from __future__ import annotations

import csv
from pathlib import Path

import spekpy as sp
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'data'/'terad_input_baseline.csv'
RESULTS=ROOT/'results'
PHYSICS=('kqp','spekcalc','spekpy-v1')
ANGLE=30.0
BE_MM=0.8
DK=0.5
KVP_MIN=20.0
KVP_MAX=225.0


def hvl(kvp: float, physics: str, fmat: str, fmm: float) -> float:
    s=sp.Spek(kvp=float(kvp),th=ANGLE,dk=DK,physics=physics,targ='W',x=0,y=0,z=100,mas=1,brem=True,char=True)
    s.filter('Be',BE_MM)
    if fmm>0: s.filter(fmat,fmm)
    return float(s.get_hvl1(matl='Cu',to='air'))


def main():
    RESULTS.mkdir(exist_ok=True)
    beams=list(csv.DictReader(BASELINE.open()))
    rows=[]
    for b in beams:
        nominal=float(b['kvp']); target=float(b['hvl_cu_mm']); fmat=b['known_filter_material']; fmm=float(b['known_filter_mm'])
        for physics in PHYSICS:
            lo=max(KVP_MIN, 10.0); hi=KVP_MAX
            hlo=hvl(lo,physics,fmat,fmm); hhi=hvl(hi,physics,fmat,fmm); hnom=hvl(nominal,physics,fmat,fmm)
            rec={
                'beam_id':b['beam_id'],'physics':physics,'nominal_kvp':f'{nominal:g}',
                'target_hvl_cu_mm':f'{target:.6f}','known_filter_material':fmat,'known_filter_mm':f'{fmm:g}',
                'target_angle_deg':f'{ANGLE:g}','be_window_mm':f'{BE_MM:g}',
                'nominal_model_hvl_cu_mm':f'{hnom:.6f}',
                'nominal_hvl_error_pct':f'{100*(hnom/target-1):+.3f}',
                'hvl_at_search_min':f'{hlo:.6f}','hvl_at_search_max':f'{hhi:.6f}',
            }
            if not (min(hlo,hhi) <= target <= max(hlo,hhi)):
                rec.update({'status':'no_kvp_solution_20_to_225','effective_kvp':'NA','effective_minus_nominal_kv':'NA','effective_minus_nominal_pct':'NA','matched_hvl_cu_mm':'NA'})
            else:
                root=float(brentq(lambda v:hvl(v,physics,fmat,fmm)-target,lo,hi,xtol=1e-5,rtol=1e-8,maxiter=80))
                hm=hvl(root,physics,fmat,fmm)
                rec.update({
                    'status':'solution','effective_kvp':f'{root:.4f}',
                    'effective_minus_nominal_kv':f'{root-nominal:+.4f}',
                    'effective_minus_nominal_pct':f'{100*(root/nominal-1):+.3f}',
                    'matched_hvl_cu_mm':f'{hm:.6f}',
                })
            rows.append(rec)
    fields=['beam_id','physics','nominal_kvp','target_hvl_cu_mm','known_filter_material','known_filter_mm','target_angle_deg','be_window_mm','nominal_model_hvl_cu_mm','nominal_hvl_error_pct','hvl_at_search_min','hvl_at_search_max','status','effective_kvp','effective_minus_nominal_kv','effective_minus_nominal_pct','matched_hvl_cu_mm']
    out=RESULTS/'stage1r_effective_kvp_diagnostic.csv'
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    lines=[]
    for b in beams:
        lines.append(f"[{b['beam_id']}] nominal={b['kvp']} kV, target HVL={float(b['hvl_cu_mm']):.6f} mm Cu")
        for r in [x for x in rows if x['beam_id']==b['beam_id']]:
            if r['status']=='solution':
                lines.append(f"  {r['physics']}: effective={r['effective_kvp']} kV ({r['effective_minus_nominal_pct']}%), nominal-model HVL={r['nominal_model_hvl_cu_mm']}")
            else:
                lines.append(f"  {r['physics']}: NO SOLUTION in 20-225 kV, nominal-model HVL={r['nominal_model_hvl_cu_mm']}")
        lines.append('')
    summary=RESULTS/'stage1r_effective_kvp_summary.txt'
    summary.write_text('\n'.join(lines))
    print(summary.read_text())
    print('Wrote',out)

if __name__=='__main__': main()
