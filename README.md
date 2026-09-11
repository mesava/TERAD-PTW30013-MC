# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Canonical task:** `docs/CANONICAL_MC_TASK.md` and `data/terad_clinical_geometries.csv` define the user-supplied TERAD beam qualities, all 12 applicator combinations and the real RW3 chamber setup. These inputs take priority over later exploratory branches.

> **Current milestone:** **Stage 3G high-stat Model A replication is running**. TERAD Stage 1 is accepted first-pass using the original user-supplied measured HVLs **0.224 / 0.410 / 0.729 / 1.452 mm Cu**. The temporary Stage 1R branch based on 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu is superseded.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

Individual chamber calibration:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project keeps separate:

1. intrinsic chamber beam-quality correction `k_Q`;
2. field/SSD/applicator correction `k_g`;
3. RW3-to-water correction;
4. direct end-to-end checks in the actual RW3 measurement geometry.

## Authoritative TERAD production baseline

| Beam | Tube voltage | Tube current | Measured HVL1 | Known clinical filter |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu |

Authoritative files:

- `docs/CANONICAL_MC_TASK.md`;
- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`;
- `data/terad_clinical_geometries.csv`.

## Real clinical TERAD geometries

For **every** Q120/Q140/Q150/Q200 quality, all three applicators are equal members of the production task and each must be calculated explicitly:

- F40 / SSD 40 cm / 6 x 8 cm2;
- F40 / SSD 40 cm / 4 x 15 cm2;
- F50 / SSD 50 cm / 8 x 10 cm2.

Therefore production MC contains **12 real kV/applicator combinations**.

The supplied RW3 setup is:

- RW3 transverse size 30 x 30 cm2;
- PTW 30013 horizontal, axis perpendicular to beam axis;
- chamber centre on central axis;
- stem to the right;
- chamber centre at 2.0 cm water-equivalent depth;
- 1.3 cm RW3 physically above the chamber body in the stated setup;
- approximately 10 cm RW3 downstream;
- lateral margin at least 10 cm;
- applicator pressed directly against RW3 surface.

**F50 / 8 x 10 / SSD 50 is a real clinical configuration and is calculated in full for every kVp.** In addition, after its own calculation it is used as the mathematical normalization baseline for expressing the relative field/SSD/applicator response `k_g` of the two F40 configurations. Setting `k_g(F50)=1` is therefore only a normalization convention after the F50 response has been calculated; it is not an assumption that removes the F50 calculation.

Final work includes direct end-to-end MC checks for **all 12 RW3 configurations**, including all four F50 cases.

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

Approximate mean photon energies:

- Q120: 56.84 keV;
- Q140: 65.41 keV;
- Q150: 75.36 keV;
- Q200: 96.21 keV.

See `docs/SPECTRUM_MODEL_STAGE1.md`.

### Superseded Stage 1R branch

Runs `34566147632`, `34566631576`, and `34566781628` used the wrong temporary HVL set and are retained only as audit history. Their physical conclusions do not apply to production TERAD spectra.

## Calculation structure for the three clinical applicators

**Co-60 certificate denominator**

- water;
- SDD = 100 cm;
- reference depth = 5 g/cm2 H2O;
- field = 10 x 10 cm2 at chamber reference plane.

For each TERAD quality Q, the project calculates the three supplied clinical configurations explicitly in water and later again in the matched RW3 geometry:

1. **F50 / SSD 50 cm / 8 x 10 cm2**;
2. **F40 / SSD 40 cm / 6 x 8 cm2**;
3. **F40 / SSD 40 cm / 4 x 15 cm2**.

The chamber reference point is at 2 cm depth in the water calculation corresponding to the specified experimental chamber-centre depth, with chamber axis perpendicular to beam axis.

For bookkeeping only, the calculated F50 water response is chosen as the normalization denominator for geometry-response ratios:

`k_g,Q(F50 8x10) = 1` by definition,

`k_g,Q(F40 6x8) = R_Q(F40 6x8) / R_Q(F50 8x10)`,

`k_g,Q(F40 4x15) = R_Q(F40 4x15) / R_Q(F50 8x10)`.

This normalization does not replace the F50 result. The F50 `R_Q`, `k_Q,Co`, RW3 response and end-to-end result are all explicit outputs.

## EGSnrc baseline

Pinned official NRC EGSnrc commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Accepted Stage 3 VRT architecture:

- IPSS / `TmpPhsp = 1`;
- XCSE = 64;
- Russian Roulette survival = 1/64;
- `ESAVE = 0.512 MeV`;
- local XCSE zones for water and chamber scoring;
- independent RNG seeds for independent qualities and replications.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI | ✅ complete |
| 1 | TERAD production spectra | ✅ accepted first pass |
| 2 | PTW 30013 geometry — Model A | 🟡 provisional |
| 3 | Published medium-kV benchmark | 🟡 **Stage 3G high-stat replication running** |
| 4 | Co-60 reference ratio | ⏸ blocked by Stage 3 acceptance |
| 5 | TERAD water calculations for all three applicators at each kVp | ⏸ blocked by Stage 3 acceptance |
| 6 | TERAD spectrum/chamber sensitivity | pending |
| 7 | Geometry-response ratios `k_g` derived from the three calculated applicators | pending |
| 8 | RW3-to-water + 12 direct RW3 end-to-end checks | pending |
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

- **Stage 3A:** XCSE diagnostic;
- **Stage 3B:** accepted VRT architecture;
- **Stage 3C:** 200M legacy benchmark, `k100,250 = 0.907674 ± 0.006748`, showing a large spectral-surrogate discrepancy;
- **Stage 3D:** root-cause screen;
- **Stage 3E:** 200M discrimination, `pubemin_vac = 0.93916265 ± 0.00702366`, about -1.51% versus published midpoint 0.95355;
- **Stage 3F:** spectrum-engine / chamber-geometry screen; 50M `kqp_modelA = 0.953214` with ~1.49% MC uncertainty. Geometry perturbations showed percent-level sensitivity, but they were screening tests and are not used to tune Model A.

### Stage 3G — high-stat Model A replication 🟡 RUNNING

Workflow: `.github/workflows/stage3g-highstat-modelA-replication.yml`.

Design:

- preferred `kqp` / published-filtration / published-`Emin` benchmark spectrum;
- Model A chamber unchanged;
- CCRI100 and CCRI250 only;
- **two independent replications** (`repA`, `repB`);
- **300,000,000 histories per beam per replication**;
- four independent RNG seed pairs;
- same pinned EGSnrc, IPSS/TmpPhsp, XCSE64 and RR64 as the accepted benchmark architecture;
- explicit check that the Stage 3F `kqp` numeric spectrum is identical to the Stage 3E `published_emin` spectrum before simulation.

The summary job calculates:

1. `k100,250` and uncertainty for each 300M replication;
2. repA-versus-repB consistency z-score;
3. inverse-variance Stage 3G weighted estimate;
4. consistency with Stage 3E high-stat result;
5. an optional pooled Stage 3E + Stage 3G estimate;
6. deviation and z-score versus the published target 0.95355.

No chamber geometry parameter is changed in Stage 3G and no parameter is tuned to force agreement.

## Acceptance gates before production Stage 4/5

Stage 1 is satisfied. The remaining primary gate is scientific acceptance of the PTW 30013 published benchmark with an adequate uncertainty budget.

After that the project will:

1. calculate `R_Co`;
2. calculate `R_Q` in water for **all 12 TERAD kVp/applicator combinations**;
3. derive the F50 `k_Q,Co` result for each kVp and the corresponding F40 geometry-response ratios, while retaining the absolute calculated response for every applicator;
4. quantify TERAD-specific spectrum/chamber sensitivity;
5. calculate matched RW3 responses for all three applicators at all four kVp;
6. determine RW3-to-water effects;
7. perform direct end-to-end MC for all 12 actual RW3 configurations;
8. combine final coefficients and uncertainty budget.
