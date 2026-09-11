# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 3F — root-cause sensitivity of the residual published-benchmark discrepancy after the Stage 3E high-stat discrimination. Stage 4 (Co-60) remains blocked until the medium-kV benchmark is scientifically accepted.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

The individual chamber calibration is anchored to:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project deliberately keeps three physical problems separate:

1. intrinsic chamber beam-quality correction `k_Q`;
2. field/SSD geometry correction `k_g`;
3. RW3-to-water correction.

They are not folded into one empirical coefficient.

## Measured TERAD beam qualities

| Beam | HVL | Known added filter |
|---|---:|---|
| 120 kV | 0.224 mm Cu | 4.0 mm Al |
| 140 kV | 0.410 mm Cu | 0.2 mm Cu |
| 150 kV | 0.729 mm Cu | 0.5 mm Cu |
| 200 kV | 1.452 mm Cu | 1.0 mm Cu |

## Reference geometries

**Co-60 certificate denominator**
- water;
- SDD = 100 cm;
- reference depth = 5 g/cm² H2O;
- field = 10 x 10 cm² at the chamber reference plane.

**TERAD kV first-pass reference geometry**
- water;
- SSD = 50 cm;
- PTW 30013 reference point at 2 cm depth;
- field = 8 x 10 cm² at the phantom surface;
- chamber axis perpendicular to the beam axis.

RW3 conversion and field/SSD geometry corrections are intentionally separated from the first `k_Q` calculation.

## EGSnrc baseline

The project is pinned to the official NRC EGSnrc 2026 release commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

CI builds EGSnrc and `egs_chamber` reproducibly. Stage 3 patches the `egs_chamber` build to compile `rad_compton1.mortran`, so Radiative Compton corrections can be explicitly enabled and verified from each run log.

The accepted Stage 3 variance-reduction architecture uses:

- IPSS / `TmpPhsp = 1`;
- photon cross-section enhancement `XCSE = 64`;
- Russian Roulette survival probability `1/64`;
- `ESAVE = 0.512 MeV`;
- local XCSE zones for both `D_w` and chamber scoring;
- independent RNG seeds for independent high-stat benchmark qualities.

This architecture reduced the water-score uncertainty from about 4–5% in the early Stage 3A pilot to roughly 0.1–0.2% in high-stat runs; the chamber score then became the dominant statistical term.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI infrastructure | ✅ complete |
| 1 | SpekPy TERAD spectra fitted to measured Cu HVL | ✅ complete |
| 2 | PTW 30013 chamber geometry — Model A | 🟡 provisional; benchmark sensitivity in progress |
| 3 | Published medium-kV benchmark | 🟡 Stage 3F spectrum/geometry sensitivity running |
| 4 | Co-60 reference ratio | ⏸ blocked by Stage 3 |
| 5 | TERAD `k_Q,Co` | pending |
| 6 | TERAD spectrum / chamber-geometry production sensitivity | pending |
| 7 | Field and SSD geometry correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1 — accepted nominal TERAD spectra

The accepted first-pass TERAD spectrum model uses SpekPy 2.5.4, a W target, nominal 20 degree anode angle, `kqp` physics and 0.5 keV bins. Unknown tube-head/inherent filtration is represented by a fitted non-negative equivalent-Al nuisance parameter; it is not claimed to be the physical TERAD inherent filtration.

| Beam | measured Cu HVL1 (mm) | initial model (mm) | fitted eq. Al (mm) | final model (mm) | mean E (keV) |
|---|---:|---:|---:|---:|---:|
| Q120 | 0.224000 | 0.207172 | 0.447246 | 0.224000 | 56.8438 |
| Q140 | 0.410000 | 0.388502 | 0.525157 | 0.410000 | 65.4082 |
| Q150 | 0.729000 | 0.723665 | 0.264108 | 0.729000 | 75.3565 |
| Q200 | 1.452000 | 1.452955 | 0.000000 | 1.452955 | 96.2098 |

Q200 is already only +0.0658% harder than the measured HVL with the known 1.0 mm Cu filter, so no unphysical negative added filtration is used. All four qualities satisfy the Stage 1 HVL acceptance criterion of ±0.5%.

See `docs/SPECTRUM_MODEL_STAGE1.md` and `results/spekpy_fit_summary.csv`.

## Stage 2 — PTW 30013 Model A

Stage 2 intentionally avoids treating limited public PTW dimensions as a complete manufacturer blueprint. **Model A** is a transparent, public-volume-constrained first-pass geometry for benchmark validation.

Model A uses:

- air-cavity radius = 3.05 mm;
- internal cavity length = 21.80 mm;
- Al central-electrode radius = 0.575 mm;
- Al electrode length = 21.20 mm;
- graphite thickness = 0.09 mm;
- PMMA thickness = 0.335 mm.

The resulting aggregate volumes are approximately:

- internal cavity = 0.63710 cm³;
- central electrode = 0.02202 cm³;
- net air cavity = 0.61508 cm³.

Model A does **not** claim exact knowledge of detailed tip geometry, guard-ring/electric-field dead volume, electrode base, stem/cable construction or serial-specific manufacturing tolerances. Those are explicit sensitivity terms rather than hidden assumptions.

See `docs/PTW30013_GEOMETRY_STAGE2.md`.

## Stage 3 — published medium-kV PTW 30013 benchmark

Before calculating TERAD production coefficients, Model A is tested against published PTW 30013 medium-kV correction factors from Czarnecki et al. 2020.

Benchmark set:

| Beam | Cu HVL (mm) | published kQ ENEA | published kQ THM |
|---|---:|---:|---:|
| CCRI100 | 0.1461 | 0.9537 | 0.9534 |
| CCRI135 | 0.4708 | 0.9754 | 0.9738 |
| CCRI180 | 0.9863 | 0.9857 | 0.9856 |
| CCRI250 | 2.5150 | 1.0000 | 1.0000 |

The primary pilot benchmark uses CCRI250 for normalization:

`k_Q^MC = R_Q / R_250`, where `R_Q = D_w / D_cav`.

For CCRI100/250 the comparison reference is approximately `0.95355` (midpoint of the published ENEA/THM values).

### Benchmark geometry

- point source to reference point = 100 cm;
- chamber reference point = 2 cm water depth;
- water phantom = 20 x 20 x 20 cm³;
- circular field diameter = 10.5 cm at the reference plane;
- PTW 30013 axis perpendicular to the beam axis;
- chamber-free water dose scored in a cylindrical voxel with radius 1 cm and thickness 0.025 cm.

### Low-energy transport baseline

- `Global PCUT = 0.001 MeV`;
- `Global ECUT = 0.512 MeV`;
- photon cross sections = `mcdf-xcom`;
- Rayleigh scattering = On;
- photoelectron angular sampling = On;
- atomic relaxations = On;
- bound Compton scattering = On;
- Radiative Compton corrections = On;
- bremsstrahlung cross sections = NIST;
- bremsstrahlung angular sampling = KM;
- spin effects = On;
- electron impact ionization = `ik`;
- `ESTEPE = 0.25`;
- `XIMAX = 0.5`;
- exact boundary crossing algorithm.

## Stage 3 chronology and accepted conclusions

### Stage 3A — XCSE diagnostic

An 8-point matrix (CCRI100/250 × XCSE 64/128/256/512, 5M histories) established that increasing chamber XCSE alone reduced `D_cav` uncertainty but left `D_w` at roughly 4–5%, making the water score the statistical bottleneck.

Stage 3A is retained as a diagnostic, not as benchmark validation.

### Stage 3B — VRT pilot

The benchmark architecture was changed to match the published variance-reduction strategy more closely: IPSS/TmpPhsp, XCSE64, RR64, ESAVE 0.512 MeV and local enhancement around both scoring targets.

At 5M histories this reduced `u(D_w)` to about 0.63–0.69%, demonstrating that the VRT architecture works and removing the Stage 3A bottleneck.

### Stage 3C — first high-stat benchmark

With 200M histories per quality using the original HVL-refitted SpekPy `kqp` surrogate:

- `R100 = 0.99787 ± 0.00542`;
- `R250 = 1.09937 ± 0.00558`;
- `k100,250 = 0.907674 ± 0.006748`;
- relative MC uncertainty ≈ 0.743%;
- deviation from published ≈ **−4.8%**.

This discrepancy is too large to attribute to Monte Carlo statistics.

### Stage 3D — root-cause screen

A 50M sensitivity matrix separated spectrum construction from the additional 48 cm air transport. The most informative result was that using the paper's published filtration plus its explicit lower-energy cut `Emin` improved the central benchmark substantially, while forcing a SpekPy Al refit to the same Cu HVL drove the result back toward the original discrepancy.

This demonstrated that **matching HVL alone is not sufficient to reproduce the benchmark spectrum shape**.

### Stage 3E — high-stat discrimination

Three cases were repeated at 200M histories per quality:

| Case | k100,250 | u(k) abs | u(k) rel | Δ vs 0.95355 | z vs published |
|---|---:|---:|---:|---:|---:|
| `legacy_vac` | 0.913197 | 0.006794 | 0.744% | −4.232% | −5.94 |
| `pubemin_vac` | **0.939163** | 0.007024 | 0.748% | **−1.509%** | −2.05 |
| `pubemin_air48` | 0.930423 | 0.006964 | 0.749% | −2.425% | −3.32 |

The `legacy_vac` repeat is statistically consistent with Stage 3C (`z ≈ 0.58`), confirming that the original large discrepancy was reproducible.

The best current benchmark is therefore the **published filtration + published Emin** spectrum without forcing a cross-code HVL refit. It reduces the discrepancy from about −4.2 to −1.5%.

The direct `air48 - vacuum` difference for the published-Emin family was not statistically significant (`z ≈ −0.88`), so the extra-air treatment is not currently accepted as the explanation for the residual discrepancy.

### Current interpretation after Stage 3E

The initial 4–5% disagreement was primarily a spectrum-surrogate problem, not evidence that the PTW chamber geometry was wrong by 4–5%.

A residual ≈1.5% discrepancy remains. It can plausibly come from:

- residual spectral-shape differences between SpekPy `kqp` and the original SpekCalc spectrum;
- simplifications in PTW 30013 Model A;
- a combination of both.

Stage 4 is therefore intentionally blocked.

## Stage 3F — spectrum-engine and chamber-geometry sensitivity (current)

Stage 3F first tests the most direct remaining spectrum hypothesis: **the original paper used SpekCalc**, whereas Stage 3E used SpekPy-v2 `kqp`. SpekPy 2.5.4 can generate spectra with its legacy `spekcalc` physics mode, allowing a much closer cross-model test without changing the paper filtration or Emin.

Spectrum-engine screen, all using the paper filtration and Emin:

- `kqp` — Stage 3E spectral baseline;
- `spekcalc` — highest-priority legacy SpekCalc-compatible model;
- `spekpy-v1` — additional spectral-shape sensitivity.

The same Stage 3F screen also tests transparent Model A geometry surrogates using the `spekcalc` spectrum:

- cavity radius 3.025 mm with internal cavity volume held at 637.1 mm³;
- cavity radius 3.075 mm with internal cavity volume held at 637.1 mm³;
- central-electrode radius 0.55 mm;
- central-electrode radius 0.60 mm;
- graphite thickness surrogate 0.07 mm while total wall thickness is held fixed;
- graphite thickness surrogate 0.11 mm while total wall thickness is held fixed.

These geometry perturbations are **sensitivity surrogates, not claimed PTW manufacturing tolerances**. They are used only to determine whether realistic small changes in the simplified Model A can plausibly move `k100,250` by the remaining ~1.5%.

Stage 3F starts as a 50M-history screen per point. Any spectrum or geometry case that produces a potentially meaningful shift will be repeated at high statistics before it is accepted or rejected.

Workflow: `.github/workflows/stage3f-spectrum-geometry-sensitivity.yml`  
Spectrum generator: `scripts/generate_czarnecki_stage3f_spectra.py`

## Stage 3 acceptance rule

No production TERAD `k_Q,Co` will be generated until the benchmark discrepancy is understood and the accepted chamber/spectrum model reproduces published medium-kV behavior within a justified uncertainty budget.

Only after the CCRI100/250 root cause is resolved will CCRI135 and CCRI180 be added as independent validation points.

## Planned downstream workflow

After successful Stage 3 validation:

1. calculate the Co-60 reference ratio `R_Co = (D_w / D_cav)_Co`;
2. calculate TERAD Q120/Q140/Q150/Q200 ratios in water;
3. derive `k_Q,Co = R_Q / R_Co`;
4. quantify TERAD-specific spectrum and chamber-geometry sensitivity;
5. determine the separate field/SSD geometry correction `k_g`;
6. determine the separate RW3-to-water correction;
7. combine accepted results into final coefficients with a traceable uncertainty budget.

No intermediate Stage 3 result is treated as a production TERAD `k_Q,Co`.