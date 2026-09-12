# TERAD-PTW30013-MC

Monte Carlo проект для определения chamber-specific коэффициентов коррекции по качеству пучка для ионизационной камеры PTW 30013, используемой на киловольтном рентгенотерапевтическом аппарате TERAD.

> **Каноническое ТЗ:** `docs/CANONICAL_MC_TASK.md` и `data/terad_clinical_geometries.csv` задают исходные пользовательские данные TERAD, все 12 комбинаций аппликаторов и реальную геометрию измерений в RW3. Эти данные имеют приоритет над всеми исследовательскими benchmark-ветками.

> **Текущий этап:** выполняется **Stage 3H-3 Model B1 tip sensitivity**. Stage 3H-2 Model B0 завершён успешно и показал, что замена эффективной sensitive length 21.8 mm из Model A на публичное значение PTW 23.0 mm повышает weighted CCRI100/250 benchmark примерно на 1.15%, но сама модель камеры пока ещё не валидирована.

## Основная цель

Для качества пучка Q:

`R_Q = (D_w / D_cav)_Q`

`k_Q,Co = R_Q / R_Co`

Индивидуальный calibration anchor для камеры:

`N_D,w(Co-60) = 5.389e7 Gy/C`

для PTW 30013 SN 013488.

В проекте отдельно рассматриваются:

1. отклик камеры в зависимости от качества пучка;
2. влияние field / SSD / applicator через `k_g`;
3. поправка RW3-to-water;
4. прямые end-to-end проверки в реальной геометрии RW3.

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

Временная ветка Stage 1R с HVL 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu признана неверной и не относится к production MC.

## 12 реальных клинических геометрий TERAD

Для **каждого** качества Q120/Q140/Q150/Q200 полностью рассчитываются все три аппликатора:

- F40 / SSD 40 cm / 6 × 8 cm²
- F40 / SSD 40 cm / 4 × 15 cm²
- F50 / SSD 50 cm / 8 × 10 cm²

Итоговая клиническая задача содержит **12 комбинаций kV/applicator**.

F50 является полноценной рассчитываемой клинической конфигурацией и не заменяет два F40. После собственного расчёта F50 дополнительно используется как удобный normalization denominator для относительных значений `k_g`.

## Реальная геометрия RW3

- поперечный размер RW3: 30 × 30 cm²;
- PTW 30013 расположена горизонтально;
- ось камеры перпендикулярна оси пучка;
- geometric centre / reference point камеры находится на central axis;
- stem направлен вправо;
- центр камеры находится на 2.0 cm water-equivalent depth;
- в заданной экспериментальной геометрии физически над корпусом камеры расположено 1.3 cm RW3;
- downstream запас RW3 — приблизительно 10 cm;
- боковой запас — не менее 10 cm;
- SSD задаётся аппликатором F40/F50;
- аппликатор прижат к поверхности RW3.

Все 12 конфигураций будут рассчитаны непосредственно в RW3 в дополнение к раздельному анализу water / geometry / RW3.

## Stage 0 — инфраструктура EGSnrc ✅

Закреплённый commit официального NRC EGSnrc:

`f4d029f625a6c96ef3456e0b6d91d46ffce613e7`

Принятая benchmark transport/VRT архитектура включает low-energy photon transport, Radiative Compton, exact BCA, IPSS/TmpPhsp, XCSE 64 и Russian Roulette survival 1/64.

## Stage 1 — production spectra TERAD ✅ принят первый вариант

Первичная модель спектров TERAD использует SpekPy 2.5.4, W reflection target, nominal anode angle 20°, `kqp` physics, известные клинические фильтры и неотрицательную equivalent-Al nuisance filtration.

| Beam | Target HVL1 | Final HVL1 | Ошибка |
|---|---:|---:|---:|
| Q120 | 0.224000 | 0.224000 | 0.000% |
| Q140 | 0.410000 | 0.410000 | 0.000% |
| Q150 | 0.729000 | 0.729000 | 0.000% |
| Q200 | 1.452000 | 1.452955 | +0.0658% |

Постоянно сохранённый результат: `results/spekpy_fit_summary.csv`.

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

Опубликованный midpoint для CCRI100/CCRI250:

`k100,250 = 0.95355`

при определении `R_Q = D_w / D_cav`.

### Stage 3G — high-stat `kqp` / Model A ❌

Run `34572944985`:

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.928161 | 0.005668 | -2.663% |
| repB | 0.927563 | 0.005660 | -2.725% |
| weighted | **0.927861** | **0.004005** | **-2.694%** |

Две независимые реплики по 300M/beam согласуются между собой, но weighted result отличается от опубликованного target примерно на 6.4 sigma. Увеличение числа histories для той же комбинации `kqp`/Model A нецелесообразно.

### Stage 3H-0 — spectrum fidelity ✅

Постоянно сохранённый результат: `results/stage3h0_spectrum_fidelity.csv`.

`spekcalc` выбран как основной benchmark spectrum surrogate, поскольку лучше других вариантов одновременно воспроизводит опубликованные Cu HVL и kerma-weighted mean energy для CCRI100/135/180/250.

### Stage 3H-1 — paper-faithful SpekCalc + air48 / Model A ❌

Run `34580291967` завершён успешно с двумя независимыми репликами по 200M/beam.

Постоянно сохранённый результат: `results/stage3h1_summary.csv`.

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.932799 | 0.006960 | -2.176% |
| repB | 0.923246 | 0.006891 | -3.178% |
| weighted | **0.92797486** | **0.00489702** | **-2.6821%** |

Реплики согласуются между собой (`z = +0.975`). Следовательно, более точное воспроизведение spectrum/air geometry не устраняет систематическое расхождение Model A.

### Stage 3H-2 — Model B0: публичная sensitive length 🟠 улучшение, но модель ещё не принята

Run `34597238397` завершён успешно.

Постоянно сохранённый результат: `results/stage3h2_summary.csv`.

B0 меняет только одно подтверждённое публичное геометрическое условие относительно Model A:

- sensitive length: **21.8 mm → 23.0 mm**.

Axial length центрального электрода 21.2 mm пока сохраняется только как legacy computational assumption и не трактуется как реальный manufacturer dimension.

| Оценка | k100,250 | u(k) | Отклонение от target |
|---|---:|---:|---:|
| repA | 0.931782 | 0.006809 | -2.283% |
| repB | 0.945731 | 0.006890 | -0.820% |
| weighted | **0.93867384** | **0.00484302** | **-1.560%** |

Реплики приемлемо согласуются (`z = -1.440`). Относительно Stage 3H-1 Model A переход к B0 сдвигает weighted result на **+1.1529%** и закрывает около 42% прежнего расхождения, но результат всё ещё примерно на 3.07 sigma ниже опубликованного midpoint.

Документация: `docs/STAGE3H2_MODEL_B0.md`.

### Stage 3H-3 — Model B1 tip sensitivity 🟡 выполняется

Workflow:

`.github/workflows/stage3h3-modelB1-tip-sensitivity.yml`

Run:

`34690628930`

Документация:

`docs/STAGE3H3_MODEL_B1_TIP.md`

B1 сохраняет sensitive volume Model B0 с length 23.0 mm и добавляет асимметричный PMMA tip surrogate со стороны физического tip камеры.

Публичные ограничения дают:

- sensitive length = 23.0 mm;
- reference point = 13.0 mm от tip камеры.

Отсюда независимо получается номинальное расстояние со стороны tip:

`13.0 - 23.0/2 = 1.5 mm`.

Заранее заданное семейство B1:

| case | PMMA tip surrogate | Назначение |
|---|---:|---|
| tip1p0 | 1.0 mm | нижняя граница sensitivity |
| tip1p5 | **1.5 mm** | nominal public-derived geometry |
| tip2p0 | 2.0 mm | верхняя граница sensitivity |

Номинальный вариант 1.5 mm определён до получения результатов и рассчитывается с **двумя независимыми репликами по 120M/beam**. Варианты 1.0 и 2.0 mm используются как screening bounds по 120M/beam. Ни одна tip thickness не будет выбрана только потому, что она лучше воспроизводит 0.95355.

PMMA используется лишь как first-order tip surrogate, поскольку это публично известный материал наружной стенки. Реальная rounded tip shape, axial graphite continuation, adhesive, guard и insulator остаются неизвестными и не выдаются за manufacturer truth.

Если заранее определённая nominal B1 geometry останется несовместимой с benchmark, следующие объявленные этапы — guard/insulator sensitivity и затем stem-transition sensitivity.

См. также:

- `docs/PTW30013_MODEL_B_PUBLIC_PLAN.md`
- `data/ptw30013_modelB_public_constraints.csv`

## Текущий статус проекта

| Stage | Содержание | Статус |
|---:|---|---|
| 0 | EGSnrc / egs_chamber infrastructure | ✅ завершено |
| 1 | production spectra TERAD | ✅ принят первый вариант |
| 2 | PTW 30013 Model A | ❌ benchmark не пройден |
| 3G | high-stat `kqp`/Model A benchmark | ❌ systematic fail |
| 3H-0 | spectrum fidelity | ✅ завершено; выбран SpekCalc |
| 3H-1 | paper-faithful SpekCalc + air48 / Model A | ❌ systematic fail |
| 3H-2 | Model B0 public-sensitive-length benchmark | 🟠 улучшение; не принят |
| 3H-3 | Model B1 tip sensitivity | 🟡 выполняется |
| 4 | Co-60 reference ratio | ⏸ заблокирован до принятия benchmark |
| 5 | water calculations для всех 12 TERAD configurations | ⏸ заблокирован до принятия benchmark |
| 6 | TERAD spectrum/chamber sensitivity | ожидает выполнения |
| 7 | определение geometry-response ratios `k_g` | ожидает выполнения |
| 8 | RW3-to-water + 12 direct RW3 end-to-end calculations | ожидает выполнения |
| 9 | итоговые коэффициенты и uncertainty budget | ожидает выполнения |

## Путь к production calculations после принятия benchmark

1. рассчитать `R_Co` в Co-60 certificate reference geometry;
2. рассчитать water `R_Q` для всех **12** комбинаций TERAD kVp/applicator;
3. определить chamber-specific `k_Q,Co`, сохранив явные абсолютные результаты для всех трёх аппликаторов;
4. рассчитать относительные geometry-response ratios `k_g` только как способ представления уже рассчитанных абсолютных откликов;
5. оценить TERAD spectrum/chamber-model sensitivity;
6. смоделировать matched RW3 geometry для всех 12 конфигураций;
7. определить RW3-to-water effect;
8. выполнить direct end-to-end RW3 MC для всех 12 конфигураций;
9. объединить итоговые коэффициенты и uncertainty budget.
