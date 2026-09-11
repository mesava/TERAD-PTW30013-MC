# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 1R — rebuild the TERAD production beam-quality input from the actual measured HVL provenance. Stage 3F published-benchmark sensitivity is complete and Stage 3G is paused. Production Co-60 and TERAD coefficients remain blocked until the TERAD HVLs are physically verified and the chamber benchmark is scientifically accepted.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

The individual chamber calibration is anchored to:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project keeps three physical problems separate:

1. intrinsic chamber beam-quality correction `k_Q`;
2. field/SSD/applicator correction `k_g`;
3. RW3-to-water correction.

They are not folded into one empirical coefficient.

## Controlled TERAD production inputs

Input control is documented in:

- `docs/TERAD_INPUT_BASELINE.md`;
- `docs/STAGE1R_HVL_PROVENANCE_AUDIT.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

The following machine settings are accepted:

| Beam | Tube voltage | Tube current | Known removable clinical filter |
|---|---:|---:|---|
| Q120 | 120 kV | 10 mA | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | 1.0 mm Cu |

Clinical applicators retained from the source workbook:

- F40 6 x 8 cm2;
- F40 4 x 15 cm2;
- F50 8 x 10 cm2.

The first intrinsic TERAD `k_Q` calculation will use F50 / 8 x 10 cm2 / SSD 50 cm. F40 conditions remain reserved for the separate `k_g` study.

### HVL provenance hold

The current workbook-derived HVLs are:

- Q120: 0.12198 mm Cu;
- Q140: 0.22715 mm Cu;
- Q150: 0.77398 mm Cu;
- Q200: 1.11223 mm Cu.

These values are now **PROVISIONAL / ON HOLD**, not accepted production targets. Stage 1R found that spreadsheet versions retain the same D0/D1/D2 readings but associate them with different absorber-thickness pairs `(x1,x2)`. Because the physical absorber stack is part of the measurement, the accepted HVL must be reconstructed from the actual Cu plate IDs used during each D1/D2 exposure or remeasured.

The earlier project HVL set 0.224 / 0.410 / 0.729 / 1.452 mm Cu is retained for historical traceability but is also not promoted merely because it agrees better with a spectrum model. Measurement provenance, not model convenience, decides the accepted values.

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

CI builds EGSnrc and `egs_chamber` reproducibly. Stage 3 additionally patches `egs_chamber` to compile `rad_compton1.mortran` so Radiative Compton corrections are explicitly enabled and verified.

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
| 1R | TERAD HVL provenance + production spectrum reconstruction | 🔴 active priority; HVL plate provenance hold |
| 2 | PTW 30013 geometry — Model A | 🟡 provisional |
| 3 | Published medium-kV benchmark | 🟡 Stage 3F complete; Stage 3G paused until Stage 1R is resolved |
| 4 | Co-60 reference ratio | ⏸ blocked |
| 5 | TERAD `k_Q,Co` | ⏸ blocked |
| 6 | TERAD production spectrum / chamber sensitivity | pending |
| 7 | Field / SSD / applicator correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1R — TERAD beam-quality reconstruction

### Stage 1R-1 — broad spectrum feasibility map ✅

Workflow run `34566147632` tested 108 combinations: four TERAD beams × SpekPy `kqp`, `spekcalc`, `spekpy-v1` × target-angle candidates 5–45 degrees while the clinical removable filter was held fixed.

Against the current provisional HVLs:

- Q120: no positive-filtration solution; closest base HVL ≈ 0.187 mm Cu versus 0.122 mm Cu;
- Q140: no positive-filtration solution; closest base HVL ≈ 0.358 mm Cu versus 0.227 mm Cu;
- Q150: generally representable;
- Q200: no positive-filtration solution; closest base HVL ≈ 1.349 mm Cu versus 1.112 mm Cu.

This ruled out simple re-fitting of the old positive-equivalent-Al model.

### Stage 1R-2 — tube-informed audit ✅

Workflow run `34566631576` used physically informed TERAD tube-head constraints: W target, 30 degree target-angle candidate and Be window sensitivity around 0.8 mm, with the clinical removable filters unchanged.

Representative `kqp`, 0.8 mm Be results:

- Q120: 0.196614 mm Cu (+61.2% vs provisional HVL);
- Q140: 0.373329 mm Cu (+64.4%);
- Q150: 0.705341 mm Cu (-8.9%);
- Q200: 1.401786 mm Cu (+26.0%).

The Be window hardens the spectrum slightly and therefore does not explain the provisional soft Q120/Q140/Q200 values.

### Stage 1R-3 — effective-kVp diagnostic ✅

Workflow run `34566781628` fixed W / 30 degrees / 0.8 mm Be / clinical removable filter and solved for the idealized constant-potential kVp required to reproduce each provisional HVL.

Representative `kqp` solutions:

- Q120: 83.88 kV for nominal 120 kV;
- Q140: 98.40 kV for nominal 140 kV;
- Q150: 162.20 kV for nominal 150 kV;
- Q200: 165.13 kV for nominal 200 kV.

The direction is inconsistent across the beam set, so a single common kVp calibration shift or ordinary generator-ripple explanation is inadequate.

### Stage 1R-4 — HVL provenance audit 🔴 current

Spreadsheet comparison found that the same D0/D1/D2 readings were later recomputed with different `x1/x2` absorber thicknesses.

Earlier assignments included, for example:

| Beam | Earlier x1 | Earlier x2 | Derived HVL |
|---|---:|---:|---:|
| Q120 | 0.210 | 0.323 | 0.219590 mm Cu |
| Q140 | 0.315 | 0.510 | 0.340355 mm Cu |
| Q150 | 0.510 | 0.615 | 0.534317 mm Cu |
| Q200 | 1.000 | 1.105 | 1.057981 mm Cu |

Later regrouped assignments used the same readings but changed the thicknesses to approximately 0.100/0.359, 0.207/0.362, 0.714/0.973 and 1.004/1.200 mm Cu, producing the current provisional HVLs.

Because D1 and D2 physically correspond to specific absorber stacks, production modelling is paused until the actual plate IDs used during each exposure are recovered or the HVLs are remeasured with plate IDs recorded contemporaneously.

See `docs/STAGE1R_HVL_PROVENANCE_AUDIT.md`.

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

See `docs/PTW30013_GEOMETRY_STAGE2.md`.

## Stage 3 — published PTW 30013 medium-kV benchmark

Stage 3 is independent of the TERAD clinical inputs. Its purpose is to test whether the Monte Carlo chamber/spectrum methodology reproduces published PTW 30013 behavior before production coefficients are trusted.

| Beam | Cu HVL (mm) | published kQ ENEA | published kQ THM |
|---|---:|---:|---:|
| CCRI100 | 0.1461 | 0.9537 | 0.9534 |
| CCRI135 | 0.4708 | 0.9754 | 0.9738 |
| CCRI180 | 0.9863 | 0.9857 | 0.9856 |
| CCRI250 | 2.5150 | 1.0000 | 1.0000 |

Primary pilot normalization:

`k_Q^MC = R_Q / R_250`, where `R_Q = D_w / D_cav`.

### Stage 3 chronology

**Stage 3A — XCSE diagnostic.** Increasing chamber XCSE reduced chamber uncertainty but left water uncertainty at ~4–5%.

**Stage 3B — VRT pilot.** IPSS/TmpPhsp + XCSE64 + RR64 reduced `u(D_w)` to ~0.63–0.69% at 5M histories and removed the water-score bottleneck.

**Stage 3C — first 200M benchmark.** Legacy HVL-refitted SpekPy `kqp` surrogate gave `k100,250 = 0.907674 ± 0.006748`, about -4.8% versus publication.

**Stage 3D — root-cause screen.** Published filtration + explicit paper `Emin` substantially improved the benchmark; forcing a cross-code HVL refit pushed it back toward the original disagreement.

**Stage 3E — 200M discrimination.** Best high-stat case was `pubemin_vac = 0.939163 ± 0.007024`, about -1.51% versus the published midpoint.

**Stage 3F — spectrum-engine / chamber-geometry sensitivity.** Completed successfully. At 50M histories the `kqp_modelA` central value was 0.953214 (1.49% MC uncertainty); `spekcalc` and `spekpy-v1` were lower, and wall/electrode/cavity perturbations showed percent-level sensitivity. Because this screen is statistically coarse and Stage 1R is now the production-data priority, Stage 3G high-stat follow-up is paused rather than used to tune Model A.

## Acceptance gates before production

Production Stage 4/5 is allowed only after both conditions are met:

1. TERAD beam-quality inputs are physically verified: actual D1/D2 absorber stacks are recovered or the HVLs are freshly remeasured, and Stage 1 production spectra reproduce the accepted HVLs without unphysical tuning;
2. the PTW 30013 / published-medium-kV benchmark is scientifically accepted with a justified uncertainty budget.

Only then will the project:

1. calculate the Co-60 reference ratio `R_Co`;
2. calculate TERAD Q120/Q140/Q150/Q200 ratios in water;
3. derive `k_Q,Co = R_Q / R_Co`;
4. quantify TERAD-specific spectrum/chamber sensitivity;
5. determine separate applicator/SSD correction `k_g` for F40/F50 conditions;
6. determine RW3-to-water correction;
7. combine results into final coefficients and uncertainty budget.
