# Stage 3H-2 — PTW 30013 Model B0 public-sensitive-length test

## Purpose

Stage 3H-1 showed that a paper-faithful SpekCalc spectrum plus explicit 48 cm air transport does not validate the simplified PTW 30013 Model A. The weighted Stage 3H-1 result was `k100,250 = 0.92797486 +/- 0.00489702`, about -2.68% from the published midpoint 0.95355.

Stage 3H-2 therefore begins Model B-public in the smallest controlled increment possible. It changes one fixed public chamber constraint only: the sensitive length is set to 23.0 mm instead of the Model A effective 21.8 mm.

## Model B0 geometry

Fixed public quantities retained:

- sensitive radius = 3.05 mm;
- sensitive length = 23.0 mm;
- graphite wall = 0.09 mm;
- PMMA wall = 0.335 mm;
- central-electrode diameter = 1.15 mm Al;
- radial incidence.

Legacy computational assumption retained for this B0 isolation test:

- central-electrode axial length = 21.2 mm.

The 21.2 mm electrode length is **not** claimed to be a PTW manufacturer dimension. It is retained only so that the effect of the one confirmed public change, 21.8 -> 23.0 mm sensitive length, can be measured independently.

With the electrode centred axially, the simple Model A end-air regions increase from 0.30 mm to 0.90 mm each. This remains a surrogate representation and is not claimed to reproduce the proprietary PTW tip/guard construction.

## Air volume and cavity mass

Using:

- cavity radius `r = 0.305 cm`;
- sensitive length `L = 2.30 cm`;
- electrode radius `re = 0.0575 cm`;
- retained legacy electrode length `Le = 2.12 cm`;

net modelled air volume is

`Vair = pi*r^2*L - pi*re^2*Le = 0.6501471018732639 cm3`.

Using the same model air density as the EGSnrc input, `rho = 1.2048e-3 g/cm3`, the cavity mass is

`mcav = 7.832972283369083e-4 g`.

Both values are checked automatically in CI before simulation.

## Benchmark conditions

Identical to Stage 3H-1 apart from Model B0 geometry:

- SpekCalc benchmark surrogate selected by Stage 3H-0;
- published filters and Emin;
- first 50 cm air represented in spectrum generation;
- additional 48 cm air explicitly transported;
- same water phantom, field and source geometry;
- same pinned EGSnrc commit and transport/VRT settings;
- CCRI100 and CCRI250;
- two independent replications;
- 200M primary histories per beam per replication.

Workflow:

`.github/workflows/stage3h2-modelB0-public-length.yml`

## Interpretation rule

Model B0 is not accepted merely if its central value moves toward 0.95355. The result is used to quantify the isolated effect of the confirmed 23.0 mm sensitive-length constraint.

If B0 does not remove the benchmark discrepancy, subsequent Model B-public stages introduce tip, guard/insulator and stem-transition families as declared sensitivity models. Unknown dimensions remain sensitivity parameters and are never labelled as manufacturer truth or selected only because they fit the benchmark.
