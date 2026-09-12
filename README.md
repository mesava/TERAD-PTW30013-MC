# TERAD-PTW30013-MC

Monte Carlo project for deriving PTW 30013 chamber-specific beam-quality corrections for a TERAD kilovoltage therapy unit.

> **Canonical task:** `docs/CANONICAL_MC_TASK.md` and `data/terad_clinical_geometries.csv` define the user-supplied TERAD beam qualities, all 12 applicator combinations and the real RW3 setup. These inputs take priority over exploratory benchmark branches.

> **Current milestone:** **Stage 3H-3 Model B1 tip sensitivity is running**. Stage 3H-2 Model B0 completed successfully and showed that replacing the Model A effective 21.8 mm sensitive length by the public 23.0 mm PTW value shifts the weighted CCRI100/250 benchmark upward by about 1.15%, but does not yet validate the chamber model.

## Primary target

For quality Q:

`R_Q = (D_w / D_cav)_Q`

`k_Q,Co = R_Q / R_Co`

Individual chamber calibration anchor:

`N_D,w(Co-60) = 5.389e7 Gy/C`

for PTW 30013 SN 013488.

The project keeps separate:

1. chamber beam-quality response;
2. field/SSD/applicator response `k_g`;
3. RW3-to-water effect;
4. direct end-to-end checks in the actual RW3 geometry.

## Authoritative TERAD production baseline

| Beam | Tube voltage | Tube current | Measured HVL1 | Added clinical filter |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu |

Authoritative input files:

- `docs/CANONICAL_MC_TASK.md`
- `docs/TERAD_INPUT_BASELINE.md`
- `data/terad_input_baseline.csv`
- `data/beam_qualities.csv`
- `data/terad_clinical_geometries.csv`

The temporary Stage 1R branch based on 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu is superseded and is not part of production MC.

## The 12 real TERAD geometries

For **every** Q120/Q140/Q150/Q200 beam, all three applicators are full production calculations:

- F40 / SSD 40 cm / 6 x 8 cm2
- F40 / SSD 40 cm / 4 x 15 cm2
- F50 / SSD 50 cm / 8 x 10 cm2

Therefore the final clinical task contains **12 kV/applicator combinations**.

F50 is a real calculated configuration, not a substitute for the F40 applicators. After its own calculation it is also used as a convenient normalization denominator for relative `k_g` values.

## User-supplied RW3 geometry

- RW3 transverse size 30 x 30 cm2
- PTW 30013 horizontal
- chamber axis perpendicular to beam axis
- chamber centre/reference point on central axis
- stem directed right
- chamber centre at 2.0 cm water-equivalent depth
- 1.3 cm RW3 physically above the chamber body in the stated setup
- approximately 10 cm RW3 downstream
- lateral margin at least 10 cm
- SSD set by F40/F50 applicator
- applicator in contact with the RW3 surface

All 12 configurations will be calculated directly in RW3 in addition to the factorised water/geometry/RW3 analysis.

## Stage 0 — EGSnrc infrastructure ✅

Pinned official NRC EGSnrc commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Accepted benchmark transport/VRT architecture includes low-energy photon transport, Radiative Compton, exact BCA, IPSS/TmpPhsp, XCSE 64 and Russian Roulette survival 1/64.

## Stage 1 — TERAD production spectra ✅ accepted first pass

First-pass TERAD spectrum model uses SpekPy 2.5.4 with W reflection target, nominal 20 degree anode angle, `kqp` physics, known clinical filters and non-negative equivalent-Al nuisance filtration.

| Beam | Target HVL1 | Final HVL1 | Error |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Persistent record: `results/spekpy_fit_summary.csv`.

## Stage 2 — PTW 30013 Model A ❌ not benchmark-validated

Model A is a simplified public/aggregate surrogate:

- air-cavity radius 3.05 mm
- effective internal cavity length 21.80 mm
- Al central-electrode radius 0.575 mm
- retained electrode length 21.20 mm
- graphite 0.09 mm
- PMMA 0.335 mm

It does not model the real proprietary tip, guard, insulator, electrode base or stem transition.

## Stage 3 — published PTW 30013 benchmark

Published CCRI100/CCRI250 target midpoint:

`k100,250 = 0.95355`

with `R_Q = D_w / D_cav`.

### Stage 3G — high-stat `kqp` / Model A ❌

Run `34572944985`:

| Estimate | k100,250 | u(k) | delta vs target |
|---|---:|---:|---:|
| repA | 0.928161 | 0.005668 | -2.663% |
| repB | 0.927563 | 0.005660 | -2.725% |
| weighted | **0.927861** | **0.004005** | **-2.694%** |

The two 300M-per-beam replications agree, but the weighted result differs from the published target by about 6.4 sigma.

### Stage 3H-0 — spectrum fidelity ✅

Persistent result: `results/stage3h0_spectrum_fidelity.csv`.

`spekcalc` was selected as the primary benchmark surrogate because it best reproduces both published Cu HVL and kerma-weighted mean energy across CCRI100/135/180/250.

### Stage 3H-1 — paper-faithful SpekCalc + air48 / Model A ❌

Run `34580291967` completed successfully with two independent 200M-per-beam replications.

Persistent result: `results/stage3h1_summary.csv`.

| Estimate | k100,250 | u(k) | delta vs target |
|---|---:|---:|---:|
| repA | 0.932799 | 0.006960 | -2.176% |
| repB | 0.923246 | 0.006891 | -3.178% |
| weighted | **0.92797486** | **0.00489702** | **-2.6821%** |

The replications are mutually consistent (`z = +0.975`). The paper-faithful spectrum/air treatment therefore does not remove the Model A discrepancy.

### Stage 3H-2 — Model B0 public sensitive length 🟠 improved, not yet accepted

Run `34597238397` completed successfully.

Persistent result: `results/stage3h2_summary.csv`.

B0 changes exactly one confirmed public constraint relative to Model A:

- sensitive length: **21.8 mm -> 23.0 mm**.

The 21.2 mm electrode axial length is retained only as a legacy computational assumption and is not claimed as a manufacturer dimension.

| Estimate | k100,250 | u(k) | delta vs target |
|---|---:|---:|---:|
| repA | 0.931782 | 0.006809 | -2.283% |
| repB | 0.945731 | 0.006890 | -0.820% |
| weighted | **0.93867384** | **0.00484302** | **-1.560%** |

The replications are reasonably consistent (`z = -1.440`). Relative to Stage 3H-1 Model A, B0 shifts the weighted result by **+1.1529%**, closing about 42% of the previous gap, but the result remains about 3.07 sigma below the published midpoint.

Documentation: `docs/STAGE3H2_MODEL_B0.md`.

### Stage 3H-3 — Model B1 tip sensitivity 🟡 RUNNING

Workflow:

`.github/workflows/stage3h3-modelB1-tip-sensitivity.yml`

Run:

`34690628930`

Documentation:

`docs/STAGE3H3_MODEL_B1_TIP.md`

B1 preserves the B0 23.0 mm sensitive volume and introduces an asymmetric PMMA tip surrogate on the physical tip side.

Public constraints provide:

- sensitive length = 23.0 mm;
- reference point = 13.0 mm from the chamber tip.

Therefore the independently derived nominal tip-side distance is:

`13.0 - 23.0/2 = 1.5 mm`.

Predeclared B1 family:

| case | PMMA tip surrogate | role |
|---|---:|---|
| tip1p0 | 1.0 mm | lower sensitivity bound |
| tip1p5 | **1.5 mm** | nominal public-derived geometry |
| tip2p0 | 2.0 mm | upper sensitivity bound |

The nominal 1.5 mm case is fixed before results and is calculated with **two independent 120M/beam replications**. The 1.0 and 2.0 mm cases are 120M/beam screening bounds. No tip thickness will be selected simply because it reproduces 0.95355.

PMMA is used only as a first-order tip surrogate because it is the public outer-wall material. The true rounded tip shape, axial graphite continuation, adhesive, guard and insulator details remain unknown and are not represented as manufacturer truth.

If the independently defined nominal B1 geometry remains discrepant, the next declared steps are guard/insulator sensitivity and then stem-transition sensitivity.

See also:

- `docs/PTW30013_MODEL_B_PUBLIC_PLAN.md`
- `data/ptw30013_modelB_public_constraints.csv`

## Current project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ complete |
| 1 | TERAD production spectra | ✅ accepted first pass |
| 2 | PTW 30013 Model A | ❌ benchmark not validated |
| 3G | high-stat `kqp`/Model A benchmark | ❌ systematic fail |
| 3H-0 | spectrum fidelity | ✅ complete; SpekCalc selected |
| 3H-1 | paper-faithful SpekCalc + air48 / Model A | ❌ systematic fail |
| 3H-2 | Model B0 public-sensitive-length benchmark | 🟠 improved; not accepted |
| 3H-3 | Model B1 tip sensitivity | 🟡 running |
| 4 | Co-60 reference ratio | ⏸ blocked by benchmark acceptance |
| 5 | water calculations for all 12 TERAD configurations | ⏸ blocked by benchmark acceptance |
| 6 | TERAD spectrum/chamber sensitivity | pending |
| 7 | derive geometry-response ratios `k_g` | pending |
| 8 | RW3-to-water + 12 direct RW3 end-to-end calculations | pending |
| 9 | final coefficients and uncertainty budget | pending |

## Production path after benchmark acceptance

1. calculate `R_Co` in the Co-60 certificate reference geometry;
2. calculate water `R_Q` for all **12** TERAD kVp/applicator combinations;
3. calculate chamber-specific `k_Q,Co` results while retaining explicit results for all three applicators;
4. derive relative geometry-response ratios `k_g` only as bookkeeping from already calculated absolute responses;
5. quantify TERAD spectrum/chamber-model sensitivity;
6. model matched RW3 geometries for all 12 configurations;
7. quantify RW3-to-water effects;
8. perform direct end-to-end RW3 MC for all 12 configurations;
9. combine final coefficients and uncertainty budget.
