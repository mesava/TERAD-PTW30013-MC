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

The CI smoke test has successfully built EGSnrc and `egs_chamber` and completed an official Co-60 Monte Carlo example.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI infrastructure | ✅ complete |
| 1 | SpekPy TERAD spectra fitted to measured Cu HVL | ✅ complete |
| 2 | PTW 30013 chamber geometry | 🔄 next |
| 3 | Published medium-kV benchmark | pending |
| 4 | Co-60 reference ratio | pending |
| 5 | TERAD k_Q,Co | pending |
| 6 | Spectrum / geometry sensitivity | pending |
| 7 | Field and SSD geometry correction k_g | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1 accepted nominal spectra

The accepted first-pass spectrum model uses SpekPy 2.5.4, a W target, nominal 20 degree anode angle, `kqp` physics and 0.5 keV bins. The unknown tube-head/inherent filtration is represented by a fitted non-negative equivalent-Al nuisance parameter; it is not a claimed physical TERAD filtration thickness.

| Beam | measured Cu HVL1 (mm) | initial model (mm) | fitted eq. Al (mm) | final model (mm) | mean E (keV) |
|---|---:|---:|---:|---:|---:|
| Q120 | 0.224000 | 0.207172 | 0.447246 | 0.224000 | 56.8438 |
| Q140 | 0.410000 | 0.388502 | 0.525157 | 0.410000 | 65.4082 |
| Q150 | 0.729000 | 0.723665 | 0.264108 | 0.729000 | 75.3565 |
| Q200 | 1.452000 | 1.452955 | 0.000000 | 1.452955 | 96.2098 |

Q200 is already only +0.0658% harder than the measured HVL with the known 1.0 mm Cu filter, so no unphysical negative added filtration is used. All four qualities satisfy the Stage 1 HVL acceptance criterion of ±0.5%.

See `docs/SPECTRUM_MODEL_STAGE1.md` and `results/spekpy_fit_summary.csv`.
