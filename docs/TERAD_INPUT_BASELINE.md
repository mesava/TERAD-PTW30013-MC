# TERAD production input baseline

This document is the authoritative source of truth for TERAD production calculations in this repository.

It is intentionally separated from the Czarnecki published-benchmark inputs. Stage 3 CCRI100/135/180/250 beams exist only to validate the PTW 30013 Monte Carlo model and must never overwrite or redefine the clinical TERAD beam settings below.

## Authoritative TERAD beam set

The HVL values below are the user-supplied measured beam-quality values to be used as MC input constraints.

| Beam | Tube voltage | Tube current | Authoritative measured HVL1 (Cu) | Known added filtration | Clinical applicators |
|---|---:|---:|---:|---|---|
| Q120 | 120 kV | 10 mA | **0.224 mm Cu** | 4.0 mm Al | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q140 | 140 kV | 10 mA | **0.410 mm Cu** | 0.2 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q150 | 150 kV | 10 mA | **0.729 mm Cu** | 0.5 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q200 | 200 kV | 7 mA | **1.452 mm Cu** | 1.0 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |

Machine-readable copies:

- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

## What HVL means for Monte Carlo

For production MC, the measured HVL is a beam-quality constraint on the incident photon spectrum. The absorber thicknesses historically used to determine the HVL are part of the measurement procedure and are not required by the MC source model once the measured HVL itself is accepted.

HVL alone does not uniquely determine the full photon spectrum. Stage 1 therefore constructs a physically plausible spectrum/family consistent with:

- nominal tube voltage;
- tungsten target / TERAD tube information;
- known clinical removable filter;
- measured HVL;
- additional independent beam-quality observables if available later.

Residual same-HVL spectral ambiguity is treated as spectrum-model uncertainty and propagated to `D_w/D_cav` and `k_Q,Co`.

## Production reference geometry

The first intrinsic TERAD `k_Q` calculation uses:

- water phantom;
- F50 applicator;
- 8 x 10 cm2 field at phantom surface;
- SSD = 50 cm;
- PTW 30013 reference point at 2 cm depth in water;
- chamber axis perpendicular to the beam axis.

F40 6 x 8 cm2 and F40 4 x 15 cm2 are retained for the separate `k_g` field/SSD/applicator study.

## Stage 1R correction note

A temporary Stage 1R branch used the unrelated values 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu after they were mistakenly promoted from another calculation context. Those values are **not** the TERAD MC baseline and must not be used for this project.

Consequently, Stage 1R runs `34566147632`, `34566631576`, and `34566781628` are retained only as superseded diagnostics of the wrong input set. Their physical conclusions must not be used to select the TERAD production spectrum.

The correct Stage 1 work resumes from the authoritative values 0.224 / 0.410 / 0.729 / 1.452 mm Cu above.

## Acceptance rule before production spectrum use

For each Q120/Q140/Q150/Q200 beam, Stage 1 must produce an accepted spectrum or bounded spectrum family that:

1. preserves the authoritative nominal kVp and known clinical filter;
2. reproduces the authoritative measured HVL within numerical tolerance;
3. is physically plausible and transparently documents any nuisance spectral parameter;
4. quantifies residual same-HVL spectrum-shape sensitivity in `D_w/D_cav` and ultimately `k_Q,Co`.

## Change-control rule

Any future change to TERAD voltage, current, measured HVL, clinical filter or applicator information must first update this document and both machine-readable baseline files. Downstream production spectra and final coefficients must then be regenerated.
