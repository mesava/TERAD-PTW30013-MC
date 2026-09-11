# Stage 1R — HVL provenance audit

## Why this audit was opened

Stage 1R feasibility work showed that the current spreadsheet-derived TERAD HVLs (0.12198, 0.22715, 0.77398 and 1.11223 mm Cu for Q120/Q140/Q150/Q200) are not consistently reproducible by physically informed tungsten-target spectrum models while the documented clinical removable filters are held fixed.

Before tuning a spectrum model to those values, the measurement provenance must therefore be checked.

## Raw readings are stable; absorber thickness assignment changed

Across the spreadsheet versions inspected, the same D0/D1/D2 readings are retained for the medium-energy beams. What changed is the absorber-thickness pair `(x1,x2)` associated with D1 and D2.

### Earlier spreadsheet assignment

| Beam | D0 mean | D1 mean | D2 mean | x1 (mm Cu) | x2 (mm Cu) | derived HVL (mm Cu) |
|---|---:|---:|---:|---:|---:|---:|
| Q120 | 126.4000 | 65.2000 | 45.1667 | 0.210 | 0.323 | 0.219590 |
| Q140 | 179.9500 | 93.0000 | 72.1167 | 0.315 | 0.510 | 0.340355 |
| Q150 | 216.9000 | 110.4500 | 102.0700 | 0.510 | 0.615 | 0.534317 |
| Q200 | 175.8000 | 90.1500 | 86.1167 | 1.000 | 1.105 | 1.057981 |

### Later regrouped assignment used by the current kQ workbook

| Beam | same D0/D1/D2 | x1 (mm Cu) | x2 (mm Cu) | derived HVL (mm Cu) |
|---|---|---:|---:|---:|
| Q120 | yes | 0.100 | 0.359 | 0.121981 |
| Q140 | yes | 0.207 | 0.362 | 0.227154 |
| Q150 | yes | 0.714 | 0.973 | 0.773983 |
| Q200 | yes | 1.004 | 1.200 | 1.112231 |

The log-linear interpolation itself is internally consistent. The scientific question is whether the later `x1/x2` stacks are the physical absorber stacks that were actually present when D1 and D2 were measured.

Changing `x1/x2` after the exposure while retaining the same D1/D2 changes the physical meaning of the measurement and therefore cannot be accepted without provenance for the plate IDs used during each exposure.

## Stage 1R computational evidence

### Stage 1R-1 feasibility map

Run `34566147632` scanned 108 cases: four TERAD beams × SpekPy `kqp/spekcalc/spekpy-v1` × target-angle candidates 5–45 degrees, while the documented clinical removable filter was held fixed.

Using the current later-regrouped HVLs:

- Q120: no fit-capable case; closest base HVL about 0.187 mm Cu versus 0.122 mm Cu;
- Q140: no fit-capable case; closest base HVL about 0.358 mm Cu versus 0.227 mm Cu;
- Q150: many fit-capable cases;
- Q200: no fit-capable case; closest base HVL about 1.349 mm Cu versus 1.112 mm Cu.

### Stage 1R-2 tube-informed audit

Run `34566631576` used a physically informed candidate head: W target, 30 degree target angle, Be exit window 0/0.7/0.8/0.9 mm, and the documented removable clinical filter. Adding the 0.8 mm Be window slightly hardened the spectra and therefore did not solve the Q120/Q140/Q200 mismatch.

Representative `kqp` results with 0.8 mm Be:

- Q120: 0.196614 mm Cu (+61.2% vs current spreadsheet HVL);
- Q140: 0.373329 mm Cu (+64.4%);
- Q150: 0.705341 mm Cu (-8.9%);
- Q200: 1.401786 mm Cu (+26.0%).

### Stage 1R-3 effective-kVp diagnostic

Run `34566781628` fixed W, 30 degrees, 0.8 mm Be and the clinical removable filter, then solved for the idealized constant-potential kVp required to reproduce the current spreadsheet HVL.

For `kqp` the required effective voltages were approximately:

- Q120: 83.88 kV instead of 120 kV;
- Q140: 98.40 kV instead of 140 kV;
- Q150: 162.20 kV instead of 150 kV;
- Q200: 165.13 kV instead of 200 kV.

The direction is not even consistent across the four beams. A single voltage-calibration error or ordinary generator ripple cannot plausibly explain this pattern.

## Current scientific decision

The current numeric HVL set remains stored for traceability but is **PROVISIONAL / ON HOLD** for production Monte Carlo until the physical absorber stacks used for D1 and D2 are recovered or the HVLs are remeasured.

Do not tune the TERAD spectrum to the current HVLs and do not generate production `k_Q,Co` from them yet.

The following remain accepted independently of the HVL provenance issue:

- nominal tube voltages and currents;
- documented removable clinical filters;
- clinical applicator inventory;
- PTW 30013 identity/calibration;
- Stage 3 published-benchmark work, because it uses independent published CCRI beams.

## Data required to close the hold

For each of Q120/Q140/Q150/Q200, recover one of the following:

1. the actual Cu plate IDs/composition used for D1 and D2 during the original HVL exposure, allowing the measured thicknesses to be reconstructed from calibration certificates; or
2. a fresh narrow-beam HVL measurement with the plate IDs recorded contemporaneously.

Once that is available, recalculate HVL directly from the original/fresh D0, D1, D2 and the verified physical `x1,x2`, then update `data/terad_input_baseline.csv` and rebuild Stage 1 spectra.
