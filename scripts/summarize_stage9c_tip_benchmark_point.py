#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--log",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--case",required=True)
    ap.add_argument("--tip-mm",required=True,type=float)
    ap.add_argument("--beam",required=True)
    ap.add_argument("--ncase",required=True)
    ap.add_argument("--seed1",required=True)
    ap.add_argument("--seed2",required=True)
    a=ap.parse_args()
    text=Path(a.log).read_text(errors="replace")
    m=re.findall(r'^dose_to_water\s+chamber_in_water\s+-\s+([0-9.+\-Ee]+)\s+\+/-\s*([0-9.+\-Ee]+)',text,re.M)
    if not m: raise SystemExit("Missing dose_to_water/chamber_in_water ratio")
    ratio,u=map(float,m[-1])
    u_pct=100*u/ratio
    if u_pct>1.0: raise SystemExit(f"Raw benchmark ratio precision gate failed: {u_pct:.4f}%")
    with Path(a.output).open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["case","tip_mm","beam","ncase","seed1","seed2","R_Dw_over_Dcav","u_R_abs","u_R_pct","precision_gate"])
        w.writerow([a.case,a.tip_mm,a.beam,a.ncase,a.seed1,a.seed2,ratio,u,u_pct,"true"])

if __name__=="__main__": main()
