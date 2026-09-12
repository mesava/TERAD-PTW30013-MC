# Stage 3H-3 — Model B1 tip sensitivity family

## Purpose

Stage 3H-2 Model B0 replaced the Model A effective sensitive length (21.8 mm) with the public PTW 30013 sensitive length of 23.0 mm and improved the weighted CCRI100/250 benchmark from 0.927975 to 0.938674, but the published midpoint 0.95355 was still not reproduced.

Stage 3H-3 therefore introduces the first explicitly asymmetric chamber-end feature: a simple tip surrogate on the tip side of the sensitive volume.

This is a sensitivity model, not a claim to reproduce proprietary PTW drawings.

## Independent geometric anchor

Public PTW specifications used by this repository provide:

- sensitive length = 23.0 mm;
- reference point = 13.0 mm from the chamber tip.

If the sensitive volume is centered on the reference point, the distance from the tip to the nearest edge of the 23.0 mm sensitive length is

`13.0 - 23.0/2 = 1.5 mm`.

This 1.5 mm value is therefore used as the predeclared nominal B1 tip extent. It is a derived public-geometry constraint, not a fitted benchmark parameter.

## B1 geometry family

The B0 sensitive cavity is kept unchanged:

- radius 3.05 mm;
- total sensitive length 23.0 mm;
- public graphite and PMMA radial wall thicknesses;
- B0 cavity mass unchanged;
- legacy 21.2 mm electrode axial length retained only as an explicit computational assumption.

Immediately outside the tip-side edge of the sensitive volume, B1 inserts a cylindrical PMMA tip surrogate with outer chamber radius 3.475 mm. The outer annulus remains water so the local XCSE envelope size is unchanged.

Predeclared family:

| case | tip surrogate thickness | role |
|---|---:|---|
| tip1p0 | 1.0 mm | lower sensitivity bound |
| tip1p5 | 1.5 mm | nominal public-derived geometry |
| tip2p0 | 2.0 mm | upper sensitivity bound |

The ±0.5 mm bounds are sensitivity limits around the independently derived 1.5 mm nominal value. They are not manufacturer dimensions.

## Material policy

PMMA is used as the first-order axial tip surrogate because PMMA is the public outer-wall material of the PTW 30013. The true tip shape, any axial graphite continuation, adhesive, guard and insulator details are not established by the public specification and are not asserted here.

Those effects remain for later controlled families if needed.

## Benchmark design

All beam/source conditions remain identical to Stage 3H-1/H-2:

- SpekCalc benchmark surrogate;
- published filters and Emin;
- first 50 cm air folded into the spectrum;
- 48 cm air transported explicitly;
- Czarnecki water phantom and field;
- pinned EGSnrc transport/VRT settings.

Statistics:

- tip1p0: one 120M/beam screening replicate;
- tip1p5: two independent 120M/beam replicates;
- tip2p0: one 120M/beam screening replicate.

The nominal 1.5 mm geometry is predeclared before results and is not selected based on agreement with 0.95355.

## Interpretation rule

The family is used to measure the magnitude and direction of tip sensitivity relative to B0. A result close to the published benchmark does not by itself validate the geometry.

If the independently defined nominal tip1p5 model remains discrepant, the project proceeds to guard/insulator and then stem-transition sensitivity without retuning the tip thickness to force the benchmark.
