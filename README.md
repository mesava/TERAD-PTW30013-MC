# TERAD-PTW30013-MC

Monte Carlo проект для определения chamber-specific коэффициентов коррекции для ионизационной камеры **PTW 30013** на киловольтном рентгенотерапевтическом аппарате **TERAD**.

> **Текущий статус:** модель камеры **PTW 30013 Model B1 прошла опубликованный benchmark Czarnecki et al. для CCRI100/135/180/250**. Проект перешёл к **Stage 4 — Co-60 reference ratio**. Первый Stage 4 run `34840485287` остановился на техническом self-check builder (`Unresolved template token remains`) **до запуска MC**, поэтому физического результата Co-60 из этого run нет.

## Цель проекта

Для качества пучка `Q` рассчитывается

`R_Q = (D_w / D_cav)_Q`

и затем

`k_Q,Co = R_Q / R_Co`.

Для камеры PTW 30013 SN 013488 используется индивидуальный calibration coefficient:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

Итоговая задача — получить для всех клинических конфигураций TERAD:

- water-response `R_Q`;
- chamber-specific `k_Q,Co`;
- влияние геометрии `field / SSD / applicator` через `k_g`;
- `RW3-to-water` correction;
- direct `end-to-end` MC в реальной геометрии RW3;
- итоговый uncertainty budget.

## Канонические входные данные TERAD

Авторитетные файлы:

- `docs/CANONICAL_MC_TASK.md`
- `docs/TERAD_INPUT_BASELINE.md`
- `data/terad_input_baseline.csv`
- `data/beam_qualities.csv`
- `data/terad_clinical_geometries.csv`

| Beam | Напряжение | Ток | Измеренный HVL1 | Добавочный фильтр |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu |

Временная ветка со значениями HVL `0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu` является ошибочной и не относится к production calculations.

## Клинические геометрии TERAD

Для **каждого** Q120/Q140/Q150/Q200 рассчитываются все три реальные конфигурации:

| Аппликатор | SSD | Поле |
|---|---:|---:|
| F40 | 40 cm | 6 × 8 cm² |
| F40 | 40 cm | 4 × 15 cm² |
| F50 | 50 cm | 8 × 10 cm² |

Итого: **12 клинических комбинаций**.

F50 — полноценная клиническая конфигурация. Она рассчитывается так же, как оба F40, и только после собственного абсолютного расчёта может использоваться как normalization denominator для представления `k_g`.

## Production spectra TERAD

Текущий принятый первый вариант спектральной модели:

- SpekPy 2.5.4;
- W reflection target;
- nominal anode angle 20°;
- `kqp` physics;
- известный клинический фильтр;
- неотрицательная equivalent-Al nuisance filtration;
- 0.5 keV bins.

| Beam | Target HVL1 | Полученный HVL1 | Ошибка |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Результат: `results/spekpy_fit_summary.csv`.

## Принятая модель PTW 30013

### Model B1 — benchmark-validated

Model B1 основана только на public/aggregate данных и не претендует на точное воспроизведение proprietary конструкции камеры.

Ключевые параметры:

- sensitive radius = **3.05 mm**;
- sensitive length = **23.0 mm**;
- graphite wall = **0.09 mm**;
- PMMA wall = **0.335 mm**;
- Al central electrode diameter = **1.15 mm**;
- nominal PMMA tip surrogate = **1.5 mm**;
- reference point = **13.0 mm от физического tip**;
- cavity mass = `7.832972283369083e-04 g`.

Nominal tip 1.5 mm получен до MC из публичной геометрической связи:

`13.0 - 23.0/2 = 1.5 mm`.

Он не подбирался по benchmark.

Точная геометрия guard, insulator, electrode base и stem transition неизвестна; эти элементы не объявляются manufacturer dimensions.

## Benchmark PTW 30013

Benchmark: Czarnecki et al. 2020, CCRI100/135/180/250.

Опубликованные midpoint targets:

- `k100,250 = 0.95355`;
- `k135,250 = 0.97460`;
- `k180,250 = 0.98565`;
- `k250,250 = 1`.

Фиксированная Model B1 прошла endpoint и промежуточную high-stat validation без дальнейшей подгонки геометрии.

| Quality | MC weighted | u(k) | Target | Δ | z_vs_pub | z_rep |
|---|---:|---:|---:|---:|---:|---:|
| CCRI100/250 | **0.95093210** | 0.00401972 | 0.95355 | -0.2745% | -0.651 | -0.137 |
| CCRI135/250 | **0.97168791** | 0.00415738 | 0.97460 | -0.2988% | -0.700 | -0.959 |
| CCRI180/250 | **0.98774017** | 0.00419134 | 0.98565 | +0.2121% | +0.499 | +0.478 |

Validation gate:

- `|z_rep| <= 2` — выполнено;
- `|z_vs_pub| <= 2` — выполнено;
- `k135,250 < k180,250 < 1` — выполнено.

**Итог: Model B1 принята как benchmark-validated модель для последующих Co-60 и TERAD calculations.**

Основные результаты:

- `results/stage3h4_summary.csv`
- `results/stage3h5_summary.csv`
- `docs/STAGE3H5_INTERMEDIATE_VALIDATION.md`
- `docs/PTW30013_MODEL_B_PUBLIC_PLAN.md`

## Stage 4 — Co-60 reference ratio

Цель:

`R_Co = (D_w / D_cav)_Co`.

Референсная геометрия:

- SDD = **100 cm**;
- SSD = **95 cm**;
- reference depth = **5 cm water**;
- поле = **10 × 10 cm²** в плоскости reference point;
- water phantom = **30 × 30 × 30 cm³**;
- Model B1 без изменений;
- две независимые реплики по **300M histories**.

Файлы:

- `data/co60_reference_geometry.csv`
- `docs/STAGE4_CO60_ANCHOR.md`
- `scripts/build_stage4_co60_b1.py`
- `.github/workflows/stage4-co60-anchor.yml`

Текущий статус Stage 4:

- run `34840485287` — **technical failure до MC**;
- EGSnrc configure/build прошли успешно;
- остановка произошла на `Build and self-check Co-60 Model B1 input`;
- причина: `Unresolved template token remains`;
- `R_Co` из этого run не получен;
- следующий шаг — исправить builder и повторить Stage 4 без изменения физической модели.

Предварительно установленный replication gate:

- `|z_rep| <= 2`;
- относительная MC uncertainty каждой реплики `<= 1%`.

## Реальная геометрия RW3

- RW3: **30 × 30 cm²**;
- PTW 30013 расположена горизонтально;
- ось камеры перпендикулярна central axis;
- geometric centre / reference point находится на central axis;
- stem направлен вправо;
- reference point соответствует **2.0 cm water-equivalent depth**;
- физически над корпусом камеры в заданной установке находится **1.3 cm RW3**;
- downstream запас RW3 — приблизительно **10 cm**;
- боковой запас — не менее **10 cm**;
- SSD определяется аппликатором F40/F50;
- аппликатор прижат к поверхности RW3.

Для всех 12 конфигураций требуется прямой `end-to-end` RW3 MC в дополнение к раздельным water / geometry / RW3 calculations.

## EGSnrc

Используется официальный NRC EGSnrc, закреплённый на commit:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`.

Основные принятые настройки включают low-energy photon transport, Radiative Compton, exact BCA, XCSE и Russian Roulette. Benchmark calculations дополнительно использовали IPSS/TmpPhsp и paper-faithful air transport.

## Текущий статус проекта

| Stage | Содержание | Статус |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ |
| 1 | TERAD production spectra | ✅ первый вариант принят |
| 2–3 | PTW 30013 benchmark development | ✅ Model B1 принята |
| 3H-4 | CCRI100/250 high-stat validation | ✅ PASS |
| 3H-5 | CCRI135/180 independent validation | ✅ PASS |
| 4 | Co-60 `R_Co` | 🟠 builder fix; MC ещё не запускался |
| 5 | Water `R_Q` для 12 TERAD configurations | ⏸ после Stage 4 |
| 6 | Spectrum / chamber sensitivity | ⏸ |
| 7 | Geometry-response `k_g` | ⏸ |
| 8 | RW3-to-water + 12 direct end-to-end | ⏸ |
| 9 | Итоговые коэффициенты и uncertainty budget | ⏸ |

## Дальнейший production workflow

1. Исправить Stage 4 builder и получить weighted `R_Co`.
2. Рассчитать water `R_Q` для всех **12** TERAD configurations.
3. Вычислить `k_Q,Co = R_Q / R_Co` для каждой клинической конфигурации.
4. Представить относительные geometry-response ratios `k_g` без замены абсолютных расчётов.
5. Оценить sensitivity к TERAD spectrum и ограничениям chamber model.
6. Рассчитать matched RW3 geometry для всех 12 конфигураций.
7. Определить `RW3-to-water` effect.
8. Выполнить direct `end-to-end` RW3 MC для всех 12 конфигураций.
9. Сформировать итоговые коэффициенты и uncertainty budget.

## Правила проекта

- measured HVL TERAD не меняются ради улучшения fit;
- geometry PTW 30013 не подгоняется к benchmark после получения результатов;
- один HVL не определяет спектр однозначно — spectrum ambiguity учитывается отдельно;
- benchmark валидирует методику, но не заменяет TERAD input data;
- F50 не является `reference-only`;
- RW3 рассматривается отдельно от water-response и дополнительно проверяется direct `end-to-end` MC;
- технически неуспешный CI run не трактуется как физический MC-result.

## История разработки

Подробности отклонённых Model A/B0 веток, spectrum-fidelity tests, screening runs и технических итераций сохранены в `docs/`, `results/` и GitHub Actions. README содержит только текущую принятую архитектуру и актуальный production status.
