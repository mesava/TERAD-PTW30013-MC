#!/usr/bin/env python3
"""Build Stage 9C1 PTW30013 B1 tip-family benchmark inputs.

This stage reuses only the predeclared Stage 3H-3 tip sensitivity endpoints
(1.0 and 2.0 mm). It does not introduce new proprietary dimensions and does
not tune geometry to TERAD or to the published benchmark.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--beam", required=True, choices=["CCRI100","CCRI135","CCRI180","CCRI250"])
    ap.add_argument("--tip-cm", required=True, type=float, choices=[0.10,0.20])
    ap.add_argument("--ncase", required=True)
    ap.add_argument("--nbatch", required=True)
    ap.add_argument("--xcse", required=True)
    ap.add_argument("--rr", required=True)
    ap.add_argument("--seed1", required=True)
    ap.add_argument("--seed2", required=True)
    args=ap.parse_args()

    text=Path(args.template).read_text()

    # B0 public sensitive length = 23.0 mm.
    if text.count("thickness = 0.03") != 2:
        raise SystemExit("Unexpected Model A end-gap structure")
    text=text.replace("thickness = 0.03","thickness = 0.09")
    text=text.replace("axis = 2.09 0 0  -1 0 0","axis = 2.15 0 0  -1 0 0",1)
    text=text.replace("positions = -1.09 1.09","positions = -1.15 1.15",1)

    # B1 predeclared tip-family endpoint, carried forward unchanged from 3H-3.
    tip=args.tip_cm
    old_layer="""        :start layer:
            thickness = 1.0
            top radii    = 1.3475
            bottom radii = 1.3475
            media = WATER_1KEV
        :stop layer:

        :start layer:
            thickness = 0.09
"""
    water_pre=1.0-tip
    new_layer=f"""        :start layer:
            thickness = {water_pre:.2f}
            top radii    = 1.3475
            bottom radii = 1.3475
            media = WATER_1KEV
        :stop layer:

        :start layer:
            thickness = {tip:.2f}
            top radii    = 0.3475 1.3475
            bottom radii = 0.3475 1.3475
            media = PMMA_1KEV WATER_1KEV
        :stop layer:

        :start layer:
            thickness = 0.09
"""
    if old_layer not in text:
        raise SystemExit("Could not insert B1 tip layer")
    text=text.replace(old_layer,new_layer,1)

    old="set label = chamber_cavity 5 11 15"
    new="set label = chamber_cavity 10 16 20"
    if old not in text: raise SystemExit("cavity label anchor missing")
    text=text.replace(old,new,1)

    old="set label = chamber_xcse_zone 0 5 6 7 8 10 11 12 13 14 15 16 17 18 20"
    new="set label = chamber_xcse_zone 0 5 6 10 11 12 13 15 16 17 18 19 20 21 22 23 25"
    if old not in text: raise SystemExit("XCSE label anchor missing")
    text=text.replace(old,new,1)

    marker="geometry name = chamber_in_water"
    head,chamber=text.split(marker,1)
    body,tail=chamber.split(":stop calculation geometry:",1)
    token="@@XCSE@@"
    if body.count(token)!=15:
        raise SystemExit(f"Unexpected chamber enhancement count: {body.count(token)}")
    pos=body.rfind(token)+len(token)
    body=body[:pos]+" \\\n                      @@XCSE@@ @@XCSE@@"+body[pos:]
    if body.count(token)!=17:
        raise SystemExit("Could not expand chamber enhancement list")
    text=head+marker+body+":stop calculation geometry:"+tail

    rho_air=1.2048e-3
    r,L,re,Le=0.305,2.30,0.0575,2.12
    net=math.pi*r*r*L-math.pi*re*re*Le
    mass=net*rho_air
    old="cavity mass = 7.410453757123e-4"
    if old not in text: raise SystemExit("Model A cavity mass anchor missing")
    text=text.replace(old,f"cavity mass = {mass:.15e}",1)

    # Benchmark geometry: first 50 cm air folded into spectrum, next 48 cm explicit.
    marker="name = water_phantom"
    head,tail=text.split(marker,1)
    if "z-planes = -2 18" not in tail:
        raise SystemExit("water z-plane anchor missing")
    tail=tail.replace("z-planes = -2 18","z-planes = -50 -2 18",1)
    oldmedia="media = WATER_1KEV\n        :stop media input:"
    newmedia="media = AIR_1KEV WATER_1KEV\n            set medium = 1 1\n        :stop media input:"
    if oldmedia not in tail:
        raise SystemExit("water phantom media anchor missing")
    tail=tail.replace(oldmedia,newmedia,1)
    text=head+marker+tail

    repl={"@@BEAM@@":args.beam,"@@XCSE@@":args.xcse,"@@RR@@":args.rr,"@@NCASE@@":args.ncase}
    for a,b in repl.items(): text=text.replace(a,b)
    text=text.replace("nbatch = 10",f"nbatch = {args.nbatch}",1)
    rng=(
        ":start rng definition:\n"
        "    type = ranmar\n"
        f"    initial seeds = {args.seed1} {args.seed2}\n"
        ":stop rng definition:\n\n"
    )
    text=text.replace(":start run control:",rng+":start run control:",1)

    if "@@" in text:
        raise SystemExit("Unresolved template token remains")
    if "set label = chamber_cavity 10 16 20" not in text:
        raise SystemExit("B1 cavity labels missing")
    if "z-planes = -50 -2 18" not in text:
        raise SystemExit("Benchmark explicit-air geometry missing")

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text)
    print(f"Wrote {out}")
    print(f"beam={args.beam}; tip={10*tip:.1f} mm")
    print("family role=predeclared Stage3H3 model-form endpoint; not manufacturer truth")
    print(f"cavity mass={mass:.15e} g")


if __name__=="__main__":
    main()
