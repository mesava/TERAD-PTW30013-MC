# Stage 1 — TERAD spectrum model

## Current status

**REOPENED.** The earlier Stage 1 acceptance was based on an older HVL set and is no longer valid for production TERAD `k_Q,Co` calculations.

The authoritative production inputs are now defined in:

- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

The Czarnecki CCRI benchmark spectra used in Stage 3 are a separate validation problem and do not redefine the TERAD beam qualities.

## Authoritative measured beam-quality anchors

| Beam | kVp | tube current | measured HVL1 | known added filtration |
|---|---:|---:|---:|---|
| Q120 | 120 | 10 mA | 0.12198 mm Cu | 4.0 mm Al |
| Q140 | 140 | 10 mA | 0.22715 mm Cu | 0.2 mm Cu |
| Q150 | 150 | 10 mA | 0.77398 mm Cu | 0.5 mm Cu |
| Q200 | 200 | 7 mA | 1.11223 mm Cu | 1.0 mm Cu |

Reference production geometry for the first intrinsic `k_Q` calculation is F50, 8 x 10 cm2 at the phantom surface, SSD 50 cm, PTW 30013 reference point at 2 cm water depth, chamber axis perpendicular to the beam.

The F40 6 x 8 cm2 and F40 4 x 15 cm2 clinical applicators are retained for the later, separate `k_g` study.

## Legacy first-pass SpekPy model

The original Stage 1 model used:

- SpekPy 2.5.4;
- W reflection target;
- nominal 20 degree anode angle;
- `kqp` physics;
- 0.5 keV bins;
- the known added clinical filter;
- one additional **non-negative equivalent-Al nuisance parameter** fitted to the measured Cu HVL.

The equivalent-Al term was never intended to represent measured physical inherent filtration. It was only a first-pass nuisance parameter for unknown tube-window/head hardening.

## Why the legacy model is no longer accepted

The earlier accepted HVLs were:

- 0.224 mm Cu at 120 kV;
- 0.410 mm Cu at 140 kV;
- 0.729 mm Cu at 150 kV;
- 1.452 mm Cu at 200 kV.

Those values are superseded.

With the corrected authoritative HVLs, the known-filter-only legacy SpekPy model is already harder than the measured beam for Q120, Q140 and Q200. A positive Al thickness can only harden the spectrum further, so the old fitting family cannot represent those measurements without an unphysical negative filtration.

Therefore:

- old generated TERAD spectra in `spectra/Qxxx.*` are **legacy/superseded artifacts** and must not be used for final production coefficients;
- `results/spekpy_fit_summary.csv` is retained only as an audit record of the superseded first-pass model;
- Stage 1 remains open until a spectrum family can reproduce the authoritative HVLs without changing the known clinical filters or requiring negative filtration.

## Diagnostic workflow

`scripts/diagnose_terad_stage1_baseline.py` compares the authoritative HVLs with the known-filter-only legacy model and classifies each beam as either:

- `positive_Al_fit_possible`, or
- `model_already_too_hard`.

Workflow: `.github/workflows/terad-stage1-baseline-diagnostic.yml`.

This diagnostic intentionally does **not** generate production spectra.

## Stage 1 rebuild plan

The rebuilt spectrum model may test, transparently and independently:

1. SpekPy physics family (`kqp`, `spekcalc`, `spekpy-v1` where supported);
2. anode-angle sensitivity;
3. tube-window / inherent-filtration representation;
4. exact material and thickness assignment of the known clinical filters;
5. low-energy spectral cutoff assumptions only when physically justified;
6. consistency of the HVL measurement grouping with the filter configuration in the source workbook.

No parameter will be silently tuned solely to force agreement.

## Re-acceptance rule

A TERAD beam can be accepted for production Stage 1 only when the chosen model:

- uses the authoritative kVp and clinical filter;
- reproduces the authoritative measured HVL within a predeclared tolerance;
- does not require negative filtration or another unphysical correction;
- documents the spectrum-engine and all nuisance/model assumptions;
- produces stable EGSnrc spectrum files for the later `D_w/D_cav` calculation.

Stage 3 benchmark validation may continue in parallel because it uses independent published CCRI inputs. Stage 4/5 production results remain blocked until both Stage 3 validation and this rebuilt TERAD Stage 1 are accepted.
