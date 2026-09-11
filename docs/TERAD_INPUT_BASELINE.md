# TERAD production input baseline

This document is the authoritative source of truth for TERAD production calculations in this repository.

It is intentionally separated from the Czarnecki published-benchmark inputs. Stage 3 CCRI100/135/180/250 beams exist only to validate the PTW 30013 Monte Carlo model and must never overwrite or redefine the clinical TERAD beam settings below.

## Authoritative TERAD beam set

The HVL values below are user-supplied measured beam-quality values and are accepted directly as MC input constraints. The absorber thicknesses used historically to derive those HVLs are **not required for Monte Carlo once the measured HVL itself is accepted**.

| Beam | Tube voltage | Tube current | Authoritative measured HVL1 (Cu) | Known added filtration | Clinical applicators |
|---|---:|---:|---:|---|---|
| Q120 | 120 kV | 10 mA | **0.12198 mm Cu** | 4.0 mm Al | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q140 | 140 kV | 10 mA | **0.22715 mm Cu** | 0.2 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q150 | 150 kV | 10 mA | **0.77398 mm Cu** | 0.5 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q200 | 200 kV | 7 mA | **1.11223 mm Cu** | 1.0 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |

Machine-readable copy: `data/terad_input_baseline.csv`.

## What HVL means for Stage 1 Monte Carlo

For production MC, HVL is used as a measured beam-quality constraint on the incident photon spectrum. The historical absorber pair `(x1,x2)` used to calculate the HVL is part of the measurement procedure, not part of the MC source model.

Therefore Stage 1 must reproduce the accepted HVL values above; it must not reopen or reinterpret them from unrelated spreadsheet versions.

HVL alone does **not** uniquely determine the complete photon spectrum. Stage 1 must therefore construct a physically plausible spectrum family consistent with:

- nominal tube voltage;
- tungsten target / TERAD tube information;
- known clinical removable filter;
- measured HVL;
- any additional independent beam-quality observables available later (for example second HVL / homogeneity coefficient, measured depth-dose information, or other spectral constraints).

Residual ambiguity between spectra sharing the same HVL is treated as a spectrum-model uncertainty, not as uncertainty in the supplied HVL.

## Production reference geometry

The first intrinsic TERAD `k_Q` calculation uses one real clinical geometry as the reference condition:

- water phantom;
- F50 applicator;
- 8 x 10 cm2 field at the phantom surface;
- SSD = 50 cm;
- PTW 30013 reference point at 2 cm depth in water;
- chamber axis perpendicular to the beam axis.

The F40 6 x 8 cm2 and F40 4 x 15 cm2 applicators are preserved for the separate field/SSD/applicator correction study `k_g`, so that intrinsic chamber beam-quality correction and applicator geometry effects are not mixed.

## Separation from the Stage 3 benchmark

The published CCRI100/135/180/250 spectra, filters and geometries belong exclusively to validation of the PTW 30013 / MC methodology. They are not TERAD beam substitutes.

## Stage 1R findings so far

The previous one-parameter model family (SpekPy spectrum + known clinical filter + only non-negative equivalent-Al adjustment) cannot represent Q120, Q140 and Q200 because those nominal SpekPy spectra are already harder than the accepted measured HVLs. This does **not** invalidate the measured HVLs. It invalidates that restricted spectrum-model family for these TERAD beams.

Stage 1R therefore proceeds by broadening the source-spectrum model rather than changing the measured HVLs.

Completed diagnostics:

- Stage 1R-1: spectrum-engine / anode-angle feasibility map;
- Stage 1R-2: W-target / Be-window tube-informed check;
- Stage 1R-3: effective-kVp diagnostic showing that a simple common voltage shift is not an adequate explanation.

These diagnostics are retained as model-selection evidence only.

## Acceptance rule before production spectrum use

For each Q120/Q140/Q150/Q200 beam, Stage 1 must produce at least one accepted spectrum (and preferably a bounded spectrum family) that:

1. preserves the authoritative nominal kVp and known clinical filter;
2. reproduces the authoritative measured HVL within the chosen numerical tolerance;
3. does not rely on interpreting unrelated historical spreadsheet absorber stacks;
4. is physically plausible and transparently documents any empirical spectral-shape correction;
5. quantifies the effect of residual same-HVL spectral ambiguity on `D_w/D_cav` and ultimately on `k_Q,Co`.

## Change-control rule

Any future change to TERAD voltage, current, measured HVL, clinical filter or applicator information must first update this document and `data/terad_input_baseline.csv`. Downstream Stage 1 production spectra and final coefficients must then be regenerated.
