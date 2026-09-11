# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 3F — spectrum-engine and PTW 30013 geometry sensitivity for the published benchmark. In parallel, TERAD Stage 1 has been **reopened** after correcting the authoritative clinical HVL baseline. Production Co-60/TERAD coefficients remain blocked until both the benchmark model and the rebuilt TERAD spectra are accepted.

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

## Authoritative TERAD production baseline

The single source of truth is:

- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

| Beam | Tube voltage | Tube current | Measured HVL1 | Known added filter |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.12198 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.22715 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.77398 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.11223 mm Cu** | 1.0 mm Cu |

Clinical applicators retained from the source workbook for all four Farmer-beam qualities:

- F40 6 x 8 cm2;
- F40 4 x 15 cm2;
- F50 8 x 10 cm2.

The first intrinsic TERAD `k_Q` calculation uses the real clinical reference condition F50 / 8 x 10 cm2 / SSD 50 cm. F40 applicators are preserved for the later separate `k_g` study.

The published CCRI100/135/180/250 benchmark beams are **validation-only inputs** and must never overwrite the TERAD baseline above.

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
| 1 | TERAD production spectra | 🔴 reopened after authoritative HVL correction |
| 2 | PTW 30013 geometry — Model A | 🟡 provisional; benchmark sensitivity in progress |
| 3 | Published medium-kV benchmark | 🟡 Stage 3F spectrum/geometry sensitivity running |
| 4 | Co-60 reference ratio | ⏸ blocked by Stages 1 and 3 |
| 5 | TERAD `k_Q,Co` | ⏸ blocked by Stages 1 and 3 |
| 6 | TERAD production spectrum / chamber sensitivity | pending |
| 7 | Field / SSD / applicator correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1 — TERAD spectrum model: REOPENED

The earlier first-pass Stage 1 used SpekPy 2.5.4, W target, nominal 20 degree anode angle, `kqp` physics and a fitted non-negative equivalent-Al nuisance thickness.

That model had been accepted against an older HVL set:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

Those values are superseded and must not be used for final TERAD coefficients.

With the corrected authoritative HVLs, the known-filter-only legacy SpekPy model is already harder than the measured beam for Q120, Q140 and Q200. Positive Al can only increase HVL, so the old one-parameter fitting family cannot represent those qualities without an unphysical negative filtration.

Therefore:

- old `spectra/Qxxx.*` files are retained only as legacy audit artifacts;
- `results/spekpy_fit_summary.csv` is also legacy/superseded;
- Stage 1 is reopened;
- no production TERAD `k_Q,Co` may use those spectra.

The diagnostic script `scripts/diagnose_terad_stage1_baseline.py` and workflow `.github/workflows/terad-stage1-baseline-diagnostic.yml` explicitly test this model-family feasibility against the authoritative baseline.

The Stage 1 rebuild will test spectrum physics family, anode-angle assumption, window/inherent-filtration representation and other justified spectral assumptions without changing the measured HVL or known clinical filter merely to force agreement.

See `docs/SPECTRUM_MODEL_STAGE1.md` and `docs/TERAD_INPUT_BASELINE.md`.

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

### Benchmark geometry

- source to reference point = 100 cm;
- reference point = 2 cm depth in water;
- water phantom = 20 x 20 x 20 cm3;
- circular field diameter = 10.5 cm at reference plane;
- chamber axis perpendicular to beam;
- water score voxel radius = 1 cm, thickness = 0.025 cm.

### Stage 3 chronology

**Stage 3A — XCSE diagnostic.** Increasing chamber XCSE reduced chamber uncertainty but left water uncertainty at ~4–5%.

**Stage 3B — VRT pilot.** IPSS/TmpPhsp + XCSE64 + RR64 reduced `u(D_w)` to ~0.63–0.69% at 5M histories and removed the water-score bottleneck.

**Stage 3C — first 200M benchmark.** Legacy HVL-refitted SpekPy `kqp` surrogate gave:

- `R100 = 0.99787 ± 0.00542`;
- `R250 = 1.09937 ± 0.00558`;
- `k100,250 = 0.907674 ± 0.006748`;
- deviation from published ≈ −4.8%.

**Stage 3D — root-cause screen.** Published filtration + explicit paper `Emin` substantially improved the benchmark; forcing a cross-code HVL refit pushed it back toward the original disagreement. This showed that equal HVL does not guarantee equal spectral shape.

**Stage 3E — 200M discrimination.** High-stat results:

| Case | k100,250 | u(k) rel | Δ vs 0.95355 | z vs published |
|---|---:|---:|---:|---:|
| `legacy_vac` | 0.913197 | 0.744% | −4.232% | −5.94 |
| `pubemin_vac` | **0.939163** | 0.748% | **−1.509%** | −2.05 |
| `pubemin_air48` | 0.930423 | 0.749% | −2.425% | −3.32 |

The large original mismatch is therefore primarily spectral-surrogate related, while a residual ~1.5% discrepancy remains.

## Stage 3F — current spectrum-engine and chamber-geometry sensitivity

Stage 3F directly compares the Stage 3E `kqp` spectrum against SpekPy legacy `spekcalc` and `spekpy-v1` modes using the paper filtration and `Emin`.

It also screens Model A sensitivities on the `spekcalc` spectrum:

- cavity radius 3.025 / 3.075 mm with internal volume held at 637.1 mm3;
- central-electrode radius 0.55 / 0.60 mm;
- graphite thickness 0.07 / 0.11 mm while total wall thickness is held fixed.

These are sensitivity surrogates, not claimed PTW manufacturing tolerances.

Stage 3F starts at 50M histories per point. Any meaningful candidate shift is repeated at high statistics before acceptance.

Workflow: `.github/workflows/stage3f-spectrum-geometry-sensitivity.yml`.

## Acceptance gates before production

Production Stage 4/5 is allowed only after **both** conditions are met:

1. the PTW 30013 / published-medium-kV benchmark is scientifically accepted with a justified uncertainty budget;
2. rebuilt TERAD Stage 1 spectra reproduce the authoritative Q120/Q140/Q150/Q200 HVLs without unphysical negative filtration and without silently changing the clinical filters.

Only then will the project:

1. calculate the Co-60 reference ratio `R_Co`;
2. calculate TERAD Q120/Q140/Q150/Q200 ratios in water;
3. derive `k_Q,Co = R_Q / R_Co`;
4. quantify TERAD-specific spectrum/chamber sensitivity;
5. determine separate applicator/SSD correction `k_g` for F40/F50 conditions;
6. determine RW3-to-water correction;
7. combine results into final coefficients and uncertainty budget.
