# Stage 3H-5 — независимая проверка промежуточных качеств CCRI135 и CCRI180

## Цель

После успешного high-stat endpoint benchmark Stage 3H-4 проверить, что заранее определённая nominal Model B1 воспроизводит не только отношение CCRI100/CCRI250, но и форму зависимости отклика камеры в промежуточной области качества пучка.

Геометрия камеры, transport parameters, spectrum surrogate и air geometry не изменялись относительно Stage 3H-4.

## Фиксированная Model B1

- sensitive radius: 3.05 mm;
- sensitive length: 23.0 mm;
- nominal PMMA tip surrogate: 1.5 mm;
- reference-point relation: 13.0 mm from physical tip;
- cavity mass: `7.832972283369083e-04 g`;
- SpekCalc benchmark spectra;
- explicit additional air transport: 48 cm;
- XCSE = 64;
- Russian Roulette survival = 1/64;
- pinned EGSnrc commit `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`.

Никакие параметры Model B1 по результатам Stage 3H-5 не изменялись.

## Опубликованные benchmark targets

Использованы midpoint двух опубликованных PTW 30013 расчётов Czarnecki et al.:

- CCRI135/CCRI250: `(0.9754 + 0.9738)/2 = 0.97460`;
- CCRI180/CCRI250: `(0.9857 + 0.9856)/2 = 0.98565`;
- CCRI250 = 1 by normalization.

## Расчётный дизайн

Две независимые реплики, каждая содержит CCRI135, CCRI180 и CCRI250:

- repA: 300M histories на каждый beam;
- repB: 300M histories на каждый beam.

Всего 6 независимых MC jobs.

Для каждой реплики:

`k135,250 = R_135 / R_250`

`k180,250 = R_180 / R_250`

После этого вычислены inverse-variance weighted estimates для обоих качеств.

## Заранее определённый validation gate

Model B1 может перейти к Co-60 и TERAD production calculations только если одновременно выполняются:

1. repA и repB согласуются для CCRI135: `|z_rep| <= 2`;
2. repA и repB согласуются для CCRI180: `|z_rep| <= 2`;
3. weighted CCRI135 совместим с target 0.97460: `|z_vs_pub| <= 2`;
4. weighted CCRI180 совместим с target 0.98565: `|z_vs_pub| <= 2`;
5. сохраняется физически ожидаемый порядок `k135,250 < k180,250 < 1`.

`z_vs_pub` рассчитывался только с MC uncertainty проекта; опубликованная uncertainty не добавлялась.

## Фактическое выполнение

Основной run: `34820344407`.

В первой попытке `repA / CCRI180` был прерван внешним shutdown GitHub hosted runner после 25/30 batches. Это не трактовалось как физический fail. Был выполнен rerun failed jobs без изменения input, после чего все шесть физических точек и итоговый evaluation завершились `success`.

## Результаты

| Quality | Estimate | kQ,250 | u(k) | u(k), % | Target | Delta vs target | z vs target |
|---|---|---:|---:|---:|---:|---:|---:|
| CCRI135 | repA | 0.96777383 | 0.00582582 | 0.6020 | 0.97460 | -0.7004% | -1.172 |
| CCRI135 | repB | 0.97574940 | 0.00593452 | 0.6082 | 0.97460 | +0.1179% | +0.194 |
| CCRI135 | **weighted** | **0.97168791** | **0.00415738** | **0.4279** | **0.97460** | **-0.2988%** | **-0.700** |
| CCRI180 | repA | 0.98972791 | 0.00590583 | 0.5967 | 0.98565 | +0.4137% | +0.690 |
| CCRI180 | repB | 0.98572307 | 0.00594931 | 0.6035 | 0.98565 | +0.0074% | +0.012 |
| CCRI180 | **weighted** | **0.98774017** | **0.00419134** | **0.4243** | **0.98565** | **+0.2121%** | **+0.499** |

Согласие независимых реплик:

- CCRI135: `z_rep = -0.959`;
- CCRI180: `z_rep = +0.478`.

Порядок откликов:

`0 < 0.97168791 < 0.98774017 < 1`.

Итоговый gate:

`gate_pass = true`

`monotonic = true`

## Решение

**Stage 3H-5 пройден. Nominal PTW 30013 Model B1 считается benchmark-validated для дальнейших расчётов проекта.**

Guard/insulator sensitivity и stem-transition sensitivity не используются как дополнительные параметры подгонки benchmark. Они могут быть проведены позднее только как отдельная model-form sensitivity / uncertainty study.

Следующий этап: Co-60 reference ratio `R_Co = (D_w/D_cav)_Co` в референсной геометрии проекта, после чего — TERAD water calculations для всех 12 клинических конфигураций.

Постоянный результат: `results/stage3h5_summary.csv`.
