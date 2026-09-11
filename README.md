# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 1R — reconstruct physically plausible TERAD source-spectrum families constrained by the user-supplied measured HVLs. Stage 3F published-benchmark sensitivity is complete and Stage 3G is paused while the production TERAD spectra are rebuilt.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

The individual chamber calibration is anchored to:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project keeps three physical problems separate:

1. intrinsic chamber beam-quality correction `k_Q`;
2. field/SSD/applicator correction `k_g`;
3. RW3-to-water correction.

## Authoritative TERAD production baseline

The single source of truth is:

- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

| Beam | Tube voltage | Tube current | Authoritative measured HVL1 | Known clinical filter |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.12198 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.22715 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.77398 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.11223 mm Cu** | 1.0 mm Cu |

These HVLs are accepted directly as measured beam-quality inputs. The absorber thicknesses historically used to determine them are not required by the MC source model once the HVLs themselves are accepted.

Clinical applicators retained for all four Farmer-beam qualities:

- F40 6 x 8 cm2;
- F40 4 x 15 cm2;
- F50 8 x 10 cm2.

The first intrinsic TERAD `k_Q` calculation uses F50 / 8 x 10 cm2 / SSD 50 cm. F40 applicators remain reserved for the later separate `k_g` study.

The published CCRI100/135/180/250 benchmark beams are validation-only inputs and must never overwrite the TERAD baseline.

## Why HVL is enough to continue Stage 1R

For MC, the measured HVL is a constraint on the incident photon spectrum. Historical `x1/x2` plate thicknesses belong to the measurement procedure, not to the production MC geometry.

HVL alone does not uniquely specify a spectrum. Therefore Stage 1R must not attempt to recover the old absorber stacks. Instead it must construct a bounded family of spectra that all preserve:

- the authoritative nominal kVp;
- TERAD tube/head information where known;
- the known clinical removable filter;
- the authoritative measured HVL.

Any residual difference among spectra sharing the same kVp/filter/HVL is treated as spectrum-shape uncertainty and propagated into `D_w/D_cav` and `k_Q,Co`.

## Reference geometries

**Co-60 certificate denominator**
- water;
- SDD = 100 cm;
- reference depth = 5 g/cm2 H2O;
- field = 10 x 10 cm2 at the chamber reference plane.

**TERAD first intrinsic `k_Q` geometry**
- water;
- SSD = 50 cm;
- F50 applicator;
- field = 8 x 10 cm2 at phantom surface;
- PTW 30013 reference point at 2 cm depth;
- chamber axis perpendicular to the beam axis.

## EGSnrc baseline

The project is pinned to official NRC EGSnrc commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

CI builds EGSnrc and `egs_chamber` reproducibly. Stage 3 patches `egs_chamber` so Radiative Compton corrections are explicitly enabled and verified.

Accepted Stage 3 VRT architecture:

- IPSS / `TmpPhsp = 1`;
- XCSE = 64;
- Russian Roulette survival = 1/64;
- `ESAVE = 0.512 MeV`;
- local XCSE zones for both water and chamber scoring;
- independent RNG seeds for independent high-stat benchmark qualities.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI infrastructure | ✅ complete |
| 1R | TERAD production spectrum reconstruction from authoritative HVLs | 🟡 active priority |
| 2 | PTW 30013 geometry — Model A | 🟡 provisional |
| 3 | Published medium-kV benchmark | 🟡 Stage 3F complete; Stage 3G paused |
| 4 | Co-60 reference ratio | ⏸ blocked by Stages 1R and 3 |
| 5 | TERAD `k_Q,Co` | ⏸ blocked by Stages 1R and 3 |
| 6 | TERAD spectrum/chamber sensitivity | pending |
| 7 | Field / SSD / applicator correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1R — TERAD spectrum reconstruction

### Stage 1R-1 — broad spectrum feasibility map ✅

Run `34566147632` tested four beams × SpekPy `kqp/spekcalc/spekpy-v1` × target angle 5–45 degrees with the clinical filter held fixed.

The restricted family could not reproduce Q120/Q140/Q200 by adding only non-negative equivalent filtration; Q150 was representable. This means the restricted model family is inadequate. It does not invalidate the measured HVLs.

### Stage 1R-2 — tube-informed audit ✅

Run `34566631576` tested W target, candidate 30 degree target angle, Be-window sensitivity around 0.8 mm and the known clinical filters. The window hardened the simple model slightly and did not close the Q120/Q140/Q200 gap.

Representative `kqp`, 0.8 mm Be predictions:

- Q120: 0.196614 mm Cu vs measured 0.121980;
- Q140: 0.373329 mm Cu vs measured 0.227150;
- Q150: 0.705341 mm Cu vs measured 0.773980;
- Q200: 1.401786 mm Cu vs measured 1.112230.

### Stage 1R-3 — effective-kVp diagnostic ✅

Run `34566781628` showed that a simple common voltage shift is not an adequate explanation of the discrepancy. That result is retained only as evidence that nominal-kVp-preserving spectral reconstruction is preferable to replacing the clinical kVp with arbitrary effective values.

### Stage 1R-4 — next step: same-HVL spectrum family

The next production task is to generate, for each Q120/Q140/Q150/Q200 beam, multiple candidate spectra that all preserve nominal kVp, known clinical filtration and the measured HVL, while differing in otherwise plausible spectral shape.

Candidate families will be compared by:

- exact HVL agreement;
- mean energy and low/high-energy fluence balance;
- any additional independent beam-quality data available;
- impact on `D_w/D_cav` in the PTW 30013 calculation.

The spread in `D_w/D_cav` across accepted same-HVL spectra becomes an explicit Stage 6 spectrum-model uncertainty rather than hidden tuning.

## Stage 2 — PTW 30013 Model A

Model A is a transparent public-volume-constrained first-pass geometry:

- air-cavity radius = 3.05 mm;
- internal cavity length = 21.80 mm;
- Al central-electrode radius = 0.575 mm;
- Al electrode length = 21.20 mm;
- graphite thickness = 0.09 mm;
- PMMA thickness = 0.335 mm.

Approximate aggregate volumes:

- internal cavity = 0.63710 cm3;
- central electrode = 0.02202 cm3;
- net air cavity = 0.61508 cm3.

Model A does not claim exact proprietary tip, guard/dead-volume, electrode-base or stem construction. Those are explicit sensitivity terms.

## Stage 3 — published PTW 30013 medium-kV benchmark

Stage 3 is independent of TERAD clinical inputs and tests the MC chamber/spectrum methodology against published PTW 30013 behavior.

Published normalization:

`k_Q^MC = R_Q / R_250`, where `R_Q = D_w / D_cav`.

Chronology:

- Stage 3A: XCSE diagnostic;
- Stage 3B: accepted VRT architecture;
- Stage 3C: 200M legacy benchmark, large spectral-surrogate discrepancy;
- Stage 3D: root-cause screen;
- Stage 3E: 200M discrimination, best high-stat `pubemin_vac = 0.939163 ± 0.007024`;
- Stage 3F: spectrum-engine / chamber-geometry sensitivity complete; 50M `kqp_modelA` central value 0.953214 with 1.49% MC uncertainty; Stage 3G high-stat follow-up paused while Stage 1R is prioritized.

## Acceptance gates before production

Production Stage 4/5 starts only after both conditions are met:

1. Stage 1R provides accepted TERAD spectra/families reproducing the authoritative Q120/Q140/Q150/Q200 HVLs without changing the clinical beam settings;
2. the PTW 30013 published-medium-kV benchmark is scientifically accepted with a justified uncertainty budget.

Then the project will calculate `R_Co`, TERAD `R_Q`, derive `k_Q,Co`, quantify spectrum/chamber sensitivity, determine separate `k_g`, determine RW3-to-water correction, and combine the final uncertainty budget.
