# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 3 benchmark refinement. TERAD Stage 1 is restored to **accepted first-pass** status using the original user-supplied measured HVLs 0.224 / 0.410 / 0.729 / 1.452 mm Cu. The temporary Stage 1R branch based on 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu is superseded.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

Individual chamber calibration:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project keeps separate:

1. intrinsic chamber beam-quality correction `k_Q`;
2. field/SSD/applicator correction `k_g`;
3. RW3-to-water correction.

## Authoritative TERAD production baseline

| Beam | Tube voltage | Tube current | Measured HVL1 | Known clinical filter |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu |

Authoritative files:

- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

Clinical applicators retained for all four Farmer-beam qualities:

- F40 6 x 8 cm2;
- F40 4 x 15 cm2;
- F50 8 x 10 cm2.

The first intrinsic TERAD `k_Q` calculation uses F50 / 8 x 10 cm2 / SSD 50 cm. F40 conditions are reserved for the separate `k_g` study.

The published CCRI100/135/180/250 benchmark beams are validation-only inputs and never redefine the TERAD baseline.

## Stage 1 — accepted TERAD spectrum model ✅

First-pass source model:

- SpekPy 2.5.4;
- W reflection target;
- nominal 20 degree anode angle;
- `kqp` physics;
- 0.5 keV bins;
- known clinical filter;
- non-negative equivalent-Al nuisance thickness where required.

The equivalent-Al term is a spectrum-model nuisance parameter and is not claimed to be measured inherent filtration.

Accepted results:

| Beam | Target HVL1 | Known-filter-only HVL | Eq. Al | Final HVL1 | Error |
|---|---:|---:|---:|---:|---:|
| Q120 | 0.224000 | 0.207172 | 0.447246 mm | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.388502 | 0.525157 mm | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.723665 | 0.264108 mm | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | 0.000000 mm | 1.452955 | +0.0658% |

All beams satisfy the <=0.5% HVL acceptance target.

Full record: `results/spekpy_fit_summary.csv`.

Approximate mean photon energies of the accepted first-pass spectra:

- Q120: 56.84 keV;
- Q140: 65.41 keV;
- Q150: 75.36 keV;
- Q200: 96.21 keV.

See `docs/SPECTRUM_MODEL_STAGE1.md`.

### Superseded Stage 1R branch

A temporary branch mistakenly promoted the unrelated values 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu. Runs `34566147632`, `34566631576`, and `34566781628` therefore tested the wrong TERAD input set. They are retained only as audit history and their physical conclusions do not apply to production TERAD spectra.

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
- chamber axis perpendicular to beam axis.

## EGSnrc baseline

Pinned official NRC EGSnrc commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Accepted Stage 3 VRT architecture:

- IPSS / `TmpPhsp = 1`;
- XCSE = 64;
- Russian Roulette survival = 1/64;
- `ESAVE = 0.512 MeV`;
- local XCSE zones for water and chamber scoring;
- independent RNG seeds for independent qualities.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI | ✅ complete |
| 1 | TERAD production spectra | ✅ accepted first pass |
| 2 | PTW 30013 geometry — Model A | 🟡 provisional |
| 3 | Published medium-kV benchmark | 🟡 Stage 3F complete; high-stat refinement still needed |
| 4 | Co-60 reference ratio | ⏸ blocked by Stage 3 acceptance |
| 5 | TERAD `k_Q,Co` | ⏸ blocked by Stage 3 acceptance |
| 6 | TERAD spectrum/chamber sensitivity | pending |
| 7 | Field / SSD / applicator correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 2 — PTW 30013 Model A

Model A first-pass geometry:

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

Model A does not claim exact proprietary tip, guard/dead-volume, electrode-base or stem construction. Those remain sensitivity terms.

## Stage 3 — published PTW 30013 medium-kV benchmark

Stage 3 is independent of TERAD clinical inputs and tests the MC chamber/spectrum methodology against published PTW 30013 behavior.

Published normalization:

`k_Q^MC = R_Q / R_250`, where `R_Q = D_w / D_cav`.

Chronology:

- Stage 3A: XCSE diagnostic;
- Stage 3B: accepted VRT architecture;
- Stage 3C: 200M legacy benchmark, `k100,250 = 0.907674 ± 0.006748`, showing a large spectral-surrogate discrepancy;
- Stage 3D: root-cause screen;
- Stage 3E: 200M discrimination, best high-stat `pubemin_vac = 0.939163 ± 0.007024`, about -1.51% versus published midpoint;
- Stage 3F: spectrum-engine / chamber-geometry sensitivity complete; 50M `kqp_modelA = 0.953214` with ~1.49% MC uncertainty, while geometry perturbations demonstrated percent-level sensitivity.

Stage 3F therefore requires selective high-stat confirmation before the benchmark gate is accepted. No chamber parameter will be tuned merely to force agreement.

## Acceptance gates before production Stage 4/5

Stage 1 is satisfied. The remaining primary gate is scientific acceptance of the PTW 30013 published benchmark with an adequate uncertainty budget.

After that the project will:

1. calculate `R_Co`;
2. calculate TERAD Q120/Q140/Q150/Q200 `R_Q` using the accepted Stage 1 spectra;
3. derive `k_Q,Co = R_Q / R_Co`;
4. quantify TERAD-specific spectrum/chamber sensitivity;
5. determine separate `k_g` for F40/F50 conditions;
6. determine RW3-to-water correction;
7. combine the final coefficients and uncertainty budget.
