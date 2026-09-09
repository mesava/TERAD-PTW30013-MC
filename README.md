# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

The individual chamber calibration is anchored to:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

## Measured TERAD beam qualities

| Beam | HVL | Known added filter |
|---|---:|---|
| 120 kV | 0.224 mm Cu | 4.0 mm Al |
| 140 kV | 0.410 mm Cu | 0.2 mm Cu |
| 150 kV | 0.729 mm Cu | 0.5 mm Cu |
| 200 kV | 1.452 mm Cu | 1.0 mm Cu |

## Reference geometries

**Co-60 certificate denominator**
- water
- SDD = 100 cm
- reference depth = 5 g/cm² H2O
- field = 10 x 10 cm² at the chamber reference plane

**TERAD kV first-pass reference geometry**
- water
- SSD = 50 cm
- PTW 30013 reference point at 2 cm depth
- field = 8 x 10 cm² at the phantom surface
- chamber axis perpendicular to beam axis

RW3 conversion and field/SSD geometry corrections are intentionally separated from the first k_Q calculation.

## EGSnrc baseline

The project is pinned initially to the official NRC EGSnrc 2026 master release commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

The first CI milestone is only an EGSnrc/egs_chamber build-and-smoke-test. Production Monte Carlo cases will be added after the official examples and input syntax are reproduced successfully.
