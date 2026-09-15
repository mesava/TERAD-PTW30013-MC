# TERAD-PTW30013-MC

Monte Carlo проект для определения chamber-specific коэффициентов коррекции для **PTW 30013** на киловольтном рентгенотерапевтическом аппарате **TERAD**.

> **Текущий статус:** PTW 30013 **Model B1 benchmark-validated** по CCRI100/135/180/250. **Stage 4 Co-60 — PASS**: `R_Co = 1.12016676 ± 0.00104473`. **Stage 5 TERAD matched-water — PASS: 12/12 конфигураций**. **Stage 8 — реальная RW3-геометрия и прямой RW3→water transfer — ACTIVE**.

## Базовая задача

Камера PTW 30013 SN 013488 имеет calibration coefficient в Co-60:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

Задача проекта — определить, как по показанию этой камеры в реальной TERAD/RW3-геометрии получить absorbed dose to water для каждого качества пучка и каждого клинического аппликатора.

Основные определения:

`R_Q,g = (D_w / D_cav)_(Q,g)`

`R_Co = (D_w / D_cav)_Co`

`k_Q,g,Co = R_Q,g / R_Co`

Для внутреннего сравнения геометрий при одном качестве Q:

`k_g,Q(g) = R_Q,g / R_Q,F50`

Для RW3-блока дополнительно определяется direct RW3→water response:

`R_Q,g^(RW3→w) = D_w^(matched water) / D_cav^(RW3)`

и соответствующий клинический коэффициент:

`k_Q,g,Co^(RW3→w) = R_Q,g^(RW3→w) / R_Co`.

## Канонические TERAD inputs

| Beam | kV | mA | Measured HVL1 | Added filter |
|---|---:|---:|---:|---|
| Q120 | 120 | 10 | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 | 10 | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 | 10 | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 | 7 | **1.452 mm Cu** | 1.0 mm Cu |

Для каждого качества рассчитываются три реальные клинические конфигурации:

| Applicator | SSD | Field |
|---|---:|---:|
| F40 | 40 cm | 6 × 8 cm² |
| F40 | 40 cm | 4 × 15 cm² |
| F50 | 50 cm | 8 × 10 cm² |

Итого **12 Q/applicator combinations**.

Авторитетные файлы:

- `docs/CANONICAL_MC_TASK.md`
- `data/beam_qualities.csv`
- `data/terad_clinical_geometries.csv`

## Production spectra ✅

Принятый first-pass TERAD spectrum model:

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

Один HVL не определяет spectrum однозначно; spectrum ambiguity остаётся отдельным uncertainty contribution.

## PTW 30013 Model B1 ✅ benchmark-validated

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

Точная proprietary geometry guard/insulator/electrode-base/stem-transition не выдумывается и учитывается как model limitation.

### Benchmark validation

| Quality | MC weighted | u(k) | Target | Δ | z_vs_pub | z_rep |
|---|---:|---:|---:|---:|---:|---:|
| CCRI100/250 | **0.95093210** | 0.00401972 | 0.95355 | -0.2745% | -0.651 | -0.137 |
| CCRI135/250 | **0.97168791** | 0.00415738 | 0.97460 | -0.2988% | -0.700 | -0.959 |
| CCRI180/250 | **0.98774017** | 0.00419134 | 0.98565 | +0.2121% | +0.499 | +0.478 |

**Итог:** Model B1 прошла endpoint и intermediate validation без подгонки геометрии после получения результатов.

## Stage 4 — Co-60 anchor ✅ PASS

Reference geometry:

- SDD = 100 cm;
- SSD = 95 cm;
- depth = 5 cm water;
- field = 10×10 cm² at reference point;
- water phantom = 30×30×30 cm³;
- two independent 300M-history replications.

Run `34849606671`:

- repA: `R_Co = 1.121780 ± 0.001430`;
- repB: `R_Co = 1.118320 ± 0.001530`;
- weighted: **`R_Co = 1.12016676 ± 0.00104473`**;
- weighted MC uncertainty = **0.0933%**;
- `z_rep = +1.652`;
- gate = **PASS**.

Persisted result: `results/stage4_co60_summary.csv`.

## Stage 5 — TERAD matched-water ✅ PASS

Workflow run: **`34931189724`**.

Design:

- 12/12 canonical Q/applicator configurations;
- 300M histories / 30 batches per point;
- fixed benchmark-validated Model B1;
- accepted TERAD spectra;
- chamber centre at 2.0 cm depth in water;
- 30×30 cm² water phantom;
- explicit air path;
- clinical SSD 40/50 cm;
- field aperture specified at phantom surface and projected to chamber reference plane.

Predeclared point gate:

`u(R_Q,g) / R_Q,g <= 1.0%`.

**Все 12/12 точек прошли gate.**

| Config | R_Q,g | u(R), % | k_Q,g,Co | k_g vs F50 |
|---|---:|---:|---:|---:|
| Q120 F40 6×8 | 1.04389 | 0.3583 | 0.93190589 | 0.99678208 |
| Q120 F40 4×15 | 1.05025 | 0.4085 | 0.93758361 | 1.00285507 |
| Q120 F50 8×10 | 1.04726 | 0.4478 | 0.93491437 | 1.00000000 |
| Q140 F40 6×8 | 1.05251 | 0.3620 | 0.93960117 | 0.99347756 |
| Q140 F40 4×15 | 1.06164 | 0.4126 | 0.94775174 | 1.00209549 |
| Q140 F50 8×10 | 1.05942 | 0.4474 | 0.94576990 | 1.00000000 |
| Q150 F40 6×8 | 1.06825 | 0.3632 | 0.95365265 | 0.99715299 |
| Q150 F40 4×15 | 1.08036 | 0.4147 | 0.96446354 | 1.00845701 |
| Q150 F50 8×10 | 1.07130 | 0.4490 | 0.95637546 | 1.00000000 |
| Q200 F40 6×8 | 1.09033 | 0.3522 | 0.97336400 | 1.00472724 |
| Q200 F40 4×15 | 1.09022 | 0.3990 | 0.97326580 | 1.00462588 |
| Q200 F50 8×10 | 1.08520 | 0.4349 | 0.96878433 | 1.00000000 |

Intrinsic F50 beam-quality coefficients:

- `k_120,Co = 0.93491437 ± 0.00427671`
- `k_140,Co = 0.94576990 ± 0.00432247`
- `k_150,Co = 0.95637546 ± 0.00438567`
- `k_200,Co = 0.96878433 ± 0.00430944`

Persisted files:

- `results/stage5_terad_water_summary.csv`
- `results/stage5_intrinsic_kq.csv`
- `results/stage5_gate.txt`
- `results/stage5_absolute_scores.csv`
- `docs/STAGE5_TERAD_WATER.md`

`results/stage5_absolute_scores.csv` additionally preserves `D_w/history` and `D_cav,water/history` for direct matched-medium transfer calculations, so water MC does not have to be repeated in the RW3 block.

### Stage 5 modelling limits

The supplied clinical data define SSD and aperture but not proprietary applicator-wall material/thickness/internal geometry. Stage 5 therefore models field/SSD/aperture geometry, not unknown applicator-body scatter.

For rectangular fields the current explicit convention is: first listed field dimension along chamber axis/stem and second dimension perpendicular. Orientation remains a geometry-sensitivity item.

## Stage 8 — RW3 matched / direct end-to-end 🟡 ACTIVE

Real measurement geometry:

- RW3 phantom type 29672, transverse size = 30×30 cm²;
- PTW 30013 is inserted into chamber plate **29672/U19**;
- U19 thickness = 20 mm, with PTW-specified chamber-axis offsets **H1 = 7 mm** and **H2 = 13 mm**;
- in the actual clinical assembly, the chamber axis lies **7 mm below the upper face of U19**;
- an additional **13 mm of RW3 slabs is placed above U19**;
- therefore the geometric chamber centre / reference point is at a **physical depth of 20 mm = 2.0 cm from the RW3 surface**;
- PTW 30013 horizontal, chamber axis perpendicular to beam, reference point on CAX, stem right;
- approximately 10 cm RW3 downstream;
- applicator contacts RW3 surface;
- SSD = 40 or 50 cm from source to RW3 surface.

This 2.0 cm depth is a **physical geometric depth**, not a water-equivalent reinterpretation. It is deliberately matched to the 2.0 cm water depth used in Stage 5, so the direct RW3→water comparison changes the phantom material while preserving the reference-point depth and clinical SSD.

RW3 manufacturer anchors used in MC:

- polystyrene `(C8H8)` containing **2.0 ± 0.4% TiO2 by mass**;
- density = **1.045 g/cm³**;
- electron density = **1.012 × water**;
- mean `Z/A = 0.536`;
- slab thickness tolerance = **±0.1 mm**.

The direct calculation determines for each of the 12 configurations:

- `D_cav,RW3 / history`;
- `D_RW3 / history` at the chamber reference point;
- matched `D_w / D_RW3`;
- `k_RW3→w = D_cav,water / D_cav,RW3`;
- `R_Q,g^(RW3→w) = D_w,water / D_cav,RW3`;
- `k_Q,g,Co^(RW3→w) = R_Q,g^(RW3→w) / R_Co`.

This provides the direct coefficient needed to convert a chamber reading obtained in the real RW3 setup to absorbed dose to water.

## EGSnrc

Official NRC EGSnrc pinned commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Validated transport architecture uses low-energy photon transport, Radiative Compton, exact BCA, XCSE, TmpPhsp/IPSS and Russian Roulette.

## Project status

| Stage | Content | Status |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ |
| 1 | TERAD production spectra | ✅ |
| 2–3 | PTW 30013 chamber benchmark | ✅ Model B1 validated |
| 3H-4 | CCRI100/250 high-stat | ✅ PASS |
| 3H-5 | CCRI135/180 independent validation | ✅ PASS |
| 4 | Co-60 `R_Co` | ✅ PASS |
| 5 | 12 TERAD matched-water `R_Q,g` | ✅ 12/12 PASS |
| 6 | spectrum/chamber sensitivity | ⏸ nominal production first |
| 7 | applicator/orientation sensitivity | ⏸ nominal production first |
| 8 | RW3-to-water + 12 direct end-to-end | 🟡 ACTIVE |
| 9 | final coefficients + uncertainty budget | ⏸ |

## Project rules

- measured TERAD HVLs are not changed to improve agreement;
- chamber geometry is not tuned after benchmark validation;
- one HVL does not uniquely determine a spectrum;
- F50 is a real clinical configuration, not reference-only;
- technical CI failure is not interpreted as a physical MC failure;
- missing proprietary dimensions are documented as limitations, not invented;
- RW3 manufacturer composition/density and actual measured/setup geometry are tracked separately and propagated into the uncertainty model.