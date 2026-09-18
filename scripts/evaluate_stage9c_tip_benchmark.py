#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,glob,math
from pathlib import Path

BEAMS=("CCRI100","CCRI135","CCRI180","CCRI250")
CASES=("tip1p0","tip2p0")
TARGET={"CCRI100":0.95355,"CCRI135":0.97460,"CCRI180":0.98565}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--points-glob",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--gate-output",required=True)
    a=ap.parse_args()
    rows=[]
    for p in glob.glob(a.points_glob):
        rr=list(csv.DictReader(open(p)))
        if len(rr)!=1: raise SystemExit(f"Expected one row in {p}")
        rows.append(rr[0])
    idx={(r["case"],r["beam"]):r for r in rows}
    exp={(c,b) for c in CASES for b in BEAMS}
    if set(idx)!=exp or len(rows)!=8:
        raise SystemExit(f"Stage9C1 matrix mismatch; missing={sorted(exp-set(idx))}; extra={sorted(set(idx)-exp)}")
    out=[]; candidate={}
    for case in CASES:
        base=idx[(case,"CCRI250")]
        r250=float(base["R_Dw_over_Dcav"]); u250=float(base["u_R_abs"])
        kvals={}
        all_z=True
        for beam in ("CCRI100","CCRI135","CCRI180"):
            q=idx[(case,beam)]
            rq=float(q["R_Dw_over_Dcav"]); uq=float(q["u_R_abs"])
            k=rq/r250
            uk=k*math.sqrt((uq/rq)**2+(u250/r250)**2)
            target=TARGET[beam]
            z=(k-target)/uk
            kvals[beam]=k
            if abs(z)>2: all_z=False
            out.append({
                "case":case,"tip_mm":q["tip_mm"],"quality":beam,
                "kq_250":k,"uk_abs":uk,"uk_pct":100*uk/k,
                "target":target,"delta_vs_target_pct":100*(k/target-1),
                "z_vs_target":z,"within_2sigma":str(abs(z)<=2).lower()
            })
        monotonic=0<kvals["CCRI100"]<kvals["CCRI135"]<kvals["CCRI180"]<1
        candidate[case]=all_z and monotonic
    fields=list(out[0].keys())
    with Path(a.output).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    transport_gate=(len(rows)==8 and all(r["precision_gate"]=="true" for r in rows))
    with Path(a.gate_output).open("w") as f:
        f.write(f"transport_gate_pass={str(transport_gate).lower()}\n")
        f.write("new_transport_points=8/8\n")
        for case in CASES:
            f.write(f"{case}_provisional_benchmark_candidate={str(candidate[case]).lower()}\n")
        f.write("qualification_rule=all CCRI100/135/180 ratios within |z|<=2 and monotonic k100<k135<k180<1\n")
        f.write("note=single 300M replicate is a screen only; any passing endpoint requires independent replication before TERAD model-form use\n")
    print(Path(a.gate_output).read_text(),end="")
    if not transport_gate: raise SystemExit("Stage9C1 completeness/precision gate failed")

if __name__=="__main__": main()
