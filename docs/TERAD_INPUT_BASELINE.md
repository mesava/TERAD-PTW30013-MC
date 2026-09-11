# TERAD production input baseline

This document is the authoritative source of truth for TERAD production calculations in this repository.

It is intentionally separated from the Czarnecki published-benchmark inputs. Stage 3 CCRI100/135/180/250 beams exist only to validate the PTW 30013 Monte Carlo model and must never overwrite or redefine the clinical TERAD beam qualities below.

## Authoritative TERAD beam set

| Beam | Tube voltage | Tube current | Measured HVL1 (Cu) | Known added filtration | Clinical applicators represented in the source spreadsheet |
|---|---:|---:|---:|---|---|
| Q120 | 120 kV | 10 mA | 0.12198 mm Cu | 4.0 mm Al | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q140 | 140 kV | 10 mA | 0.22715 mm Cu | 0.2 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q150 | 150 kV | 10 mA | 0.77398 mm Cu | 0.5 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q200 | 200 kV | 7 mA | 1.11223 mm Cu | 1.0 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |

Machine-readable copy: `data/terad_input_baseline.csv`.

## Production reference geometry

The first intrinsic TERAD `k_Q` calculation uses one real clinical geometry as the reference condition:

- water phantom;
- F50 applicator;
- 8 x 10 cm2 field at the phantom surface;
- SSD = 50 cm;
- PTW 30013 reference point at 2 cm depth in water;
- chamber axis perpendicular to the beam axis.

The F40 6 x 8 cm2 and F40 4 x 15 cm2 applicators are not discarded. They are reserved for the separate field/SSD/applicator correction study `k_g`, so that intrinsic chamber beam-quality correction and applicator geometry effects are not mixed.

## Separation from the Stage 3 benchmark

The published CCRI100/135/180/250 spectra, filters and geometries belong exclusively to the validation problem:

`PTW 30013 Model -> published k_Q benchmark`.

They are not TERAD beam substitutes and must not be used as clinical TERAD input data.

Once Stage 3 is accepted, production work returns to the four TERAD beams listed above.

## Stage 1 spectrum-model status after baseline correction

The earlier Stage 1 spectra were fitted to an older HVL set:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

Those values are now superseded for production calculations by this baseline and must not be used for final TERAD `k_Q,Co` results.

The original Stage 1 model used SpekPy 2.5.4 with a W target, nominal 20 degree anode angle, `kqp` physics, the known added filter and then fitted only a non-negative equivalent-Al nuisance thickness.

### Automatic feasibility diagnostic

The corrected baseline was tested by `scripts/diagnose_terad_stage1_baseline.py` in GitHub Actions run `34564537373`.

| Beam | Measured HVL (mm Cu) | Legacy known-filter-only HVL (mm Cu) | Difference vs measured | Legacy positive-Al fit |
|---|---:|---:|---:|---|
| Q120 | 0.121980 | 0.207172 | +69.84% | impossible: model already too hard |
| Q140 | 0.227150 | 0.388502 | +71.03% | impossible: model already too hard |
| Q150 | 0.773980 | 0.723665 | -6.50% | possible in principle |
| Q200 | 1.112230 | 1.452955 | +30.63% | impossible: model already too hard |

Thus Q120, Q140 and Q200 cannot be represented by the old one-parameter positive-equivalent-Al family. Adding positive Al can only increase HVL further. Q150 remains representable within that family, but the production model must be rebuilt consistently for all four beams rather than accepting a mixed ad hoc solution.

This is a model-family mismatch, not a reason to alter the measured HVL values.

The previous automatic `TERAD SpekPy spectra` workflow has therefore been retired to manual legacy/audit use. The authoritative automatic gate is now `TERAD Stage 1 baseline diagnostic`.

## Required Stage 1 rebuild

Before any production TERAD `k_Q,Co` calculation, the spectrum model must be rebuilt against the authoritative HVLs above. The rebuild may investigate, as explicit model sensitivities rather than hidden tuning:

- SpekPy physics model (`kqp`, `spekcalc`, `spekpy-v1` where applicable);
- anode-angle assumption;
- correct representation of tube window / inherent filtration;
- material identity and thickness of added filters;
- whether the measured HVL grouping and filter assignment are represented exactly as in the source measurement workbook;
- low-energy spectral cutoff / transport assumptions where physically justified.

Acceptance requires the chosen model family to reproduce each measured HVL without unphysical negative filtration and without silently changing the known clinical filter.

## Change-control rule

Any future change to TERAD voltage, current, HVL, filter or applicator information must first update this document and `data/terad_input_baseline.csv`. Downstream Stage 1 production spectra and final coefficients must be regenerated from the revised baseline.
