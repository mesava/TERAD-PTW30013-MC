# TERAD-PTW30013-MC

Monte Carlo project for deriving PTW 30013 chamber-specific beam-quality corrections for a TERAD kilovoltage therapy unit.

> **Canonical task:** `docs/CANONICAL_MC_TASK.md` and `data/terad_clinical_geometries.csv` define the user-supplied TERAD beam qualities, all 12 applicator combinations and the real RW3 setup. These inputs take priority over exploratory benchmark branches.

> **Current milestone:** **Stage 3H-1 launched** — paper-faithful benchmark test using the best available `spekcalc` surrogate, explicit additional 48 cm air transport, and unchanged PTW 30013 Model A. Stage 3G is complete and showed a statistically significant systematic benchmark failure for the `kqp`/Model A combination.

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

F50 is not a substitute for the other applicators. It is a real calculated configuration. After calculation it is also used as a convenient normalization denominator for relative `k_g` values:

`k_g,Q(F50 8x10) = 1` by definition after its response is calculated.

The absolute F50 `R_Q`, `k_Q,Co`, water result, RW3 result and end-to-end result remain explicit outputs.

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

Accepted benchmark transport/VRT architecture includes:

- `Pcut = 0.001 MeV`
- `Ecut = 0.512 MeV`
- mcdf-xcom photon cross sections
- Rayleigh, bound Compton, atomic relaxations and Radiative Compton on
- NIST bremsstrahlung, KM angular sampling, spin effects, EII `ik`
- exact BCA, ESTEPE 0.25, XIMAX 0.5, skin depth 3
- IPSS / `TmpPhsp`
- XCSE 64
- Russian Roulette survival 1/64
- ESAVE 0.512 MeV

## Stage 1 — TERAD production spectra ✅ accepted first pass

First-pass spectrum model:

- SpekPy 2.5.4
- W reflection target
- nominal 20 degree anode angle
- `kqp` physics
- 0.5 keV bins
- known clinical filter
- non-negative equivalent-Al nuisance term where required

| Beam | Target HVL1 | Known-filter-only HVL | Eq. Al | Final HVL1 | Error |
|---|---:|---:|---:|---:|---:|
| Q120 | 0.224000 | 0.207172 | 0.447246 mm | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.388502 | 0.525157 mm | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.723665 | 0.264108 mm | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | 0.000000 mm | 1.452955 | +0.0658% |

All four satisfy the <=0.5% first-pass HVL criterion.

Persistent record: `results/spekpy_fit_summary.csv`.

## Stage 2 — PTW 30013 Model A 🟡 provisional / not benchmark-validated

Public/aggregate-constrained first-pass geometry:

- air-cavity radius 3.05 mm
- internal cavity length 21.80 mm
- Al central-electrode radius 0.575 mm
- Al electrode length 21.20 mm
- graphite 0.09 mm
- PMMA 0.335 mm
- internal cavity approximately 0.63710 cm3
- central electrode approximately 0.02202 cm3
- net air cavity approximately 0.61508 cm3

Model A deliberately does **not** claim the exact proprietary tip, guard, insulator, electrode-base or stem construction. The current benchmark work shows that those simplifications may be clinically relevant at medium kV.

## Stage 3 — published PTW 30013 benchmark

The Czarnecki benchmark branch is independent of the TERAD clinical inputs. It validates the MC chamber/spectrum methodology before production coefficients are trusted.

Published CCRI100/CCRI250 target midpoint:

`k100,250 = 0.95355`

with `R_Q = D_w / D_cav`.

### Stage 3A–3F — development and screening

- Stage 3A: XCSE diagnostic
- Stage 3B: accepted VRT architecture
- Stage 3C: first 200M legacy benchmark, large disagreement
- Stage 3D: root-cause spectrum/air screen
- Stage 3E: 200M discrimination; `pubemin_vac = 0.93916265 +/- 0.00702366`
- Stage 3F: spectrum-engine and simplified chamber-geometry sensitivity at 50M

The Stage 3F `kqp_modelA` central value of about 0.9532 was only a low-stat screening result and was not accepted as validation.

### Stage 3G — high-stat `kqp` / Model A replication ❌ systematic benchmark failure

Run `34572944985` completed successfully with two independent 300M-per-beam replications:

| Estimate | k100,250 | u(k) | delta vs 0.95355 |
|---|---:|---:|---:|
| repA | 0.928161 | 0.005668 | -2.663% |
| repB | 0.927563 | 0.005660 | -2.725% |
| Stage 3G weighted | **0.927861** | **0.004005** | **-2.694%** |

repA and repB agree with each other (`z approximately 0.075`), while the weighted result differs from the published target by about 6.4 sigma. Therefore increasing histories for the same `kqp`/Model A combination is not useful.

### Stage 3H-0 — benchmark spectrum fidelity ✅

Persistent result: `results/stage3h0_spectrum_fidelity.csv`

Documentation: `docs/STAGE3H_BENCHMARK_REFINEMENT.md`

The published benchmark provides both Cu HVL and kerma-weighted mean energy. Stage 3H-0 tested `kqp`, `spekcalc` and `spekpy-v1` against both observables for CCRI100/135/180/250.

`spekcalc` is the best overall surrogate:

| Beam | SpekCalc HVL error | SpekCalc kerma-mean-energy error | kqp HVL error | kqp kerma-mean-energy error |
|---|---:|---:|---:|---:|
| CCRI100 | +0.928% | -0.075% | +0.940% | -0.588% |
| CCRI135 | -0.749% | +0.264% | -3.136% | -1.419% |
| CCRI180 | -1.431% | +0.228% | -5.838% | -2.452% |
| CCRI250 | -1.793% | -0.017% | -7.080% | -3.642% |

Decision: **`spekcalc` is the primary benchmark spectrum surrogate from Stage 3H onward.** `kqp` and `spekpy-v1` remain diagnostic alternatives.

### Stage 3H-1 — paper-faithful `spekcalc` + air48 / Model A 🟡 launched

Workflow:

`.github/workflows/stage3h1-paperfaithful-spekcalc-modelA.yml`

Design:

- `spekcalc` spectrum surrogate
- W target, 30 degree anode
- published filters and published `Emin`
- first 50 cm air included in spectrum generation
- additional **48 cm air explicitly transported** before the water surface
- unchanged PTW 30013 Model A
- CCRI100 and CCRI250
- two independent replications
- 200,000,000 histories per beam per replication
- pinned EGSnrc and accepted VRT/transport settings

This is intentionally a clean test of Model A after correcting benchmark spectrum/air fidelity. No chamber dimension is fitted to the published target.

If Stage 3H-1 still fails, Stage 3H-2 will move to **Model B-public**: a more realistic PTW 30013 geometry constrained by public dimensions/materials, with unknown proprietary tip/guard/stem details treated transparently as sensitivity parameters rather than invented manufacturer dimensions.

## Current project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ complete |
| 1 | TERAD production spectra | ✅ accepted first pass |
| 2 | PTW 30013 Model A | 🟡 provisional; benchmark not validated |
| 3G | high-stat `kqp`/Model A benchmark | ❌ systematic fail |
| 3H-0 | spectrum fidelity | ✅ complete; `spekcalc` selected |
| 3H-1 | paper-faithful `spekcalc` + air48 / Model A | 🟡 launched |
| 3H-2 | Model B-public refinement | pending H-1 result |
| 4 | Co-60 reference ratio | ⏸ blocked by benchmark acceptance |
| 5 | water calculations for all 12 TERAD configurations | ⏸ blocked by benchmark acceptance |
| 6 | TERAD spectrum/chamber sensitivity | pending |
| 7 | derive geometry-response ratios `k_g` from explicit applicator calculations | pending |
| 8 | RW3-to-water + 12 direct RW3 end-to-end calculations | pending |
| 9 | final coefficients and uncertainty budget | pending |

## Production path after benchmark acceptance

1. calculate `R_Co` in the Co-60 certificate reference geometry;
2. calculate water `R_Q` for all **12** TERAD kVp/applicator combinations;
3. calculate the four F50 `k_Q,Co` values and retain absolute results for both F40 geometries;
4. express F40 geometry-response ratios relative to calculated F50 responses for bookkeeping;
5. quantify TERAD spectrum/chamber-model sensitivity;
6. model matched RW3 geometries for all 12 configurations;
7. quantify RW3-to-water effects;
8. perform direct end-to-end RW3 MC for all 12 configurations;
9. combine final coefficients and uncertainty budget.
