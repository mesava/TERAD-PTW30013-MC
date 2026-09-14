# TERAD-PTW30013-MC

Monte Carlo проект для определения chamber-specific коэффициентов коррекции по качеству пучка для ионизационной камеры PTW 30013 на киловольтном рентгенотерапевтическом аппарате TERAD.

> **Каноническое ТЗ:** `docs/CANONICAL_MC_TASK.md` и `data/terad_clinical_geometries.csv` задают исходные данные TERAD, все 12 клинических комбинаций аппликаторов и реальную геометрию измерений в RW3. Эти данные имеют приоритет над benchmark-ветками.

> **Текущий этап:** выполняется **Stage 3H-5 — независимая проверка промежуточных качеств CCRI135 и CCRI180 для фиксированной nominal Model B1**. Stage 3H-4 успешно подтвердил endpoint benchmark CCRI100/CCRI250: weighted `k100,250 = 0.95093210 ± 0.00401972`, `z_vs_pub = -0.651`, rep consistency `z = -0.137`.

## Основная цель

Для качества пучка `Q`:

`R_Q = (D_w / D_cav)_Q`

`k_Q,Co = R_Q / R_Co`

Индивидуальный calibration anchor:

`N_D,w(Co-60) = 5.389e7 Gy/C`

для камеры PTW 30013 SN 013488.

В проекте отдельно рассматриваются:

1. отклик камеры в зависимости от качества пучка;
2. влияние `field / SSD / applicator` через `k_g`;
3. поправка `RW3-to-water`;
4. прямые `end-to-end` проверки в реальной геометрии RW3.

## Авторитетная исходная база TERAD

| Beam | Напряжение | Ток | Измеренный HVL1 | Добавочный клинический фильтр |
|---|---:|---:|---:|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu |

Основные исходные файлы:

- `docs/CANONICAL_MC_TASK.md`
- `docs/TERAD_INPUT_BASELINE.md`
- `data/terad_input_baseline.csv`
- `data/beam_qualities.csv`
- `data/terad_clinical_geometries.csv`

Временная ветка Stage 1R с HVL `0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu` признана неверной и не относится к production MC.

## 12 реальных клинических геометрий TERAD

Для каждого качества Q120/Q140/Q150/Q200 рассчитываются все три аппликатора:

- F40 / SSD 40 cm / 6 × 8 cm²;
- F40 / SSD 40 cm / 4 × 15 cm²;
- F50 / SSD 50 cm / 8 × 10 cm².

Итого: **12 комбинаций kV/applicator**.

F50 является полноценной клинической конфигурацией и рассчитывается так же, как оба F40. Только после собственного расчёта F50 может дополнительно использоваться как normalization denominator для представления относительных `k_g`.

## Реальная геометрия RW3

- RW3: 30 × 30 cm²;
- PTW 30013 расположена горизонтально;
- ось камеры перпендикулярна central axis;
- geometric centre / reference point находится на central axis;
- stem направлен вправо;
- центр камеры находится на глубине 2.0 cm water-equivalent;
- физически над корпусом камеры в заданной установке находится 1.3 cm RW3;
- downstream запас RW3 — приблизительно 10 cm;
- боковой запас — не менее 10 cm;
- SSD задаётся аппликатором F40/F50;
- аппликатор прижат к поверхности RW3.

Все 12 конфигураций должны получить прямой MC-расчёт в RW3 в дополнение к раздельным расчётам water / geometry / RW3.

## Stage 0 — EGSnrc / egs_chamber ✅

Закреплённый commit официального NRC EGSnrc:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Принятая transport/VRT архитектура включает low-energy photon transport, Radiative Compton, exact BCA, IPSS/TmpPhsp, XCSE 64 и Russian Roulette survival 1/64.

## Stage 1 — production spectra TERAD ✅ принят первый вариант

Первичная модель спектров TERAD:

- SpekPy 2.5.4;
- W reflection target;
- nominal anode angle 20°;
- `kqp` physics;
- известные клинические фильтры;
- неотрицательная equivalent-Al nuisance filtration.

| Beam | Target HVL1 | Final HVL1 | Ошибка |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Результат: `results/spekpy_fit_summary.csv`.

## Stage 2 — PTW 30013 Model A ❌ benchmark не пройден

Model A — упрощённая public/aggregate surrogate геометрия:

- air-cavity radius = 3.05 mm;
- effective internal cavity length = 21.80 mm;
- Al central-electrode radius = 0.575 mm;
- retained electrode length = 21.20 mm;
- graphite = 0.09 mm;
- PMMA = 0.335 mm.

Model A не воспроизводит реальную proprietary геометрию tip, guard, insulator, electrode base и stem transition.

## Stage 3 — опубликованный benchmark PTW 30013

Опубликованные midpoint targets:

- `k100,250 = 0.95355`;
- `k135,250 = 0.97460`;
- `k180,250 = 0.98565`;
- `k250,250 = 1`.

Определение: `R_Q = D_w / D_cav`.

### Stage 3G — high-stat `kqp` / Model A ❌

Run `34572944985`:

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.928161 | 0.005668 | -2.663% |
| repB | 0.927563 | 0.005660 | -2.725% |
| weighted | **0.927861** | **0.004005** | **-2.694%** |

Две независимые реплики по 300M/beam согласовались между собой, но weighted result отличался от опубликованного target примерно на 6.4 sigma. Увеличивать histories для той же Model A нецелесообразно.

### Stage 3H-0 — spectrum fidelity ✅

Результат: `results/stage3h0_spectrum_fidelity.csv`.

`spekcalc` выбран как основной benchmark spectrum surrogate, поскольку лучше остальных вариантов одновременно воспроизводит опубликованные Cu HVL и kerma-weighted mean energy для CCRI100/135/180/250.

### Stage 3H-1 — paper-faithful SpekCalc + air48 / Model A ❌

Run `34580291967`:

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.932799 | 0.006960 | -2.176% |
| repB | 0.923246 | 0.006891 | -3.178% |
| weighted | **0.92797486** | **0.00489702** | **-2.6821%** |

Реплики согласовались (`z = +0.975`). Более точное воспроизведение spectrum/air geometry не устранило систематическое расхождение Model A.

Результат: `results/stage3h1_summary.csv`.

### Stage 3H-2 — Model B0: public sensitive length 🟠

Run `34597238397`.

Единственное физически подтверждённое изменение относительно Model A:

- sensitive length: **21.8 mm → 23.0 mm**.

Axial length центрального электрода 21.2 mm пока сохраняется только как legacy computational assumption и не трактуется как manufacturer dimension.

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.931782 | 0.006809 | -2.283% |
| repB | 0.945731 | 0.006890 | -0.820% |
| weighted | **0.93867384** | **0.00484302** | **-1.560%** |

Реплики приемлемо согласуются (`z = -1.440`). B0 сдвинул результат относительно Stage 3H-1 на **+1.1529%**, но benchmark ещё не принят.

Результат: `results/stage3h2_summary.csv`.

Документация: `docs/STAGE3H2_MODEL_B0.md`.

### Stage 3H-3B — Model B1 tip sensitivity ✅ screening завершён

Рабочий исправленный run: `34695545832`, `completed / success`.

B1 сохраняет sensitive volume Model B0 с length 23.0 mm и добавляет асимметричный PMMA tip surrogate со стороны физического tip камеры.

Публичные ограничения:

- sensitive length = 23.0 mm;
- reference point = 13.0 mm от tip камеры.

Отсюда nominal расстояние:

`13.0 - 23.0/2 = 1.5 mm`.

Заранее заданное семейство:

| case | PMMA tip surrogate | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|---:|
| tip1p0 repA | 1.0 mm | 0.94075957 | 0.00890119 | -1.3413% |
| tip1p5 repA | **1.5 mm** | 0.96239264 | 0.00910852 | +0.9273% |
| tip1p5 repB | **1.5 mm** | 0.92863760 | 0.00877824 | -2.6126% |
| tip1p5 weighted | **1.5 mm** | **0.94489204** | **0.00632069** | **-0.9080%** |
| tip2p0 repA | 2.0 mm | 0.92910553 | 0.00879336 | -2.5635% |

Результат: `results/stage3h3b_summary.csv`.

Nominal 1.5 mm был выбран до получения MC-результатов и не подбирался по target. Screening nominal-реплики разошлись на `z = +2.668`, поэтому понадобилось независимое high-stat подтверждение.

### Stage 3H-4 — nominal Model B1 high-stat confirmation ✅ endpoint benchmark пройден

Run `34696899052`, `completed / success`.

Фиксированная nominal Model B1:

- sensitive length = 23.0 mm;
- PMMA tip surrogate = **1.5 mm**;
- SpekCalc benchmark spectrum;
- paper-faithful air48;
- corrected EGS_ConeStack region topology;
- две независимые реплики;
- 300M histories/beam для CCRI100 и CCRI250.

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.95038353 | 0.00568178 | -0.3321% |
| repB | 0.95148181 | 0.00568772 | -0.2169% |
| weighted | **0.95093210** | **0.00401972** | **-0.2745%** |

High-stat реплики согласуются: `z_rep = -0.137`.

Weighted result совместим с опубликованным midpoint: `z_vs_pub = -0.651`.

Следовательно, endpoint CCRI100/250 benchmark для nominal B1 **пройден**. Результат сохранён в `results/stage3h4_summary.csv`.

Однако камера ещё не считается окончательно принятой: по заранее объявленной схеме требуется независимая проверка CCRI135 и CCRI180 без изменения геометрии.

### Stage 3H-5 — CCRI135/CCRI180 intermediate validation 🟡 выполняется

Workflow:

`.github/workflows/stage3h5-intermediate-validation.yml`

Run:

**`34820082073`**

Commit запуска:

`4aaa377971c54af038133eef9041db52eea6ae1b`

Расчётный дизайн:

- фиксированная nominal Model B1 из Stage 3H-4;
- repA: CCRI135 + CCRI180 + CCRI250;
- repB: CCRI135 + CCRI180 + CCRI250;
- 300M histories на каждый beam;
- всего 6 MC jobs;
- у каждой реплики собственный CCRI250 denominator.

Targets:

- `k135,250 = 0.97460`;
- `k180,250 = 0.98565`.

Заранее определённый gate:

1. `|z_rep| <= 2` для CCRI135;
2. `|z_rep| <= 2` для CCRI180;
3. `|z_vs_pub| <= 2` для weighted CCRI135;
4. `|z_vs_pub| <= 2` для weighted CCRI180;
5. сохраняется порядок `k135,250 < k180,250 < 1`.

Если gate проходит, nominal Model B1 считается benchmark-validated и проект переходит к Co-60 и TERAD production calculations. Если нет — следующий заранее объявленный этап: guard/insulator sensitivity, затем stem-transition sensitivity.

Документация: `docs/STAGE3H5_INTERMEDIATE_VALIDATION.md`.

См. также:

- `docs/PTW30013_MODEL_B_PUBLIC_PLAN.md`
- `data/ptw30013_modelB_public_constraints.csv`
- `scripts/build_stage3h4_b1_nominal.py`

## Текущий статус проекта

| Stage | Содержание | Статус |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ завершено |
| 1 | production spectra TERAD | ✅ принят первый вариант |
| 2 | PTW 30013 Model A | ❌ benchmark не пройден |
| 3G | high-stat `kqp` / Model A | ❌ systematic fail |
| 3H-0 | spectrum fidelity | ✅ завершено; выбран SpekCalc |
| 3H-1 | SpekCalc + air48 / Model A | ❌ systematic fail |
| 3H-2 | Model B0 public sensitive length | 🟠 улучшение; не принят |
| 3H-3B | Model B1 tip sensitivity screening | ✅ завершено |
| 3H-4 | nominal Model B1 endpoint high-stat validation | ✅ CCRI100/250 пройден |
| 3H-5 | CCRI135/180 intermediate validation | 🟡 выполняется |
| 4 | Co-60 reference ratio | ⏸ до полного принятия benchmark |
| 5 | water calculations для всех 12 TERAD configurations | ⏸ до полного принятия benchmark |
| 6 | TERAD spectrum/chamber sensitivity | ожидает выполнения |
| 7 | geometry-response ratios `k_g` | ожидает выполнения |
| 8 | RW3-to-water + 12 direct RW3 end-to-end | ожидает выполнения |
| 9 | итоговые коэффициенты и uncertainty budget | ожидает выполнения |

## Правила интерпретации benchmark

- measured HVL TERAD не меняются ради улучшения fit;
- geometry PTW30013 не подгоняется к опубликованным benchmark values;
- один HVL не определяет спектр однозначно — spectrum ambiguity учитывается отдельно;
- Stage 3 служит валидацией методики, а не источником TERAD input data;
- F50 не является `reference-only` — это полноценная клиническая конфигурация;
- RW3 рассматривается отдельно от water-response и дополнительно проверяется direct end-to-end MC.

## Путь к production calculations после принятия benchmark

1. рассчитать `R_Co` в Co-60 certificate reference geometry;
2. рассчитать water `R_Q` для всех **12** комбинаций TERAD kVp/applicator;
3. определить chamber-specific `k_Q,Co` для всех трёх аппликаторов;
4. определить `k_g` только как относительное представление уже рассчитанных абсолютных откликов;
5. оценить TERAD spectrum/chamber-model sensitivity;
6. смоделировать matched RW3 geometry для всех 12 конфигураций;
7. определить RW3-to-water effect;
8. выполнить direct end-to-end RW3 MC для всех 12 конфигураций;
9. объединить итоговые коэффициенты и uncertainty budget.
