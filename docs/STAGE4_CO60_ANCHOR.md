# Stage 4 — Co-60 reference ratio для benchmark-validated PTW 30013 Model B1

## Цель

Получить независимый Monte Carlo denominator

`R_Co = (D_w / D_cav)_Co`

для дальнейшего расчёта chamber-specific коэффициентов

`k_Q,Co = R_Q / R_Co`.

Stage 4 начинается только после успешного Stage 3H-5. Геометрия PTW 30013 Model B1 на этом этапе фиксирована и не изменяется.

## Принятая геометрия камеры

Используется та же nominal Model B1, которая прошла CCRI100/135/180/250 benchmark:

- sensitive radius = 3.05 mm;
- sensitive length = 23.0 mm;
- nominal PMMA tip surrogate = 1.5 mm;
- public reference point = 13.0 mm from physical tip;
- retained legacy electrode axial length = 21.2 mm;
- graphite wall = 0.09 mm;
- PMMA wall = 0.335 mm;
- central electrode diameter = 1.15 mm;
- net cavity air volume = 0.650147101873 cm3;
- cavity air mass = `7.832972283369083e-04 g`.

Неизвестные proprietary детали guard/insulator/stem не подгоняются по Co-60 результату.

## Co-60 reference geometry проекта

Reference point камеры находится в начале координат `z=0`.

- source-to-reference distance, SDD = **100 cm**;
- water surface = `z=-5 cm`;
- chamber reference depth = **5 cm water**;
- SSD = **95 cm**;
- field at reference plane = **10 x 10 cm2**;
- water phantom = **30 x 30 x 30 cm3** downstream of the surface;
- source-to-surface 95 cm air path transported explicitly;
- chamber axis perpendicular to beam axis, as in accepted benchmark Model B1.

Поле формируется `egs_rectangle = -5 -5 5 5` в плоскости reference point.

## Co-60 spectrum

Используется двухлинейный primary photon spectrum:

- 1.173228 MeV;
- 1.332492 MeV.

Evaluated gamma intensities 99.85 and 99.9826 per 100 parent decays нормированы к вероятностям:

- 0.4996682223020668;
- 0.5003317776979331.

Источник задаётся inline как `tabulated spectrum`, `spectrum mode = 2` (line spectrum). Энергии и intensities соответствуют evaluated Co-60 decay data NNDC/ENSDF; они не являются параметром fit.

## Transport / VRT

Сохраняется проверенная архитектура `egs_chamber`:

- pinned EGSnrc commit `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`;
- XCSE = 64;
- Russian Roulette survival = 1/64;
- TmpPhsp/IPSS;
- `Global PCUT = 0.001 MeV`;
- `Global ECUT = 0.512 MeV`;
- Radiative Compton = On;
- Rayleigh = On;
- Bound Compton = On;
- exact BCA.

Pegsless upper energies расширены относительно kV benchmark, поскольку Co-60 photons имеют энергии выше 1.33 MeV:

- `UE = 2.000 MeV`;
- `UP = 1.500 MeV`.

## Расчётный дизайн

Две независимые реплики:

- repA: 300M histories, seeds 1001 / 2001;
- repB: 300M histories, seeds 1002 / 2002.

Каждая реплика напрямую вычисляет correlated ratio

`R_Co = D_w / D_cav`.

После этого рассчитывается inverse-variance weighted `R_Co`.

## Заранее объявленный gate

Stage 4 считается воспроизводимым, если:

1. обе реплики завершились физически валидно;
2. для каждой реплики `u(R_Co)/R_Co <= 1%`;
3. согласие реплик `|z_rep| <= 2`.

На этом этапе нет внешнего target для `R_Co`; значение не подгоняется под сертификат камеры.

Индивидуальный сертификатный коэффициент

`N_D,w(Co-60) = 5.389e7 Gy/C`

для PTW 30013 SN 013488 сохраняется как calibration metadata и не используется для fit `R_Co`.

## После PASS

После принятия Stage 4:

1. фиксируется weighted `R_Co`;
2. запускаются water calculations для Q120/Q140/Q150/Q200 во всех трёх реальных аппликаторах;
3. для каждой из 12 конфигураций вычисляется `R_Q`;
4. затем `k_Q,Co = R_Q/R_Co`;
5. F50 может использоваться как normalization denominator для `k_g` только после собственного абсолютного расчёта.

Workflow: `.github/workflows/stage4-co60-anchor.yml`.

Builder: `scripts/build_stage4_co60_b1.py`.
