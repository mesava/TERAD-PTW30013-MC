#!/usr/bin/env python3
"""Validate the aggregate geometry invariants of PTW 30013 Model A."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "data" / "ptw30013_modelA.json").read_text())

r = float(CFG["cavity_radius_cm"])
L = float(CFG["internal_cavity_length_cm"])
re = float(CFG["central_electrode_radius_cm"])
Le = float(CFG["central_electrode_length_cm"])
rho_air = float(CFG["air_density_521icru_g_cm3"])

V_internal = math.pi * r * r * L
V_electrode = math.pi * re * re * Le
V_net = V_internal - V_electrode
m_air = V_net * rho_air

ref_internal = float(CFG["published_internal_cavity_volume_cm3"])
ref_electrode = float(CFG["published_central_electrode_volume_cm3"])
ref_net = float(CFG["published_net_cavity_volume_cm3"])

print("PTW 30013 Model A geometry invariants")
print(f"internal cavity volume : {V_internal:.9f} cm3 (target {ref_internal:.7f})")
print(f"central electrode vol. : {V_electrode:.9f} cm3 (target {ref_electrode:.7f})")
print(f"net air cavity volume  : {V_net:.9f} cm3 (target {ref_net:.7f})")
print(f"AIR521ICRU cavity mass : {m_air:.12e} g")

# The fitted lengths were derived from rounded aggregate volumes, so keep a
# tight but non-zero tolerance against those rounded publication values.
assert abs(V_internal - ref_internal) <= 2.0e-5
assert abs(V_electrode - ref_electrode) <= 2.0e-5
assert abs(V_net - ref_net) <= 3.0e-5

# Compare with a literal interpretation of the public 23 mm cylinder. This is
# diagnostic only; it is expected NOT to equal the nominal 0.6 cm3 volume.
L_public = float(CFG["public_ptw_sensitive_length_cm"])
V_public_gross = math.pi * r * r * L_public
V_public_net_full_electrode = V_public_gross - math.pi * re * re * L_public
print(f"public 23 mm gross cyl.: {V_public_gross:.9f} cm3")
print(f"public 23 mm net cyl.  : {V_public_net_full_electrode:.9f} cm3")
print("Model A validation passed.")
