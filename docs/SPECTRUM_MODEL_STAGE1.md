# Stage 1 — TERAD spectrum model

## Current status

**ACCEPTED first-pass production spectrum model.**

The authoritative TERAD HVLs are the user-supplied measured values:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

These are the values for which the original Stage 1 SpekPy model was constructed and accepted. A later temporary branch mistakenly substituted 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu from another calculation context; that branch is superseded and must not be used for TERAD production MC.

The authoritative inputs are defined in:

- `docs/TERAD_INPUT_BASELINE.md`;
- `data/terad_input_baseline.csv`;
- `data/beam_qualities.csv`.

## Accepted first-pass SpekPy model

- SpekPy 2.5.4;
- W reflection target;
- nominal 20 degree anode angle;
- `kqp` physics;
- 0.5 keV bins;
- spectrum distance parameter z = 100 cm;
- known clinical removable filter;
- one additional non-negative equivalent-Al nuisance thickness fitted where needed to reproduce the measured Cu HVL.

The equivalent-Al term is a model nuisance parameter for unknown tube/head hardening. It is **not** claimed to be the measured physical inherent filtration.

## Accepted fit results

| Beam | kVp | Clinical filter | Target HVL1 (mm Cu) | Known-filter-only HVL (mm Cu) | Fitted equivalent Al (mm) | Final HVL1 (mm Cu) | Relative error |
|---|---:|---|---:|---:|---:|---:|---:|
| Q120 | 120 | 4.0 mm Al | 0.224000 | 0.207172 | 0.447246 | 0.224000 | 0.000% |
| Q140 | 140 | 0.2 mm Cu | 0.410000 | 0.388502 | 0.525157 | 0.410000 | 0.000% |
| Q150 | 150 | 0.5 mm Cu | 0.729000 | 0.723665 | 0.264108 | 0.729000 | 0.000% |
| Q200 | 200 | 1.0 mm Cu | 1.452000 | 1.452955 | 0.000000 | 1.452955 | +0.0658% |

All four satisfy the Stage 1 HVL acceptance target of <=0.5% relative error. Q200 requires no additional equivalent Al; the known-filter-only model is already within tolerance.

The complete numerical record is `results/spekpy_fit_summary.csv`.

Additional model outputs from that accepted fit include approximate mean photon energies:

- Q120: 56.84 keV;
- Q140: 65.41 keV;
- Q150: 75.36 keV;
- Q200: 96.21 keV.

## Reference TERAD geometry for later MC

The first intrinsic `k_Q` calculation uses:

- water;
- SSD = 50 cm;
- F50 applicator;
- field = 8 x 10 cm2 at phantom surface;
- PTW 30013 reference point at 2 cm water depth;
- chamber axis perpendicular to beam axis.

F40 6 x 8 cm2 and F40 4 x 15 cm2 are retained for the later separate `k_g` field/SSD/applicator study.

## Spectrum-model uncertainty

Matching HVL does not prove the full spectral shape is unique. Therefore Stage 1 acceptance means the spectra are suitable as the **first-pass production source model**, not that spectrum-shape uncertainty is zero.

Later sensitivity work should quantify how alternative physically plausible same-HVL spectra change `D_w/D_cav` and `k_Q,Co`. That uncertainty is handled downstream rather than by reopening the measured HVLs.

## Superseded Stage 1R diagnostics

Runs `34566147632`, `34566631576`, and `34566781628` used the mistakenly substituted HVL set and are retained only as audit history. Their conclusions do not apply to the authoritative TERAD beam qualities above.

## Stage 1 acceptance

**Stage 1 = complete / accepted first pass.**

Production can proceed to later stages once the independent PTW 30013 benchmark gate is accepted.
