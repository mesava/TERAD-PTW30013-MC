# TERAD–PTW30013–MC

Monte Carlo проект для определения поправочных коэффициентов для ионизационной камеры **PTW 30013 SN 013488** при клинической дозиметрии киловольтного рентгенотерапевтического аппарата **TERAD 200**.

> **Текущий статус:** Model B1 benchmark — PASS; Co-60 anchor — PASS; TERAD matched-water — 12/12 PASS; direct RW3→water baseline — 12/12 PASS; Stage 8S1/8S1b TiO₂ sensitivity — завершены; **Stage 8S2 water↔RW3 spectral scoring — окончательно PASS после targeted refinement, 24/24 и max p95 = 4.96714%**; Stage 8S3a hardware feasibility — PASS; Stage 8S3b hardware-informed F50 — 16/16 + PASS; **Stage 8S3c Be/kVp/anode-angle hardware-spectrum sensitivity — ACTIVE, run `35220527537`**.
>
> **Ключевая интерпретация:** Stage 5/8 остаются контролируемым idealized/HVL-constrained baseline. Stage 8S3 показал, что explicit Be и finite focal spot способны менять `K` на величину порядка 1–2%, поэтому hardware-informed source model является необходимым следующим уровнем. До завершения source/RW3/geometry/model sensitivities ни один hardware-informed коэффициент не объявляется окончательным clinical truth.

## 1. Практическая задача

Камера имеет сертификатный коэффициент калибровки в Co-60:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

Экспериментального `N_D,w,Q` для Q120/Q140/Q150/Q200 нет. Основной clinical transfer рассчитывается напрямую от Co-60 calibration basis:

`K_Q,g,Co^(RW3→w) = [D_w,water / D_cav,RW3]_(Q,g) / R_Co`.

Клиническая формула:

`D_w = M_corr · N_D,w(Co-60) · K_Q,g,Co^(RW3→w)`.

`M_corr` — показание камеры после необходимых измерительных поправок (`k_TP`, `k_s`, `k_pol`, `k_elec` и др. согласно принятой процедуре).

При использовании direct coefficient **не нужно дополнительно умножать на отдельные `k_Q`, `k_g` или `D_w/D_RW3`**: изменение качества, геометрии и переход RW3→water уже находятся внутри `K_Q,g,Co^(RW3→w)`.

## 2. Co-60 anchor

Stage 4 использует:

- SSD = 95 см;
- глубину центра камеры = 5 см воды;
- SDD = 100 см;
- поле 10×10 см²;
- водный фантом 30×30×30 см³.

Результат:

`R_Co = 1.12016676 ± 0.00104473`, относительная MC-неопределённость 0.0933%, gate PASS.

Отношение `R_Q,g / R_Co` одновременно меняет качество `Q` и геометрию `g`, поэтому это **комбинированный transfer**, а не чистый geometry factor.

`R_Q,g / R_Q,F50` следует трактовать только как **relative geometry-response factor относительно F50**. F50 не является автоматически reference geometry TRS-398.

## 3. Канонические качества и клинические геометрии

| Качество | kV | mA | HVL1 | Добавочная фильтрация |
|---|---:|---:|---:|---|
| Q120 | 120 | 10 | 0.224 мм Cu | 4.0 мм Al |
| Q140 | 140 | 10 | 0.410 мм Cu | 0.2 мм Cu |
| Q150 | 150 | 10 | 0.729 мм Cu | 0.5 мм Cu |
| Q200 | 200 | 7 | 1.452 мм Cu | 1.0 мм Cu |

| Аппликатор | SSD | Поле |
|---|---:|---:|
| F40 | 40 см | 6×8 см² |
| F40 | 40 см | 4×15 см² |
| F50 | 50 см | 8×10 см² |

### 3.1. Плоскость определения размера поля

**Размеры 6×8, 4×15 и 8×10 см² определены на поверхности фантома, в контактной плоскости выхода аппликатора.** Аппликатор прижат непосредственно к RW3; в matched-water расчётах используется соответствующая плоскость поверхности воды. SSD 40/50 см также относится к поверхности.

Камера находится на физической глубине **2.0 см**. Размер поля не относится к плоскости камеры.

В idealized point-source Stage 5/8 это условие уже выполнялось через геометрически эквивалентную проекцию. Например F50 8×10 см² на поверхности соответствовал computational rectangle 8.32×10.40 см² в плоскости камеры, который обратно проецировался в ровно 8×10 см² на поверхность. Поэтому **Stage 5/8 не требуют исправления по размеру поля**.

Для finite circular focal spot Ø7.5 мм physical aperture задаётся непосредственно в плоскости поверхности фантома / contact applicator plane.

## 4. Два уровня модели рентгеновской трубки

### 4.1. Idealized / HVL-constrained baseline

Первоначальная production-модель:

- W reflection target;
- SpekPy 2.5.4;
- nominal `th = 20°`;
- point source;
- клиническая Al/Cu-фильтрация;
- nonnegative equivalent-Al fit к измеренному Cu HVL.

| Q | Target HVL | Final HVL | Ошибка |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Эта модель является контролируемым baseline, но не полной моделью реальной трубки.

### 4.2. Подтверждённые характеристики реальной трубки

| Параметр | Реальная трубка | Baseline MC | Hardware-informed действие |
|---|---|---|---|
| Материал анода | **W** | W | соответствует |
| Рабочее напряжение | до 225 кВ | 120/140/150/200 кВ | соответствует диапазону |
| Точность напряжения | **0.25%** | fixed kVp | operational sensitivity |
| Выходное окно | **Be** | явно отсутствует | explicit Be |
| Be-окно | **0.8 ± 0.1 мм** | скрыто в equivalent-Al | 0.7/0.8/0.9 мм model sensitivity |
| Фокус | **круглый Ø7.5 мм** | point | finite circular source |
| Реальный угол анода | неизвестен | nominal 20° | model-form sensitivity |
| Useful-beam opening | ≤30° по ТХ; ~40° в литературном описании | не используется как `th` | не путать с anode angle |
| Основной фильтр | Al/Cu | Al/Cu | соответствует |
| Tube head / applicator body | полная геометрия неизвестна | не моделируется | limitation / future sensitivity |

Угол полезного пучка 30–40° и угол анода — разные физические параметры. Значения 30–40° **не подставляются** вместо SpekPy `th`.

### 4.3. Stage 8S3a — hardware spectrum feasibility: PASS

Hardware-informed chain:

`W target → Be window → clinical Al/Cu filter → residual equivalent-Al → measured HVL`.

Для `Be = 0.8 мм`, screening `th = 20°`:

| Q | HVL после Be + clinical filter, мм Cu | Target HVL | Residual Al |
|---|---:|---:|---:|
| Q120 | 0.207924 | 0.224 | 0.42676 мм |
| Q140 | 0.389919 | 0.410 | 0.49457 мм |
| Q150 | 0.724803 | 0.729 | 0.20761 мм |
| Q200 | 1.455320 | 1.452 | 0 мм |

Все четыре качества совместимы с measured HVL без отрицательной residual filtration в принятом ±0.5% HVL gate.

Anode-angle feasibility-screen: 20°, 25° и 30° совместимы с measured HVL для всех четырёх Q; 10° слишком жёсткий для всех Q; 15° не совместим с Q150/Q200. Это **model-form probes**, а не определение реального угла анода.

## 5. PTW 30013 Model B1

Model B1 — публичная surrogate-модель, а не proprietary blueprint PTW.

- sensitive radius 3.05 мм;
- sensitive length 23.0 мм;
- graphite wall 0.09 мм;
- PMMA wall 0.335 мм;
- central Al electrode 1.15 мм;
- PMMA tip surrogate 1.5 мм;
- cavity mass `7.832972283369083e-04 g`.

Benchmark CCRI100/135/180 относительно CCRI250 — PASS. После benchmark геометрия камеры не подгоняется к TERAD.

## 6. Stage 5 — matched-water baseline: 12/12 PASS

Run `34931189724`. Для всех 12 конфигураций: 300M histories / 30 batches, Model B1, physical chamber-centre depth 2.0 см, клинические SSD 40/50 см.

Stage 5 — baseline для idealized TERAD source model.

## 7. Stage 8 — direct RW3→water baseline: 12/12 PASS

Run `34959596116`.

RW3 geometry:

- phantom 29672, 30×30 см²;
- U19 plate для PTW30013;
- H1 = 7 мм;
- дополнительно 13 мм RW3 сверху;
- physical chamber-centre depth = **20 мм = 2.0 см**;
- аппликатор в контакте с поверхностью;
- SSD относится к поверхности;
- около 10 см RW3 downstream.

Номинальный RW3: polystyrene `C8H8` + 2.0±0.4% TiO₂ by mass, density 1.045 г/см³.

| Конфигурация | Idealized baseline `K_Q,g,Co^(RW3→w)` |
|---|---:|
| Q120 F40 4×15 | **0.904762** |
| Q120 F40 6×8 | **0.902315** |
| Q120 F50 8×10 | **0.890691** |
| Q140 F40 4×15 | **0.927195** |
| Q140 F40 6×8 | **0.922061** |
| Q140 F50 8×10 | **0.905650** |
| Q150 F40 4×15 | **0.948126** |
| Q150 F40 6×8 | **0.950385** |
| Q150 F50 8×10 | **0.933468** |
| Q200 F40 4×15 | **0.967533** |
| Q200 F40 6×8 | **0.961324** |
| Q200 F50 8×10 | **0.958870** |

Stage 8 gate: max `u(R_direct)=0.44695%`, direct/factorized agreement within 0.00406%.

Эти коэффициенты являются **idealized baseline**, а не окончательной hardware-specific truth.

## 8. Переход вода → RW3 в baseline model

На одинаковой физической глубине 2 см средний dose-to-medium ratio:

| Q | `D_w / D_RW3` | `D_RW3 / D_w` |
|---|---:|---:|
| Q120 | ~1.134 | ~0.882 |
| Q140 | ~1.117 | ~0.895 |
| Q150 | ~1.094 | ~0.914 |
| Q200 | ~1.068 | ~0.937 |

Это **не чистый коэффициент ослабления**: отношение объединяет различия спектрального fluence и energy-absorption response двух сред.

## 9. Stage 8S1 + 8S1b — TiO₂ sensitivity: завершён

Manufacturer tolerance: TiO₂ = 2.0±0.4 percentage points by mass. Screening endpoints: 1.6% и 2.4%, density fixed 1.045 г/см³.

### F50 8×10

| Q | shift 1.6% | shift 2.4% | screening `u_rect`, % |
|---|---:|---:|---:|
| Q120 | -1.147% | +2.076% | 1.198 |
| Q140 | -0.045% | +2.548% | 1.471 |
| Q150 | -0.413% | +1.758% | 1.015 |
| Q200 | -0.080% | +0.977% | 0.564 |

### F40

| Конфигурация | shift 1.6% | shift 2.4% | screening `u_rect`, % |
|---|---:|---:|---:|
| Q120 4×15 | -2.536% | +1.079% | **1.464** |
| Q120 6×8 | -2.489% | +1.218% | **1.437** |
| Q140 4×15 | -1.478% | +1.012% | 0.853 |
| Q140 6×8 | -0.749% | +0.898% | 0.519 |
| Q150 4×15 | -0.222% | +0.365% | 0.211 |
| Q150 6×8 | -1.679% | +0.075% | 0.969 |
| Q200 4×15 | -0.823% | -0.191% | 0.475 |
| Q200 6×8 | -1.035% | +0.861% | 0.598 |

Stage 8S1b: 16/16 endpoints + evaluator PASS; max `u(Dcav)=0.404%`; worst screening `u_rect=1.464%` для Q120 F40 4×15.

`u_rect` является screening contribution, а не автоматически принятой standard uncertainty: окончательная probability model для TiO₂ tolerance должна быть обоснована отдельно.

Файлы:

- `results/stage8s1b_rw3_tio2_all_geometries_summary.csv`
- `results/stage8s1b_gate.txt`

## 10. Stage 8S2 — spectral scoring water↔RW3: PASS

Исходный run `35067807801`: **24/24 transport points success**.

Geometry: F50, SSD50, поле 8×10 см² на поверхности; Q120/Q140/Q150/Q200; water/RW3; depths 0.001, 1.0 и 2.0 см; scoring circle r=0.5 см; 250 bins по 1 кэВ.

Первичный набор 50M/point не прошёл только statistical precision criterion:

`p95(relative uncertainty of active spectral bins) <= 5%`.

Диагностика `35184635832` выбрала 11 слабых точек. Stage 8S2b `35184729305` точечно увеличил statistics; после него единственной пограничной точкой оставалась Q140/water/2.0 см (`p95=5.06883%`). Stage 8S2c `35201448512` пересчитал только эту точку на 80M histories.

Финальный результат:

- 24/24 combined spectral points — **PASS**;
- final evaluator — **PASS**;
- max `p95(relative uncertainty active bins) = 4.96714%`;
- transport/physics failures = 0.

Stage 8S2 является физическим объяснением spectral transfer water↔RW3 и **не создаёт дополнительный множитель** к clinical `K`.

Файлы:

- `results/stage8s2c_water_rw3_spectral_summary.csv`
- `results/stage8s2c_gate.txt`

### 10.1. Основной спектральный вывод

При одинаковой физической глубине RW3 немного увеличивает total scored photon fluence относительно воды, но средняя энергия в RW3 становится ниже. На глубине 2 см:

- Q120: `Phi_RW3/Phi_water ≈ 1.0332`, mean energy shift ≈ **-1.219%**;
- Q140: `≈1.0205`, mean energy shift ≈ **-0.871%**;
- Q150: `≈1.0136`, mean energy shift ≈ **-0.659%**;
- Q200: `≈1.0128`, mean energy shift ≈ **-0.510%**.

Это подтверждает, что Stage 8 RW3→water correction нельзя интерпретировать как простой transmission factor.

## 11. Stage 8S3b — hardware-informed F50: 16/16 + PASS

Run `35072405754`.

Использовано:

- F50, SSD50, поле 8×10 см² на поверхности;
- water и nominal RW3;
- explicit `Be = 0.8 мм`;
- screening `th = 20°`;
- nonnegative residual-Al constrained к measured HVL;
- point source и finite circular focal spot Ø7.5 мм;
- 300M histories / 30 batches;
- water numerator и RW3 chamber denominator используют одну source variant.

| Q | Idealized `K` | HW point `K` | point vs idealized | HW Ø7.5 `K` | finite vs HW point | finite vs idealized |
|---|---:|---:|---:|---:|---:|---:|
| Q120 | 0.890691 | **0.897357** | **+0.748%** | **0.888856** | **-0.947%** | -0.206% |
| Q140 | 0.905650 | **0.920261** | **+1.613%** | **0.916741** | -0.383% | **+1.225%** |
| Q150 | 0.933468 | **0.946495** | **+1.396%** | **0.943263** | -0.342% | **+1.049%** |
| Q200 | 0.958870 | **0.956967** | -0.198% | **0.957464** | +0.052% | -0.147% |

Gate:

- 8/8 derived coefficient rows PASS;
- max `u(R_direct)=0.455%`;
- max `|HW point vs idealized| = 1.613%`;
- max `|finite vs HW point| = 0.947%`.

Интерпретация:

1. **Одинаковый HVL не гарантирует одинаковый `K`.** Explicit Be + residual-HVL fit изменяет спектральную форму достаточно, чтобы `K` сдвигался до ~1.6%.
2. **Point-source approximation не всегда нейтральна.** Для Q120 finite Ø7.5 мм меняет `K` почти на -0.95%; Q140/Q150 ~-0.3…-0.4%; Q200 почти 0.
3. Hardware-informed finite-source result пока не финальный clinical coefficient: остаются source/RW3/geometry/model sensitivities.

Файлы:

- `results/stage8s3b_f50_hardware_source_summary.csv`
- `results/stage8s3b_gate.txt`

## 12. Stage 8S3c — Be / kVp / anode-angle sensitivity: ACTIVE

Run **`35220527537`**.

Stage 8S3c использует F50/SSD50/8×10 на поверхности и **фиксирует более реалистичную finite circular source Ø7.5 мм**. Номинальный reference не пересчитывается: используются уже принятые Stage 8S3b finite-source coefficients для `Be=0.8 мм`, screening `th=20°`.

Production matrix содержит 6 non-nominal source variants × 4 Q × 2 media = **48 MC points**, каждый по **300M histories / 30 batches**:

| Family | Variants | Физическая интерпретация |
|---|---|---|
| Be window | 0.7 и 0.9 мм Be, `th=20°` | model-form endpoints; residual Al **re-fit к measured HVL** |
| kVp accuracy | nominal kVp ×0.9975 и ×1.0025 | operational endpoints; **Be + clinical filter + nominal residual Al фиксированы, HVL не refit** |
| anode angle | 25° и 30°, Be 0.8 мм | model-form probes; residual Al **re-fit к measured HVL** |

### 12.1. Почему kVp и Be/anode обрабатываются по-разному

Для Be thickness и неизвестного anode angle исследуется **model ambiguity при наличии измеренного HVL**. Поэтому residual equivalent-Al остаётся nuisance parameter и повторно подгоняется, но только неотрицательно.

Для ±0.25% kVp исследуется **реальное operational deviation напряжения**. Физическая фильтрация трубки при этом не меняется. Если после изменения kVp снова подогнать residual Al к прежнему HVL, часть эффекта voltage error будет искусственно компенсирована. Поэтому в Stage 8S3c kVp endpoints рассчитываются при фиксированной nominal filtration и без нового HVL fit.

Anode-angle 25°/30° являются только model-form probes. Они **не являются** спецификацией TERAD и не объявляются formal uncertainty bounds.

Сравниваемая величина:

`ΔK_variant = K_variant(finite Ø7.5) / K_nominal,Stage8S3b(finite Ø7.5) - 1`.

Общий `R_Co` сокращается в этом относительном сравнении; uncertainty ratio оценивается по двум independent direct-transfer MC estimates, а не через повторное добавление одной и той же Co-60 uncertainty.

Текущий статус при запуске: **preflight PASS**; spectrum generation/gate выполняется; production 48×300M стартует только после spectrum PASS.

Файлы архитектуры:

- `scripts/generate_stage8s3c_spectra.py`
- `scripts/run_stage8s3c_point.sh`
- `scripts/evaluate_stage8s3c_f50.py`
- `.github/workflows/stage8s3c-hardware-spectrum-sensitivity.yml`

## 13. Следующие этапы

1. Завершить **Stage 8S3c** и определить sensitivity `K` к Be, kVp и physically feasible anode-angle model space.
2. После выбора nominal hardware-informed source распространить его с F50 на **все 12 клинических конфигураций**.
3. RW3 geometry sensitivity: physical depth, slab-thickness tolerance, accumulated top-stack thickness, contact/air gaps.
4. Rectangular-field orientation: 6×8↔8×6 и 4×15↔15×4 относительно chamber axis/stem.
5. PTW30013 model-form uncertainty только в benchmark-compatible model space.
6. Applicator/head limitation: proprietary body scatter не выдумывать; при появлении материалов/размеров моделировать отдельно.
7. При необходимости повторить ключевой water↔RW3 spectral comparison уже для выбранной nominal hardware-informed source model.
8. Экспериментальная validation PTW30013 в RW3.
9. Финальный uncertainty budget и таблица `K`, `u_c`, `U(k=2)` с областью применимости.

## 14. Текущий статус

| Этап | Содержание | Статус |
|---:|---|---|
| 0 | EGSnrc / egs++ infrastructure | ✅ |
| 1 | idealized/HVL-constrained TERAD spectra | ✅ PASS |
| 2–3 | PTW30013 benchmark | ✅ PASS |
| 4 | Co-60 anchor | ✅ PASS |
| 5 | matched-water TERAD baseline | ✅ 12/12 PASS |
| 8 | direct RW3→water baseline | ✅ 12/12 PASS |
| 8S1 | TiO₂ F50 | ✅ complete |
| 8S1b | TiO₂ all F40 geometries | ✅ 16/16 + PASS |
| 8S2 | water↔RW3 spectral scoring | ✅ 24/24 + precision PASS |
| 8S2b | targeted refinement | ✅ complete |
| 8S2c | final Q140/water/2cm closeout | ✅ PASS; max p95=4.96714% |
| 8S3a | hardware spectrum feasibility + finite-source smoke | ✅ PASS |
| 8S3b | hardware-informed F50 point↔Ø7.5 мм | ✅ 16/16 + PASS |
| 8S3c | Be/kVp/anode-angle F50 finite-source sensitivity | 🟡 ACTIVE — run `35220527537` |
| 9 | RW3/geometry/orientation/chamber/applicator sensitivities | ⏳ |
| 10 | experimental validation + final uncertainty | ⏳ |

## 15. Зафиксированные правила проекта

- measured TERAD HVL не меняются ради улучшения agreement;
- известное Be-окно моделируется явно в hardware-informed model;
- residual filtration всегда неотрицательна;
- для **model-form** Be/anode variants measured HVL может использоваться как constraint через nonnegative residual-Al refit;
- для **operational kVp ±0.25% sensitivity residual filtration не refit**, потому что физическая фильтрация не меняется вместе с ошибкой напряжения;
- clinical field dimensions относятся к **поверхности фантома / contact applicator plane**;
- finite focal spot Ø7.5 мм моделируется как circular source, physical aperture — на поверхности;
- nominal `th=20°` не считается реальной спецификацией TERAD;
- 25°/30° в Stage 8S3c — model probes, а не доказанный диапазон реального угла;
- 30–40° useful-beam opening не является автоматически anode angle;
- chamber geometry не подгоняется после benchmark validation;
- одинаковый HVL не означает однозначный spectrum;
- missing proprietary applicator/head geometry не выдумывается;
- RW3 physical depth = 2.0 см, не water-equivalent depth;
- direct coefficient не умножается повторно на `k_Q`, `k_g` или `D_w/D_RW3`;
- Stage 5/8 = **idealized baseline**;
- Stage 8S3 = **hardware-informed comparison**, пока не финальная truth;
- nominal MC statistics не равны полной clinical uncertainty;
- endpoint spans не превращаются автоматически в standard uncertainty без обоснованной probability model;
- technical CI failure не трактуется как physical MC failure.

Official EGSnrc pinned commit: `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`.
