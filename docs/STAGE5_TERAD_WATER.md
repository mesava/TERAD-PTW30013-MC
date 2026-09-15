# Stage 5 — TERAD matched-water production calculations

## Purpose

Stage 5 is the first production TERAD calculation after:

- PTW 30013 Model B1 benchmark validation (CCRI100/135/180/250); and
- Stage 4 Co-60 reference-ratio anchor.

The fixed Co-60 denominator is:

`R_Co = 1.12016676 ± 0.00104473` (MC relative uncertainty 0.0933%).

No chamber geometry parameter is changed in Stage 5.

## Canonical TERAD inputs

All 12 combinations from `data/terad_clinical_geometries.csv` are calculated:

- Q120 / Q140 / Q150 / Q200;
- F40, SSD 40 cm, 6×8 cm²;
- F40, SSD 40 cm, 4×15 cm²;
- F50, SSD 50 cm, 8×10 cm².

Measured HVLs remain authoritative:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

The accepted Stage-1 SpekPy 2.5.4 spectra are regenerated deterministically at workflow runtime from `data/beam_qualities.csv` using `scripts/generate_spekpy_spectra.py`.

## Water geometry

The matched-water geometry follows the supplied clinical setup as closely as the available data allow:

- chamber reference point / geometric centre at `z=0`;
- water surface at `z=-2 cm`;
- chamber-centre depth = 2.0 cm;
- transverse water phantom = 30×30 cm²;
- 10 cm water downstream of the chamber centre;
- source-to-surface distance = clinical SSD (40 or 50 cm);
- source-to-reference distance SDD = SSD + 2 cm;
- explicit air transport from source plane to water surface;
- applicator aperture is defined at the phantom surface and projected geometrically to the reference plane.

### Rectangular-field orientation convention

The user-supplied data do not separately specify which physical rectangular-applicator side lies along the Farmer chamber axis.

Stage 5 therefore uses the explicit computational convention:

`field_cm = first dimension along x / chamber axis / stem direction; second dimension along y`.

This is not treated as manufacturer-confirmed applicator orientation. It is retained as a geometry-model uncertainty/sensitivity item, particularly for 4×15 cm².

### Applicator hardware limitation

The available clinical input specifies SSD and aperture size, but not applicator-wall material, thickness, internal contour or source-to-collimator geometry. Stage 5 therefore represents the clinical field/SSD/aperture geometry but does **not** claim to model proprietary applicator-body scatter. That contribution remains a later geometry uncertainty / refinement item if hardware dimensions become available.

## Physics and chamber model

- EGSnrc pinned commit: `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`;
- accepted PTW 30013 Model B1;
- sensitive length 23.0 mm;
- nominal public-derived PMMA tip surrogate 1.5 mm;
- cavity mass `7.832972283369083e-04 g`;
- same XCSE / TmpPhsp / Russian-Roulette architecture used in the validated benchmark;
- XCSE = 64;
- RR survival = 1/64;
- PCUT = 1 keV;
- ECUT = 0.512 MeV;
- exact BCA;
- Radiative Compton enabled.

## Statistics

Each of the 12 production points uses:

`300,000,000 histories` and `30 batches`.

Each configuration has independent RANMAR seeds.

Predeclared statistical acceptance for a Stage 5 point:

`u(R_Q,g) / R_Q,g <= 1.0%`.

If a point exceeds 1%, only that point is to receive additional histories; the physical model is not adjusted to reduce uncertainty.

## Quantities reported

For every configuration `g`:

`R_Q,g = (D_w / D_cav)_(Q,g)`.

Geometry-specific Co-60-normalized response:

`k_Q,g,Co = R_Q,g / R_Co`.

For each beam quality Q, F50 is the internal geometry denominator:

`k_g,Q(g) = R_Q,g / R_Q,F50`.

By definition only after the F50 calculation exists:

`k_g,Q(F50) = 1`.

The intrinsic project output `k_Q,Co` is represented by the calculated F50 8×10 / SSD50 water point for each beam quality. The two F40 values are retained as actual calculated clinical geometry points and geometry-response terms; they are not discarded.

## Stage 5 gate

Stage 5 is complete when:

1. all 12 configurations produce valid `R_Q,g` values;
2. all 12 have relative MC uncertainty <=1%;
3. all F50 denominators exist so `k_g,Q` can be calculated for Q120/Q140/Q150/Q200;
4. no run contains fatal geometry/transport errors.

There is no fitted experimental target in this stage. No TERAD parameter may be changed retrospectively to make the 12 values appear smoother.

## After Stage 5

After successful matched-water calculation:

1. perform matched RW3 calculations;
2. derive RW3-to-water response terms;
3. perform direct 12-configuration RW3 end-to-end calculations/checks;
4. combine spectrum, chamber, field/SSD/applicator and RW3 material uncertainties.
