# TERAD-PTW30013-MC

Monte Carlo project for deriving chamber-specific beam-quality correction factors for a PTW 30013 Farmer chamber used with a TERAD kilovoltage therapy unit.

> **Current milestone:** Stage 3A — validation of PTW 30013 Model A against published medium-kV beam-quality benchmarks. The low-energy correlated-ratio XCSE pilot is currently running for CCRI100 and CCRI250.

## Primary target

For Q = 120, 140, 150 and 200 kV:

`k_Q,Co = (D_w / D_cav)_Q / (D_w / D_cav)_Co`

The individual chamber calibration is anchored to:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

The project deliberately keeps the chamber beam-quality correction, field/SSD geometry correction and RW3-to-water correction as separate physical problems rather than folding them into one empirical coefficient.

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

CI has successfully built EGSnrc and `egs_chamber` and completed an official Co-60 Monte Carlo smoke example. Stage 3 additionally patches the `egs_chamber` build to compile `rad_compton1.mortran`, allowing Radiative Compton corrections to be explicitly enabled and verified in the run log.

## Project status

| Stage | Description | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber CI infrastructure | ✅ complete |
| 1 | SpekPy TERAD spectra fitted to measured Cu HVL | ✅ complete |
| 2 | PTW 30013 chamber geometry — Model A | ✅ complete for benchmark validation |
| 3 | Published medium-kV benchmark | 🟡 Stage 3A XCSE pilot running |
| 4 | Co-60 reference ratio | pending |
| 5 | TERAD `k_Q,Co` | pending |
| 6 | Spectrum / geometry sensitivity | pending |
| 7 | Field and SSD geometry correction `k_g` | pending |
| 8 | RW3-to-water correction | pending |
| 9 | Final coefficients and uncertainty budget | pending |

## Stage 1 — accepted nominal TERAD spectra

The accepted first-pass spectrum model uses SpekPy 2.5.4, a W target, nominal 20 degree anode angle, `kqp` physics and 0.5 keV bins. The unknown tube-head/inherent filtration is represented by a fitted non-negative equivalent-Al nuisance parameter; it is not a claimed physical TERAD filtration thickness.

| Beam | measured Cu HVL1 (mm) | initial model (mm) | fitted eq. Al (mm) | final model (mm) | mean E (keV) |
|---|---:|---:|---:|---:|---:|
| Q120 | 0.224000 | 0.207172 | 0.447246 | 0.224000 | 56.8438 |
| Q140 | 0.410000 | 0.388502 | 0.525157 | 0.410000 | 65.4082 |
| Q150 | 0.729000 | 0.723665 | 0.264108 | 0.729000 | 75.3565 |
| Q200 | 1.452000 | 1.452955 | 0.000000 | 1.452955 | 96.2098 |

Q200 is already only +0.0658% harder than the measured HVL with the known 1.0 mm Cu filter, so no unphysical negative added filtration is used. All four qualities satisfy the Stage 1 HVL acceptance criterion of ±0.5%.

See `docs/SPECTRUM_MODEL_STAGE1.md` and `results/spekpy_fit_summary.csv`.

## Stage 2 — PTW 30013 Model A

Stage 2 intentionally avoids treating the limited public PTW dimensional data as a complete manufacturer blueprint. Instead, **Model A** is a transparent public-volume-constrained first-pass geometry for benchmark validation.

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

The model reproduces published aggregate-volume constraints while preserving the public PTW radial dimensions and material specifications. It does **not** claim exact knowledge of detailed tip geometry, guard-ring/dead-volume geometry, electrode base, stem/cable construction or chamber-specific manufacturing tolerances. Those remain explicit later sensitivity terms.

Stage 2 Model A is therefore accepted for **published benchmark work**, not yet as an exact production chamber model.

See `docs/PTW30013_GEOMETRY_STAGE2.md` and the Stage 2 `egs_chamber` inputs in `inputs/`.

## Stage 3 — published medium-kV PTW 30013 benchmark

Before calculating TERAD production coefficients, Model A is being tested against published PTW 30013 medium-kV beam-quality correction data.

Current benchmark set:

| Beam | Cu HVL (mm) | published kQ ENEA | published kQ THM |
|---|---:|---:|---:|
| CCRI100 | 0.1461 | 0.9537 | 0.9534 |
| CCRI135 | 0.4708 | 0.9754 | 0.9738 |
| CCRI180 | 0.9863 | 0.9857 | 0.9856 |
| CCRI250 | 2.5150 | 1.0000 | 1.0000 |

The benchmark uses CCRI250 as the normalization quality:

`k_Q^MC = R_Q / R_250`, where `R_Q = D_w / D_cav`.

### Benchmark geometry

- point source to reference point = 100 cm;
- chamber reference point = 2 cm water depth;
- water phantom = 20 x 20 x 20 cm³;
- circular field diameter = 10.5 cm at the reference plane;
- PTW 30013 axis perpendicular to the beam axis;
- chamber-free water dose scored in a cylindrical voxel with radius 1 cm and thickness 0.025 cm;
- `dose_to_water` and `chamber_in_water` are scored as correlated geometries.

### Low-energy transport baseline

Stage 3 uses pegsless low-energy media so that the benchmark transport thresholds can be reproduced directly:

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

### Stage 3A — XCSE stability pilot

Photon cross-section enhancement (XCSE) is used only as a variance-reduction technique. The physical Model A dimensions are unchanged. A 1 cm `WATER_1KEV` shell surrounds the chamber solely to provide a stable XCSE enhancement zone.

`chamber_xcse_zone` resolves to 15 regions. `egs_chamber` requires one enhancement value for each resolved region, so the workflow explicitly expands the requested scalar XCSE factor to all 15 entries and verifies the parsed values in the log.

The current pilot runs:

- CCRI100 and CCRI250;
- XCSE = 64, 128, 256 and 512;
- `NCASE = 5e6` per run.

The Stage 3A objective is to identify an XCSE range in which `R_Q = D_w / D_cav` is statistically efficient and independent of the enhancement factor. Only after XCSE stability is demonstrated will the benchmark be expanded to CCRI135 and CCRI180 and compared quantitatively with the published `k_Q` values.

Input: `inputs/stage3_czarnecki_modelA.template.egsinp`  
Workflow: `.github/workflows/stage3-benchmark-pilot.yml`  
Benchmark data: `data/czarnecki2020_benchmark.csv`

## Planned downstream workflow

After successful Stage 3 validation:

1. calculate the Co-60 reference ratio `R_Co = (D_w / D_cav)_Co`;
2. calculate TERAD Q120/Q140/Q150/Q200 ratios in water;
3. derive `k_Q,Co = R_Q / R_Co`;
4. quantify spectrum and chamber-geometry model sensitivity;
5. determine the separate field/SSD geometry correction `k_g`;
6. determine the separate RW3-to-water correction;
7. combine accepted results into final coefficients with a traceable uncertainty budget.

No intermediate Stage 3 result is treated as a production TERAD `k_Q,Co` until the published benchmark has been passed.