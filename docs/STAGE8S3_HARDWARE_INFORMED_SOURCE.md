# Stage 8S3 — hardware-informed модель рентгеновской трубки TERAD

## Цель

Stage 5/8 и первые sensitivity-блоки используют **идеализированную, но HVL-согласованную модель источника**. Stage 8S3 проверяет, насколько итоговый коэффициент

`K_Q,g,Co^(RW3→w)`

изменяется после явного введения известных аппаратных характеристик реальной трубки.

## Подтверждённые характеристики

- материал анода: W;
- выходное окно: Be;
- толщина Be-окна: `0.8 ± 0.1 мм`;
- диаметр фокусного пятна: `7.5 мм`;
- точность напряжения генератора: `0.25%`;
- основной клинический фильтр: Al или Cu в соответствии с `data/beam_qualities.csv`;
- фактический угол анода: неизвестен.

Угол раскрытия полезного пучка (≤30° по техническим характеристикам; около 40° в литературном описании) **не является углом анода** и не подставляется как SpekPy `th`.

## Stage 8S3a — feasibility до дорогого MC

Перед dose-transport выполняется спектральная проверка:

`W → explicit Be → known clinical Al/Cu → residual equivalent Al → measured Cu HVL`.

Residual equivalent Al допускается только `>= 0`. Если после явного Be и клинического фильтра рассчитанный спектр уже жёстче измеренного HVL, вариант помечается как **infeasible**, а отрицательная фильтрация запрещена.

Проверяемые варианты:

- Be = 0.7 / 0.8 / 0.9 мм при текущем screening angle 20°;
- kVp = nominal × (1 ± 0.0025) при Be 0.8 мм и 20°;
- model-form angle probes 10°, 15°, 20°, 25°, 30° при Be 0.8 мм и nominal kVp.

Углы 10/15/25/30° — только вычислительные probes, а не заявленные параметры TERAD и не готовые границы uncertainty distribution.

## Finite focal spot

Текущий baseline использует point source. Для source-size sensitivity вводится равномерный круглый source surrogate:

- диаметр = 7.5 мм;
- радиус = 3.75 мм = 0.375 см;
- source plane сохраняется на том же source-to-surface SSD;
- клиническая апертура и field projection не меняются.

EGSnrc `egs_collimated_source` допускает произвольную source shape; используется `egs_circle` с translation в плоскость источника.

Равномерный круг — surrogate известного диаметра, а не восстановленная proprietary intensity map focal spot.

## Переход к dose transport

Только после Stage 8S3a выбираются физически допустимые hardware-informed spectrum candidates. Для каждого transport-варианта необходимо пересчитывать **обе среды**:

1. matched water: `D_w,water/history`;
2. RW3: `D_cav,RW3/history`.

Нельзя менять только RW3 denominator и оставлять Stage 5 numerator от другого спектра.

Для каждого варианта:

`R_direct,variant = D_w,water,variant / D_cav,RW3,variant`

и

`K_variant = R_direct,variant / R_Co`.

Основная model-form comparison:

`ΔK = K_hardware-informed / K_idealized - 1`.

## Правила

- measured Cu HVL остаётся жёстким экспериментальным ограничением;
- отрицательная equivalent filtration запрещена;
- неизвестный угол анода не объявляется известным;
- 30–40° useful-beam opening не подменяет anode angle;
- finite spot Ø7.5 мм не меняет spectrum сам по себе, а проверяет source-geometry effect;
- текущие Stage 5/8 coefficients сохраняются как idealized baseline до завершения Stage 8S3.
