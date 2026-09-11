# Stage 3H — benchmark refinement after Stage 3G

## Motivation

Stage 3G demonstrated that the simplified PTW 30013 Model A with the Stage 3F/3G `kqp` spectrum family does not reproduce the published CCRI100/CCRI250 benchmark at high statistics:

- repA: k100,250 = 0.928161;
- repB: k100,250 = 0.927563;
- Stage 3G weighted: 0.927861 +/- 0.004005;
- published midpoint: 0.95355.

The independent replicates agree (z approximately 0.075), so the discrepancy is systematic rather than Monte Carlo noise.

Before modifying the chamber model, Stage 3H separates two possible systematic sources:

1. fidelity of the surrogate benchmark spectrum to the published SpekCalc beam;
2. fidelity of the public simplified PTW 30013 chamber geometry.

No chamber or spectrum parameter is tuned solely to force agreement with 0.95355.

## Stage 3H-0 — spectrum fidelity

The Czarnecki beam table supplies two independent descriptors for each benchmark quality:

- Cu HVL;
- kerma-weighted mean photon energy.

Stage 3H-0 therefore compares `kqp`, `spekcalc` and `spekpy-v1` surrogates against both observables, using the published filtration, published Emin, W target, 30 degree anode angle and the first 50 cm of air in the spectrum calculation.

Persistent results: `results/stage3h0_spectrum_fidelity.csv`.

### Main result

`spekcalc` is the most faithful overall surrogate of the published benchmark beams.

| Beam | Spekcalc HVL error | Spekcalc kerma-mean-energy error | kqp HVL error | kqp kerma-mean-energy error |
|---|---:|---:|---:|---:|
| CCRI100 | +0.9281% | -0.0746% | +0.9398% | -0.5878% |
| CCRI135 | -0.7489% | +0.2641% | -3.1364% | -1.4192% |
| CCRI180 | -1.4312% | +0.2278% | -5.8375% | -2.4517% |
| CCRI250 | -1.7928% | -0.0170% | -7.0803% | -3.6420% |

The `kqp` surrogate used by Stage 3G is particularly poor for CCRI250 and therefore cannot be treated as the paper-faithful benchmark spectrum. The accidental 50M Stage 3F central value near the published kQ target is not sufficient evidence for spectrum validity.

### Decision

For the next benchmark step, `spekcalc` is the primary spectrum surrogate. `kqp` and `spekpy-v1` remain diagnostic alternatives only.

## Stage 3H-1 — paper-faithful SpekCalc / Model A test

Stage 3H-1 holds the chamber at unchanged Model A and corrects the benchmark-side methodology first:

- `spekcalc` spectrum family;
- W target, 30 degrees;
- published filters and Emin;
- first 50 cm air included in the spectrum generation, as in the paper;
- additional 48 cm air explicitly transported between the spectrum plane and the water surface;
- CCRI100 and CCRI250;
- independent high-stat replications;
- pinned EGSnrc and the accepted Stage 3 VRT/transport settings.

This test answers a narrow question: after using the best available paper-faithful spectrum surrogate and the paper air geometry, does Model A still fail the benchmark?

If yes, the dominant remaining hypothesis becomes chamber geometry, and Stage 3H-2 will introduce a public-constraint Model B / geometry-sensitivity model without claiming proprietary manufacturer dimensions.

## Model B policy

Published benchmark studies used detailed manufacturer construction drawings for PTW 30013. This repository does not possess those proprietary drawings. Therefore any Model B built from public information must be labelled **Model B-public** and must distinguish:

- directly documented dimensions/materials;
- aggregate constraints;
- sensitivity-only surrogate dimensions for tip, guard, insulator and stem details.

Unknown internal dimensions will not be presented as manufacturer truth and will not be fitted merely to reproduce the benchmark target.
