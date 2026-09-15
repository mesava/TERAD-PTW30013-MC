# TERAD-PTW30013-MC

Monte Carlo проект для определения chamber-specific коэффициентов коррекции для **PTW 30013** на киловольтном рентгенотерапевтическом аппарате **TERAD**.

> **Текущий статус:** PTW 30013 **Model B1 benchmark-validated** по CCRI100/135/180/250. **Stage 4 Co-60 завершён PASS**: `R_Co = 1.12016676 ± 0.00104473`. Запущен **Stage 5 — 12 TERAD matched-water production calculations**, run `34931189724`.

## Основные определения

`R_Q,g = (D_w / D_cav)_(Q,g)`

`k_Q,g,Co = R_Q,g / R_Co`

Для внутреннего geometry-normalization по каждому качеству Q:

`k_g,Q(g) = R_Q,g / R_Q,F50`

F50 рассчитывается как полноценная клиническая конфигурация и только после этого используется как denominator для `k_g`.

Индивидуальный calibration metadata для PTW 30013 SN 013488:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

## Канонические входные данные TERAD

Авторитетные файлы:

- `docs/CANONICAL_MC_TASK.md`
- `data/beam_qualities.csv`
- `data/terad_clinical_geometries.csv`

| Beam | kV | mA | Measured HVL1 | Added clinical filter |
|---|---:|---:|---:|---|
| Q120 | 120 | 10 | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 | 10 | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 | 10 | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 | 7 | **1.452 mm Cu** | 1.0 mm Cu |

Ошибочная диагностическая ветка HVL `0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu` не относится к production calculations.

## 12 клинических конфигураций

Для каждого Q120/Q140/Q150/Q200 рассчитываются:

| Applicator | SSD | Field |
|---|---:|---:|
| F40 | 40 cm | 6 × 8 cm² |
| F40 | 40 cm | 4 × 15 cm² |
| F50 | 50 cm | 8 × 10 cm² |

Итого **12 kV/applicator combinations**.

## Production spectra

Первый принятый TERAD spectrum model:

- SpekPy 2.5.4;
- W reflection target;
- nominal anode angle 20°;
- `kqp` physics;
- 0.5 keV bins;
- known clinical filtration + non-negative equivalent-Al nuisance filtration;
- fit к measured Cu HVL.

| Beam | Target HVL1 | Final HVL1 | Error |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Result: `results/spekpy_fit_summary.csv`.

## PTW 30013 Model B1

Model B1 — public/aggregate surrogate, а не manufacturer blueprint.

Принятые параметры:

- sensitive radius = 3.05 mm;
- sensitive length = 23.0 mm;
- graphite wall = 0.09 mm;
- PMMA wall = 0.335 mm;
- Al central electrode diameter = 1.15 mm;
- nominal public-derived PMMA tip surrogate = 1.5 mm;
- reference point = 13.0 mm от physical tip;
- cavity mass = `7.832972283369083e-04 g`.

Точная proprietary geometry guard/insulator/electrode-base/stem-transition неизвестна и не выдумывается.

## Benchmark validation ✅

Published midpoint targets:

- `k100,250 = 0.95355`
- `k135,250 = 0.97460`
- `k180,250 = 0.98565`
- `k250,250 = 1`

| Quality | MC weighted | u(k) | Target | Δ | z_vs_pub | z_rep |
|---|---:|---:|---:|---:|---:|---:|
| CCRI100/250 | **0.95093210** | 0.00401972 | 0.95355 | -0.2745% | -0.651 | -0.137 |
| CCRI135/250 | **0.97168791** | 0.00415738 | 0.97460 | -0.2988% | -0.700 | -0.959 |
| CCRI180/250 | **0.98774017** | 0.00419134 | 0.98565 | +0.2121% | +0.499 | +0.478 |

Model B1 прошла заранее заданные endpoint/intermediate gates без дальнейшей подгонки.

## Stage 4 — Co-60 anchor ✅ PASS

Reference geometry:

- SDD 100 cm;
- SSD 95 cm;
- depth 5 cm water;
- 10×10 cm² at reference plane;
- 30×30×30 cm³ water;
- two independent 300M-history replications.

Run `34849606671`:

- repA: `R_Co = 1.121780 ± 0.001430`;
- repB: `R_Co = 1.118320 ± 0.001530`;
- weighted: **`R_Co = 1.12016676 ± 0.00104473`**;
- weighted MC uncertainty = **0.0933%**;
- `z_rep = +1.652`;
- gate = **PASS**.

Persisted result: `results/stage4_co60_summary.csv`.

## Stage 5 — TERAD matched-water production 🟡 ACTIVE

Workflow: `.github/workflows/stage5-terad-water.yml`

Run: **`34931189724`**

Design:

- all **12** canonical Q/applicator configurations;
- 300M histories / 30 batches per configuration;
- fixed benchmark-validated Model B1;
- accepted SpekPy TERAD spectra regenerated deterministically at runtime;
- chamber centre depth = 2.0 cm water;
- 30×30 cm² water phantom;
- 10 cm water downstream of chamber centre;
- explicit air path from source to phantom surface;
- SSD = 40 or 50 cm as defined by applicator;
- field aperture specified at phantom surface and projected to chamber reference plane.

Predeclared point gate:

`u(R_Q,g) / R_Q,g <= 1.0%`.

Outputs after completion:

- all 12 `R_Q,g`;
- all 12 `k_Q,g,Co`;
- F50-based `k_g,Q` for both F40 geometries;
- intrinsic F50 `k_Q,Co` for Q120/Q140/Q150/Q200.

Full method: `docs/STAGE5_TERAD_WATER.md`.

### Current modelling limitation

The supplied clinical data define applicator aperture and SSD but do not include applicator-wall material/thickness/internal geometry. Stage 5 therefore models the real supplied **field/SSD/aperture geometry**, but does not claim proprietary applicator-body scatter.

For rectangular fields, until physical orientation is independently confirmed, Stage 5 uses the explicit convention: first field dimension along chamber axis/stem, second dimension perpendicular. This remains a geometry sensitivity item, not a manufacturer fact.

## RW3 geometry for later stages

- RW3 transverse size 30×30 cm²;
- PTW 30013 horizontal;
- chamber axis perpendicular to beam;
- reference point on central axis;
- stem right;
- centre at 2.0 cm water-equivalent depth;
- 1.3 cm RW3 physically above chamber body in the supplied setup;
- approximately 10 cm downstream RW3;
- lateral margin at least 10 cm;
- applicator contacts phantom surface.

All 12 configurations require matched RW3 and direct end-to-end calculations after Stage 5.

## EGSnrc

Official NRC EGSnrc pinned commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Validated transport architecture uses low-energy photon transport, Radiative Compton, exact BCA, XCSE, TmpPhsp/IPSS and Russian Roulette.

## Project status

| Stage | Content | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ |
| 1 | TERAD production spectra | ✅ accepted first-pass model |
| 2–3 | PTW 30013 chamber benchmark | ✅ Model B1 validated |
| 3H-4 | CCRI100/250 high-stat | ✅ PASS |
| 3H-5 | CCRI135/180 independent validation | ✅ PASS |
| 4 | Co-60 `R_Co` | ✅ PASS |
| 5 | 12 TERAD matched-water `R_Q,g` | 🟡 ACTIVE |
| 6 | spectrum/chamber sensitivity | ⏸ |
| 7 | geometry refinements / applicator sensitivity | ⏸ |
| 8 | RW3-to-water + 12 direct end-to-end | ⏸ |
| 9 | final coefficients + uncertainty budget | ⏸ |

## Production path

1. Complete Stage 5 water calculations for all 12 configurations.
2. Review spectrum/chamber/field-orientation sensitivity without fitting to desired values.
3. Perform matched RW3 calculations.
4. Derive RW3-to-water response.
5. Perform direct 12-configuration RW3 end-to-end checks.
6. Produce final coefficients and uncertainty budget.

## Project rules

- measured TERAD HVLs are not changed to improve agreement;
- chamber geometry is not tuned after benchmark validation;
- one HVL does not uniquely determine a spectrum, so spectral ambiguity is evaluated separately;
- F50 is never treated as reference-only;
- technical CI failure is not a physical MC failure;
- missing proprietary applicator/chamber dimensions are documented as limitations, not invented.
