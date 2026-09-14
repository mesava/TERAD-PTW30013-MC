# Stage 3H-5 — независимая проверка промежуточных качеств CCRI135 и CCRI180

## Цель

После успешного high-stat endpoint benchmark Stage 3H-4 проверить, что заранее определённая nominal Model B1 воспроизводит не только отношение CCRI100/CCRI250, но и форму зависимости отклика камеры в промежуточной области качества пучка.

Геометрия камеры, transport parameters, spectrum surrogate и air geometry не изменяются относительно Stage 3H-4.

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

Никакие параметры Model B1 не могут изменяться по результатам Stage 3H-5.

## Опубликованные benchmark targets

Используются midpoint двух опубликованных PTW 30013 расчётов Czarnecki et al.:

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

После этого вычисляются inverse-variance weighted estimates для обоих качеств.

## Заранее определённый validation gate

Model B1 может перейти к Co-60 и TERAD production calculations только если одновременно выполняются:

1. repA и repB согласуются для CCRI135: `|z_rep| <= 2`;
2. repA и repB согласуются для CCRI180: `|z_rep| <= 2`;
3. weighted CCRI135 совместим с target 0.97460: `|z_vs_pub| <= 2`;
4. weighted CCRI180 совместим с target 0.98565: `|z_vs_pub| <= 2`;
5. сохраняется физически ожидаемый порядок `k135,250 < k180,250 < 1`.

`z_vs_pub` на этом этапе рассчитывается только с MC uncertainty проекта; опубликованная uncertainty не добавляется, поэтому критерий не искусственно ослабляется.

Если gate не проходит, следующий заранее объявленный этап — guard/insulator sensitivity Model B-public. Геометрия tip не подгоняется повторно.
