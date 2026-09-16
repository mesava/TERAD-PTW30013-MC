# TERAD–PTW30013–MC

Monte Carlo проект для определения поправочных коэффициентов для ионизационной камеры **PTW 30013 SN 013488** при клинической дозиметрии киловольтного рентгенотерапевтического аппарата **TERAD 200**.

> **Текущий статус:** Model B1 benchmark-validated; Co-60 anchor — PASS; TERAD matched-water — 12/12 PASS; прямой RW3→water transfer — 12/12 PASS; первичный TiO₂ sensitivity-screen — завершён и показал значимый эффект; **Stage 8S1b (TiO₂ для всех геометрий) — ACTIVE, run `35067286806`**; **Stage 8S2 (спектры вода↔RW3) — ACTIVE, run `35067807801`**.
>
> **Критически важная интерпретация:** все уже полученные TERAD-коэффициенты относятся к **идеализированной, HVL-согласованной модели источника**. Эта модель сознательно использовалась как первый контролируемый физический уровень: W-мишень, nominal anode angle 20°, point source, известная добавочная фильтрация и equivalent-Al fit к измеренному HVL. После получения технических данных трубки начинается второй уровень — **hardware-informed, более реалистичная модель**, где явно проверяются Be-окно 0.8±0.1 мм, конечный фокус Ø7.5 мм, допуск kVp и неопределённость реального угла анода. Текущие коэффициенты не объявляются окончательными клиническими значениями до завершения этих sensitivity-блоков.

## 1. Практическая задача

Камера имеет сертификатный коэффициент калибровки в Co-60:

`N_D,w(Co-60) = 5.389e7 Gy/C`.

Экспериментального `N_D,w,Q` для Q120/Q140/Q150/Q200 нет. Поэтому проект строится от Co-60 calibration basis и напрямую рассчитывает MC-transfer для каждой реальной TERAD/RW3-конфигурации.

Основной практический коэффициент:

`K_Q,g,Co^(RW3→w) = [D_w,water / D_cav,RW3]_(Q,g) / R_Co`.

Клиническая формула:

`D_w = M_corr · N_D,w(Co-60) · K_Q,g,Co^(RW3→w)`.

`M_corr` — показание камеры после необходимых поправок измерительной системы (`k_TP`, `k_s`, `k_pol`, `k_elec` и др. согласно принятой процедуре).

При применении direct coefficient **не нужно дополнительно умножать на отдельные `k_Q` и `k_g`**: изменение качества пучка, клинической геометрии и переход от RW3 к dose-to-water уже находятся внутри `K_Q,g,Co^(RW3→w)`.

## 2. Co-60 anchor и смысл `k_g`

Stage 4 воспроизводит calibration basis камеры:

- SSD = 95 см;
- глубина центра камеры = 5 см воды;
- SDD = 100 см;
- поле 10×10 см² в reference point;
- водный фантом 30×30×30 см³.

Результат:

`R_Co = 1.12016676 ± 0.00104473`, относительная MC-неопределённость 0.0933%, gate PASS.

Отношение `R_Q,g / R_Co` одновременно содержит изменение **качества Q и геометрии g**, поэтому оно не является чистым `k_g`.

Ранее использованное отношение `R_Q,g / R_Q,F50` — только **относительный geometry-response factor относительно F50**. Для F50 оно равно 1 по определению нормировки. F50 — реальная конфигурация SSD 50 см, поле 8×10 см², а не reference geometry TRS-398.

Чистый geometry factor при одном Q можно определить только после явного задания рентгеновской reference geometry `g_ref,Q`:

`k_g,Q^MC = R_Q,g(clin) / R_Q,g(ref)`.

## 3. Канонические качества и геометрии TERAD

| Качество | kV | mA | HVL1 | Добавочная фильтрация |
|---|---:|---:|---:|---|
| Q120 | 120 | 10 | 0.224 мм Cu | 4.0 мм Al |
| Q140 | 140 | 10 | 0.410 мм Cu | 0.2 мм Cu |
| Q150 | 150 | 10 | 0.729 мм Cu | 0.5 мм Cu |
| Q200 | 200 | 7 | 1.452 мм Cu | 1.0 мм Cu |

Для каждого качества используются три реальные конфигурации:

| Аппликатор | SSD | Поле |
|---|---:|---:|
| F40 | 40 см | 6×8 см² |
| F40 | 40 см | 4×15 см² |
| F50 | 50 см | 8×10 см² |

Итого 12 Q/geometry combinations.

## 4. Принятые спектры TERAD — первый, идеализированный уровень модели

Спектры сформированы SpekPy 2.5.4: W reflection target, **nominal anode angle 20°**, `kqp`, bins 0.5 кэВ, известная клиническая фильтрация + неотрицательная equivalent-Al nuisance filtration с fit к измеренному Cu HVL.

| Q | Target HVL | Final HVL | Ошибка |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Один HVL не определяет spectrum однозначно; spectrum ambiguity остаётся отдельным uncertainty contribution.

### 4.1. Что означает «идеализированная модель»

Текущая TERAD source model **не является геометрически полной моделью реальной рентгеновской трубки**. Она была намеренно построена как контролируемая HVL-constrained модель, позволяющая сначала проверить весь MC pipeline, камеру, Co-60 anchor, клинические геометрии и RW3 transfer без введения неподтверждённых proprietary деталей.

В текущем production-варианте:

- материал мишени — W, что соответствует реальной трубке;
- kVp соответствует клиническим режимам;
- известная добавочная Al/Cu-фильтрация учтена;
- measured Cu HVL воспроизводится;
- Be-окно трубки **не моделируется отдельным физическим слоем**;
- его вклад и другие неизвестные элементы inherent filtration фактически поглощаются fitted equivalent-Al parameter;
- источник в transport geometry — **point source**;
- anode angle = **20°** — nominal SpekPy assumption, а не подтверждённая характеристика TERAD;
- proprietary tube-head/applicator body scatter не моделируется, если геометрия и материалы неизвестны.

Поэтому Stage 5, Stage 8, Stage 8S1, Stage 8S1b и первичный Stage 8S2 следует трактовать как результаты **идеализированной/HVL-согласованной модели**. Они дают физически содержательный baseline, но ещё не являются окончательной hardware-specific клинической моделью TERAD.

### 4.2. Новые подтверждённые характеристики реальной трубки

По технической документации и уточнённым данным для используемой трубки известны следующие параметры:

| Параметр | Реальная трубка | Текущая MC-модель | Статус / действие |
|---|---|---|---|
| Материал анода | **вольфрам (W)** | W | ✅ уже соответствует |
| Номинальное напряжение трубки | до 225 кВ | 120/140/150/200 кВ | ✅ клинические режимы внутри диапазона |
| Точность выходного напряжения | **0.25%** | fixed nominal kVp | ⚠️ добавить kVp sensitivity |
| Точность тока эмиссии | **0.25%** | mA хранится как metadata | низкий приоритет для нормированного `K`, важнее для absolute output |
| Выходное окно | **Be** | отдельно не моделируется | ⚠️ требуется explicit Be model |
| Толщина Be-окна | **0.8 ± 0.1 мм** | absorbed in equivalent-Al nuisance fit | 🔴 высокий приоритет sensitivity |
| Материал мишени | **W** | W | ✅ |
| Диаметр фокусного пятна | **7.5 мм** | point source | 🔴 finite-source sensitivity |
| Реальный угол анода | неизвестен | nominal **20°** | 🔴 model-form sensitivity; 20° нельзя считать подтверждённым |
| Угол раствора полезного пучка по тех. характеристикам | ≤30° | поле задаётся клинической апертурой | не является anode angle |
| Литературное указание о полезном выходе порядка 40° | приблизительная характеристика полезного cone | не используется как `th` | не является anode angle |
| Основной фильтр | Al или Cu | реальные клинические Al/Cu filters | ✅ |
| Корпус/внутренние конструктивные элементы | часть фотонов поглощается внутри анода/корпуса | не моделируются явно | учитываются только косвенно через HVL fit; остаётся model-form limitation |

### 4.3. Почему 30–40° нельзя подставить как угол анода

Угол раствора полезного рентгеновского пучка и угол наклона вольфрамовой мишени — разные физические величины.

Литературное описание, что фотоны после взаимодействия в аноде испускаются в телесный угол `4π`, а полезный выход ограничен приблизительно углом порядка 40°, описывает **пространственный выход полезного пучка после самопоглощения и конструктивного ограничения трубкой**. Значение ≤30° из технических характеристик также относится к раствору рентгеновского пучка. Ни одно из этих значений не является автоматически SpekPy parameter `th`.

Следовательно:

- `th = 20°` остаётся nominal model assumption;
- 30° и ~40° **не заменяют** его;
- реальный anode angle должен либо быть найден в документации, либо учтён как model-form sensitivity interval.

### 4.4. Второй уровень: hardware-informed более реалистичная модель

Следующий spectrum/source model должен проверять физическую цепочку:

`W target → Be window (0.8±0.1 мм) → клинический Al/Cu filter → residual equivalent filtration fit → measured Cu HVL`.

Важно: residual equivalent-Al остаётся допустимым nuisance parameter только для неописанных компонентов tube head, но **известное Be-окно больше не должно прятаться внутри него**.

Для source geometry необходимо сравнить:

`point source` ↔ `finite circular focal spot Ø7.5 мм`.

Для spectrum/model-form uncertainty необходимо отдельно проверить:

- Be = 0.7 / 0.8 / 0.9 мм;
- kVp endpoints по технической точности 0.25%;
- несколько физически разумных значений anode angle при обязательном повторном fit к measured HVL;
- сохранение measured clinical HVL как жёсткого экспериментального ограничения.

Главная проверяемая величина для каждого hardware-informed варианта:

`ΔK = K_hardware-informed / K_idealized - 1`.

Если отличие статистически/клинически мало, текущая идеализированная модель получит количественное подтверждение. Если отличие значимо, hardware-informed variant станет новой nominal model, а текущие значения сохранятся как baseline для оценки model-form correction.

## 5. PTW 30013 Model B1

Model B1 — публичная surrogate-модель, а не proprietary blueprint производителя.

Основные параметры:

- sensitive radius 3.05 мм;
- sensitive length 23.0 мм;
- graphite wall 0.09 мм;
- PMMA wall 0.335 мм;
- центральный Al-электрод 1.15 мм;
- PMMA tip surrogate 1.5 мм;
- reference point 13 мм от physical tip;
- cavity mass `7.832972283369083e-04 g`.

Benchmark по CCRI100/135/180 относительно CCRI250 прошёл без дальнейшей подгонки геометрии камеры.

## 6. Stage 5 — TERAD matched-water: 12/12 PASS

Run `34931189724`.

Для всех 12 точек использованы 300M histories / 30 batches, принятые TERAD spectra, Model B1, физическая глубина центра камеры 2.0 см в воде и клинические SSD 40/50 см. Максимальная статистическая неопределённость `R_Q,g` < 0.5%.

**Интерпретация:** Stage 5 является baseline для **идеализированной TERAD source model**, описанной в разделе 4. После hardware-informed sensitivity этот набор будет либо подтверждён, либо скорректирован.

Файлы:

- `results/stage5_terad_water_summary.csv`
- `results/stage5_intrinsic_kq.csv`
- `results/stage5_absolute_scores.csv`
- `results/stage5_gate.txt`

## 7. Stage 8 — реальный RW3→water direct: 12/12 PASS

Run `34959596116`.

Принятая реальная RW3-геометрия:

- phantom 29672, 30×30 см²;
- PTW30013 в plate 29672/U19;
- ось камеры на 7 мм ниже верхней стороны U19;
- дополнительно 13 мм RW3 над U19;
- physical chamber-centre/reference-point depth = **20 мм = 2.0 см**;
- камера горизонтальна, ось перпендикулярна CAX;
- около 10 см RW3 downstream;
- applicator contact with RW3 surface;
- SSD 40/50 см до поверхности RW3.

2.0 см — физическая глубина, а не water-equivalent depth.

Номинальный RW3: полистирол `C8H8` с 2.0±0.4% TiO₂ по массе, density 1.045 г/см³, electron density 1.012×water, mean Z/A 0.536.

| Конфигурация | `K_Q,g,Co^(RW3→w)` |
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

Stage 8 gate: 12/12 PASS; max `u(R_direct)=0.44695%`; direct и factorized forms согласуются в пределах 0.00406%.

**Интерпретация:** эти 12 коэффициентов — текущий **идеализированный baseline**. Они уже полезны для физического анализа и предварительного пересчёта, но пока не обозначаются как финальные hardware-specific clinical coefficients. Следующая задача — оценить, насколько они сдвигаются при explicit Be window, finite focal spot и других подтверждённых характеристиках реальной трубки.

Файлы:

- `results/stage8_rw3_direct_summary.csv`
- `results/stage8_gate.txt`
- `docs/STAGE8_RW3_DIRECT.md`

## 8. Что происходит при переходе вода→RW3

На одинаковой физической глубине 2 см:

| Q | `D_w / D_RW3` | `D_RW3` относительно воды |
|---|---:|---:|
| Q120 | ~1.134 | ~88.2% |
| Q140 | ~1.117 | ~89.5% |
| Q150 | ~1.094 | ~91.4% |
| Q200 | ~1.068 | ~93.7% |

RW3 therefore не является дозиметрически эквивалентным воде в диапазоне 120–200 кВ. Эффект уменьшается с ростом энергии, но остаётся значимым при 200 кВ.

Эти значения также относятся к текущей идеализированной source model; Stage 8S2 и последующий hardware-informed spectrum sensitivity покажут устойчивость вывода к более реалистичному описанию трубки.

## 9. Stage 8S1 — TiO₂ sensitivity F50: завершён

Run `35012034674`.

Для F50 8×10 при fixed density 1.045 г/см³ рассчитаны manufacturer tolerance endpoints 1.6% и 2.4% TiO₂ относительно nominal 2.0%.

| Q | shift при 1.6% | shift при 2.4% | preliminary `u_rect`, % |
|---|---:|---:|---:|
| Q120 | -1.147% | +2.076% | 1.198 |
| Q140 | -0.045% | +2.548% | 1.471 |
| Q150 | -0.413% | +1.758% | 1.015 |
| Q200 | -0.080% | +0.977% | 0.564 |

Эффект TiO₂ существенно превышает nominal MC statistics; максимальный endpoint shift = 2.55%.

## 10. Stage 8S1b — TiO₂ sensitivity для всех F40 геометрий: ACTIVE

Run **`35067286806`**.

Расширение Stage 8S1 на оставшиеся 8 конфигураций:

- F40 6×8 и F40 4×15;
- Q120/Q140/Q150/Q200;
- TiO₂ = 1.6% и 2.4%;
- итого **16 endpoint MC**;
- 300M histories / 30 batches на точку;
- используются соответствующие nominal Stage 8 seed pairs.

Preflight и generation accepted TERAD spectra — PASS. Production matrix запущена, max-parallel = 4.

Workflow: `.github/workflows/stage8s1b-rw3-tio2-all-geometries.yml`.

## 11. Stage 8S2 — спектральное сравнение вода↔RW3: ACTIVE

Run **`35067807801`**.

Цель — напрямую измерить, как RW3 меняет photon fluence spectrum по глубине и физически объяснить Stage 8 dose-to-medium differences.

Первичный F50-screen:

- SSD 50 см;
- поле 8×10 см² задано на поверхности;
- Q120/Q140/Q150/Q200;
- среды water и nominal RW3;
- scoring depths: **0.001 см (0+), 1.0 см, 2.0 см**;
- центральный planar scoring circle radius = 0.5 см;
- 250 linear energy bins от 1 до 251 кэВ (1 кэВ/bin);
- `egs_fluence_scoring` в отдельном `tutor7pp`, без `egs_chamber` TmpPhsp replay;
- 50M histories на точку;
- всего **24 transport points**.

Регистрируются:

- differential photon fluence `dPhi/dE`;
- integrated photon fluence;
- energy fluence;
- mean and median energy;
- E10/E25/E50/E75/E90;
- fractions below 20/30/50 keV;
- `Phi_RW3(E,z)/Phi_water(E,z)`.

Preflight Stage 8S2 — PASS; generation accepted TERAD spectra — PASS; spectral matrix ожидает/получает runners после Stage 8S1b.

Этот этап является физическим объяснением RW3 correction и **не является дополнительным множителем** к `K_Q,g,Co^(RW3→w)`.

Stage 8S2 также пока использует **идеализированную source model**. Его задача — сначала изолировать эффект самой среды water↔RW3. Позже ключевые spectral comparisons будут повторены для hardware-informed source model, чтобы проверить, меняется ли вывод при explicit Be и finite focal spot.

Файлы архитектуры:

- `scripts/build_stage8s2_spectral_input.py`
- `scripts/run_stage8s2_spectral_point.sh`
- `scripts/summarize_stage8s2_spectrum.py`
- `scripts/evaluate_stage8s2_spectral.py`
- `.github/workflows/stage8s2-water-rw3-spectral-scoring.yml`
- `docs/STAGE8S2_WATER_RW3_SPECTRAL_SCORING.md`

## 12. Следующие этапы

1. Дождаться Stage 8S1b и сформировать geometry-specific TiO₂ uncertainty.
2. Дождаться Stage 8S2; при необходимости увеличить histories только для недостаточно точных spectral points.
3. **Hardware-informed spectrum sensitivity:** explicit Be 0.7/0.8/0.9 мм при сохранении measured HVL и residual equivalent-filtration fit.
4. **kVp sensitivity:** endpoints, соответствующие технической точности 0.25%, с повторным контролем HVL/spectrum.
5. **Anode-angle model-form sensitivity:** несколько физически разумных углов, потому что реальный угол анода пока неизвестен; 30–40° beam-opening data не подменяют anode angle.
6. **Finite focal spot sensitivity:** point source ↔ circular focal spot Ø7.5 мм.
7. RW3 geometry sensitivity: physical depth, slab-thickness tolerance, accumulated overlying thickness, air gaps/contact.
8. Rectangular-field orientation: 6×8↔8×6 и 4×15↔15×4 относительно chamber axis/stem.
9. PTW30013 model-form uncertainty в пределах benchmark-compatible model space без tuning к TERAD.
10. Applicator/head limitation: оценка unknown proprietary body scatter; при появлении размеров/материалов — отдельный MC sensitivity.
11. Сопоставить idealized и hardware-informed coefficients через `ΔK = K_realistic/K_idealized - 1` для всех клинических конфигураций.
12. Экспериментальная валидация реальными измерениями PTW30013 в RW3.
13. Финальный uncertainty budget: MC statistics, Co-60 anchor, TiO₂, RW3 geometry, source hardware, spectrum ambiguity, orientation, chamber model, positioning и experimental components.
14. Финальная клиническая таблица `K_Q,g,Co^(RW3→w)`, `u_c`, `U(k=2)`, область применимости и ограничения.

## 13. Текущий статус

| Этап | Содержание | Статус |
|---:|---|---|
| 0 | EGSnrc / egs++ infrastructure | ✅ |
| 1 | TERAD spectra — idealized/HVL-constrained baseline | ✅ PASS |
| 2–3 | PTW30013 benchmark | ✅ PASS |
| 4 | Co-60 anchor | ✅ PASS |
| 5 | matched-water TERAD — idealized source baseline | ✅ 12/12 PASS |
| 8 | direct RW3→water — idealized source baseline | ✅ 12/12 PASS |
| 8S1 | TiO₂ F50 screen | ✅ complete |
| 8S1b | TiO₂ all F40 geometries | 🟡 ACTIVE |
| 8S2 | water↔RW3 spectral scoring, idealized source | 🟡 ACTIVE |
| 8S3 | hardware-informed source/spectrum sensitivity: Be, kVp, anode angle, focal spot | ⏳ NEXT |
| 9 | geometry/orientation/chamber/applicator sensitivities | ⏳ |
| 10 | experimental validation + final uncertainty | ⏳ |

## 14. Зафиксированные правила проекта

- measured TERAD HVL не меняются ради улучшения agreement;
- известные hardware parameters не прячутся в nuisance parameters после того, как становятся доступными: Be-окно должно моделироваться явно в hardware-informed stage;
- nominal 20° anode angle не считается реальной спецификацией TERAD без подтверждающей документации;
- угол раскрытия полезного пучка 30–40° не интерпретируется как anode angle;
- finite focal spot Ø7.5 мм должен быть отдельно проверен относительно point-source baseline;
- chamber geometry не подгоняется после benchmark validation;
- одинаковый HVL не означает однозначный spectrum;
- missing proprietary applicator geometry не выдумывается;
- RW3 physical depth = 2.0 см и не переопределяется как water-equivalent depth;
- direct coefficient не умножается повторно на отдельные `k_Q`, `k_g` или `D_w/D_RW3`;
- текущие Stage 5/8 coefficients являются **идеализированным baseline**, а не окончательной hardware-specific truth;
- nominal MC statistical uncertainty не является полной клинической uncertainty;
- technical CI failure не трактуется как physical MC failure.

Official EGSnrc pinned commit: `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`.
