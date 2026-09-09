# Stage 1 — TERAD spectrum model

## Purpose

Generate reproducible first-pass photon spectra for the measured TERAD beam qualities and export them to EGSnrc-compatible histogram spectrum files.

## Measured beam-quality anchors

| Beam | kVp | measured HVL1 | known added filtration |
|---|---:|---:|---|
| Q120 | 120 | 0.224 mm Cu | 4.0 mm Al |
| Q140 | 140 | 0.410 mm Cu | 0.2 mm Cu |
| Q150 | 150 | 0.729 mm Cu | 0.5 mm Cu |
| Q200 | 200 | 1.452 mm Cu | 1.0 mm Cu |

All HVL values are treated as copper HVL.

## Nominal SpekPy model

- SpekPy version pinned in CI: 2.5.4
- reflection target: W
- tube potential: measured nominal kVp for each quality
- anode angle: 20 degrees **nominal first-pass assumption only**
- physics model: `kqp`
- energy bin width: 0.5 keV
- central-axis position: x = 0, y = 0, z = 100 cm
- 1 mAs normalization
- bremsstrahlung and characteristic radiation enabled

The 20 degree angle is not asserted to be the physical TERAD anode angle. It will be treated later as a model sensitivity parameter (planned 12/20/30 degree comparison with HVL re-fitting).

## Effective filtration fit

The known added filter is applied first. Then a non-negative equivalent-Al thickness is fitted until

`HVL1_Cu(model) = HVL1_Cu(measured)`.

The fitted thickness is a **nuisance/model parameter**. It must not be interpreted as the actual physical inherent filtration of the TERAD tube head. It absorbs unknown window, inherent filtration and other spectral-hardening effects in this first-pass model.

If the spectrum with the known added filtration is already harder than the measured beam, the workflow fails instead of applying an unphysical negative filter.

Acceptance for Stage 1 generation:

`abs(HVLcalc / HVLmeas - 1) <= 0.5%`.

## EGSnrc export

The SpekPy spectrum is exported in two forms:

1. `Qxxx_spekpy.csv` — mid-bin energy in keV and differential fluence in photons cm^-2 keV^-1.
2. `Qxxx.ensrc` — EGSnrc histogram spectrum format, MODE=1 (counts/MeV).

For the `.ensrc` export, SpekPy mid-bin energies are converted to bin edges. Differential fluence is converted from per-keV to per-MeV and normalized so the histogram integral is unity. Absolute normalization is not required for the later `k_Q` dose-ratio calculation; only the energy distribution is used.

## Stage-1 outputs to review before proceeding

- fitted equivalent Al thickness for all four qualities;
- initial and final Cu HVL1;
- Cu HVL2 and homogeneity coefficient;
- mean energy and Cu effective energy;
- successful creation of all four `.ensrc` spectra;
- no model-hardness failure and HVL error within 0.5%.

Only after these checks are accepted should the spectra be connected to the PTW 30013 / water Monte Carlo benchmark.
