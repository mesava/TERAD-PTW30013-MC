# TERAD production input baseline

This document is the production input control record for TERAD calculations in this repository.

It is intentionally separated from the Czarnecki published-benchmark inputs. Stage 3 CCRI100/135/180/250 beams exist only to validate the PTW 30013 Monte Carlo model and must never overwrite or redefine the clinical TERAD beam settings below.

> **HVL provenance hold:** the tube voltages, currents, clinical removable filters and applicator inventory below remain accepted. The numeric HVLs are currently **PROVISIONAL** because Stage 1R showed that the same recorded D0/D1/D2 readings were later associated with different absorber-thickness pairs `(x1,x2)` in different spreadsheet versions. Production spectrum fitting and final TERAD `k_Q,Co` are blocked until the physical Cu plate stacks used for D1/D2 are verified or the HVLs are remeasured. See `docs/STAGE1R_HVL_PROVENANCE_AUDIT.md`.

## Controlled TERAD beam set

| Beam | Tube voltage | Tube current | Current workbook HVL1 (Cu) | HVL status | Known added filtration | Clinical applicators represented in the source spreadsheet |
|---|---:|---:|---:|---|---|---|
| Q120 | 120 kV | 10 mA | 0.12198 mm Cu | PROVISIONAL — plate provenance hold | 4.0 mm Al | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q140 | 140 kV | 10 mA | 0.22715 mm Cu | PROVISIONAL — plate provenance hold | 0.2 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q150 | 150 kV | 10 mA | 0.77398 mm Cu | PROVISIONAL — plate provenance hold | 0.5 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |
| Q200 | 200 kV | 7 mA | 1.11223 mm Cu | PROVISIONAL — plate provenance hold | 1.0 mm Cu | F40 6x8 cm2; F40 4x15 cm2; F50 8x10 cm2 |

Machine-readable copy: `data/terad_input_baseline.csv`. Until the provenance hold is closed, the HVL column in that CSV is retained for traceability only and must not be interpreted as an accepted production-spectrum target.

## Production reference geometry

The first intrinsic TERAD `k_Q` calculation will use one real clinical geometry as the reference condition:

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

## Stage 1 history

The first Stage 1 spectra were fitted to an earlier project HVL set:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

A later spreadsheet reconstruction produced the current values 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu. Stage 1R subsequently demonstrated that the later values arise after changing the absorber-thickness pairs associated with unchanged D0/D1/D2 readings. Therefore neither historical set is promoted here as final merely because it produces a more convenient spectrum model. The physical measurement provenance decides the accepted HVL.

The original Stage 1 model used SpekPy 2.5.4 with a W target, nominal 20 degree anode angle, `kqp` physics, the known added filter and then fitted only a non-negative equivalent-Al nuisance thickness.

## Stage 1R evidence

### Stage 1R-1 feasibility map

GitHub Actions run `34566147632` scanned 108 combinations (four beams × `kqp/spekcalc/spekpy-v1` × target angle 5–45 degrees) with the clinical removable filter fixed. For the current provisional HVLs, Q120/Q140/Q200 had no positive-filtration solution; Q150 was generally representable.

### Stage 1R-2 tube-informed audit

Run `34566631576` added TERAD hardware constraints: W target, candidate 30 degree target angle and Be exit-window sensitivity around the documented 0.8 mm value. The Be window hardened the model slightly and did not explain the soft provisional Q120/Q140/Q200 HVLs.

### Stage 1R-3 effective-kVp diagnostic

Run `34566781628` solved the idealized constant-potential kVp required to reproduce the provisional HVLs with W / 30 degree / 0.8 mm Be / clinical filter held fixed. Representative `kqp` solutions were about 83.9, 98.4, 162.2 and 165.1 kV for nominal 120, 140, 150 and 200 kV respectively. The inconsistent direction rules out a simple common kV calibration shift as an adequate explanation.

### Stage 1R-4 provenance audit

Spreadsheet comparison found unchanged D0/D1/D2 readings but changed `x1/x2` assignments between versions. This is now the primary upstream uncertainty. Full details are in `docs/STAGE1R_HVL_PROVENANCE_AUDIT.md`.

## Acceptance rule before production spectrum generation

Before any production TERAD `k_Q,Co` calculation:

1. recover the actual absorber plate IDs/stacks used for D1 and D2 for Q120/Q140/Q150/Q200, or repeat the narrow-beam HVL measurements while recording those IDs;
2. calculate each HVL from the verified physical `x1,x2` and the corresponding D0/D1/D2;
3. update `data/terad_input_baseline.csv` with the accepted HVLs;
4. rebuild Stage 1 spectra without unphysical negative filtration and without changing the known clinical removable filters;
5. only then proceed to the Co-60 denominator and TERAD production `k_Q,Co`.

## Change-control rule

Any future change to TERAD voltage, current, accepted HVL, clinical filter or applicator information must first update this document and `data/terad_input_baseline.csv`. Downstream Stage 1 production spectra and final coefficients must then be regenerated from the revised baseline.
