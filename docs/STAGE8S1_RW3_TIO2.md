# Stage 8S1 — RW3 TiO2 composition sensitivity

## Purpose

Quantify the contribution of the PTW-specified RW3 TiO2 composition tolerance to the final direct RW3→water coefficient without retuning any accepted production input.

## Fixed quantities

The following remain exactly as in accepted Stage 8 production:

- PTW 30013 Model B1;
- 2.0 cm physical chamber-centre depth;
- F50 SSD = 50 cm and 8×10 cm² surface field;
- accepted TERAD spectra;
- RW3 density = 1.045 g/cm³;
- EGSnrc transport and variance-reduction settings;
- Stage 4 Co-60 denominator `R_Co = 1.12016676`.

Density is intentionally held fixed so this screen isolates composition sensitivity rather than mixing composition and density effects.

## Perturbation

PTW nominal RW3 composition is polystyrene `(C8H8)` with `2.0 ± 0.4 percentage points` TiO2 by mass.

Endpoints:

- low = 1.6% TiO2;
- nominal = 2.0% TiO2 (accepted Stage 8 model);
- high = 2.4% TiO2.

Elemental H/C/O/Ti fractions for the perturbed endpoints are generated from stoichiometric polystyrene and TiO2 atomic masses; they are not independently fitted.

## Screening design

The first screen uses F50 8×10 for all four beam qualities:

- Q120;
- Q140;
- Q150;
- Q200.

Each low/high endpoint is calculated with 300M histories and 30 batches. The corresponding Stage 8 F50 seed pair is reused for low and high endpoints to reduce irrelevant random-history differences.

Total new production points: 8.

## Outputs

For each quality the evaluator reports:

- accepted nominal Stage 8 F50 coefficient;
- low-endpoint coefficient;
- high-endpoint coefficient;
- relative endpoint shifts from nominal;
- low-to-high endpoint span;
- maximum absolute endpoint shift;
- preliminary standard material contribution assuming the PTW tolerance is a rectangular bound: `u_rect = max endpoint shift / sqrt(3)`;
- conservative span significance using endpoint MC uncertainties.

The first screen is not a clinical acceptance pass/fail test. Its technical gate is only `u(D_cav,RW3) <= 1%` for every endpoint.

If the composition effect is non-negligible relative to the target uncertainty budget, the TiO2 perturbation will be expanded from F50 to all 12 clinical geometries before Stage 9 final uncertainty aggregation.

Workflow: `.github/workflows/stage8s1-rw3-tio2-sensitivity.yml`.
