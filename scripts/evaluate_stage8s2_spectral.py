#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
from pathlib import Path


def read_one(path):
    with open(path,newline='') as f:
        return next(csv.DictReader(f))


def read_spectrum(path):
    with open(path,newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--summaries-glob', required=True)
    ap.add_argument('--spectra-glob', required=True)
    ap.add_argument('--output-summary', required=True)
    ap.add_argument('--output-ratios', required=True)
    ap.add_argument('--gate-output', required=True)
    args=ap.parse_args()

    summaries={}
    for fn in glob.glob(args.summaries_glob):
        r=read_one(fn)
        summaries[(r['beam'],r['medium'],float(r['depth_cm']))]=r
    if len(summaries)!=24:
        raise SystemExit(f'Expected 24 point summaries, found {len(summaries)}')

    spectra={}
    for fn in glob.glob(args.spectra_glob):
        name=Path(fn).stem
        parts=name.split('_')
        # stage8s2_spectrum_Q120_water_d0p001
        beam=parts[2]; medium=parts[3]
        dtag=parts[4][1:]
        depth=float(dtag.replace('p','.'))
        spectra[(beam,medium,depth)]=read_spectrum(fn)
    if len(spectra)!=24:
        raise SystemExit(f'Expected 24 spectra, found {len(spectra)}')

    out=[]
    ratio_rows=[]
    max_p95=0.0
    for beam in ('Q120','Q140','Q150','Q200'):
        for depth in (0.001,1.0,2.0):
            w=summaries[(beam,'water',depth)]
            r=summaries[(beam,'rw3',depth)]
            fw=float(w['integrated_fluence_cm-2']); fr=float(r['integrated_fluence_cm-2'])
            ew=float(w['energy_fluence_MeV_cm-2']); er=float(r['energy_fluence_MeV_cm-2'])
            mw=float(w['mean_energy_MeV']); mr=float(r['mean_energy_MeV'])
            medw=float(w['E50_MeV']); medr=float(r['E50_MeV'])
            max_p95=max(max_p95,float(w['p95_rel_u_active_bins_pct']),float(r['p95_rel_u_active_bins_pct']))
            out.append([
                beam,depth,fw,fr,fr/fw,ew,er,er/ew,mw,mr,100*(mr/mw-1),medw,medr,
                float(w['fraction_below_20keV']),float(r['fraction_below_20keV']),
                float(w['fraction_below_30keV']),float(r['fraction_below_30keV']),
                float(w['fraction_below_50keV']),float(r['fraction_below_50keV'])
            ])
            sw=spectra[(beam,'water',depth)]; sr=spectra[(beam,'rw3',depth)]
            if len(sw)!=len(sr):
                raise SystemExit('Spectrum length mismatch')
            for a,b in zip(sw,sr):
                e=float(a['energy_MeV']); pw=float(a['differential_fluence_per_MeV_cm2']); pr=float(b['differential_fluence_per_MeV_cm2'])
                ratio_rows.append([beam,depth,e,pw,pr,(pr/pw if pw>0 else '')])

    with open(args.output_summary,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow([
            'beam','depth_cm','Phi_water','Phi_RW3','Phi_RW3_over_water','Efluence_water','Efluence_RW3',
            'Efluence_RW3_over_water','meanE_water_MeV','meanE_RW3_MeV','meanE_shift_pct','medianE_water_MeV',
            'medianE_RW3_MeV','water_frac_lt20keV','rw3_frac_lt20keV','water_frac_lt30keV','rw3_frac_lt30keV',
            'water_frac_lt50keV','rw3_frac_lt50keV'
        ])
        w.writerows(out)
    with open(args.output_ratios,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['beam','depth_cm','energy_MeV','Phi_water','Phi_RW3','RW3_over_water'])
        w.writerows(ratio_rows)

    gate = max_p95 <= 5.0
    Path(args.gate_output).write_text(
        f'gate_pass={str(gate).lower()}\npoints=24\ncriterion=p95 relative uncertainty of active spectral bins <= 5%\nmax_p95_rel_u_active_bins_pct={max_p95:.5f}\n'
    )
    if not gate:
        raise SystemExit('Stage 8S2 precision gate failed')
    print(Path(args.output_summary).read_text())
    print(Path(args.gate_output).read_text())


if __name__=='__main__':
    main()
