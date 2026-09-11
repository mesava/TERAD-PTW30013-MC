# Canonical TERAD MC task

This file is the canonical statement of the user-supplied Monte Carlo task. It has priority over later exploratory branches or temporary diagnostics.

## 1. Hard input data supplied by the user

### TERAD beam qualities

| Beam | Nominal tube voltage | Measured HVL | Added clinical filter | Tube current |
|---|---:|---:|---|---:|
| Q120 | 120 kV | 0.224 mm Cu | 4.0 mm Al | 10 mA |
| Q140 | 140 kV | 0.410 mm Cu | 0.2 mm Cu | 10 mA |
| Q150 | 150 kV | 0.729 mm Cu | 0.5 mm Cu | 10 mA |
| Q200 | 200 kV | 1.452 mm Cu | 1.0 mm Cu | 7 mA |

These four HVLs are the authoritative measured beam-quality anchors for production TERAD MC.

### Applicators / SSD / field sizes

Every one of the four beam qualities uses all three clinical applicator geometries:

- F40, field 6 x 8 cm2 -> SSD 40 cm;
- F40, field 4 x 15 cm2 -> SSD 40 cm;
- F50, field 8 x 10 cm2 -> SSD 50 cm.

The applicator is pressed directly against the phantom surface.

Therefore the real TERAD task contains **12 kV/applicator combinations**, not only the F50 geometry.

## 2. User-supplied RW3 chamber geometry

Phantom and chamber setup:

- RW3 slab phantom, nominal transverse dimensions 30 x 30 cm2;
- PTW 30013 Farmer chamber horizontal;
- chamber axis perpendicular to the x-ray beam central axis;
- chamber geometric centre/reference point on the beam central axis;
- stem directed to the right;
- 1.3 cm RW3 physically above the chamber body, corresponding to a chamber-centre water-equivalent depth of 2.0 cm in the stated setup;
- approximately 10 cm RW3 downstream/below the chamber region as specified by the user;
- lateral RW3 margin at least 10 cm;
- SSD is set by the applicator (F40 or F50);
- the applicator contacts the RW3 surface.

The canonical reference-point statement for the experimental geometry is:

`PTW 30013 chamber centre = 2.0 cm water-equivalent depth in RW3.`

## 3. What is user input versus modelling choice

The following are **hard inputs** and must not be changed to improve agreement:

- kVp values 120/140/150/200;
- HVLs 0.224/0.410/0.729/1.452 mm Cu;
- added filters 4.0 mm Al / 0.2 mm Cu / 0.5 mm Cu / 1.0 mm Cu;
- all three applicator geometries at each kVp;
- RW3 setup, chamber orientation and 2 cm water-equivalent chamber-centre depth.

The following are **methodological decomposition choices**, not replacements for the user's real geometry:

1. compute an intrinsic chamber beam-quality correction in water;
2. choose F50 / 8 x 10 cm2 / SSD 50 cm as an internal reference geometry for that intrinsic calculation because it is the largest SSD and field nearest to 10 x 10 cm2 among the supplied clinical options;
3. determine separate field/SSD/applicator corrections for the two F40 geometries;
4. determine a separate RW3-to-water correction;
5. combine the terms only at the end and also retain direct end-to-end MC checks in the actual RW3 geometries.

Thus use of F50 as a reference geometry never removes the two F40 geometries from the task.

## 4. Factorisation used by the project

Define for a beam quality Q in water:

`R_Q = (D_w / D_cav)_Q`

and for the Co-60 calibration quality:

`R_Co = (D_w / D_cav)_Co`.

Then

`k_Q,Co = R_Q / R_Co`.

For clinical applicator geometry g at the same Q, define a separate geometry-response term relative to the chosen F50 reference:

`k_g,Q(g) = (D_w / D_cav)_(Q,g) / (D_w / D_cav)_(Q,F50-8x10)`.

RW3 is treated separately by comparing matched water and RW3 calculations rather than silently assuming water equivalence at 120-200 kV.

The project must also perform direct end-to-end calculations for all 12 actual RW3 configurations so the factorised approach can be checked against the real measurement geometry.

## 5. Co-60 denominator already used in the project

Project calibration anchor:

`N_D,w(Co-60) = 5.389e7 Gy/C` for PTW 30013 SN 013488.

MC reference geometry retained by the project:

- water;
- chamber reference point at 5 g/cm2 depth;
- source-to-reference-point distance 100 cm;
- 10 x 10 cm2 field at the chamber reference plane.

This is a separate denominator/reference-quality calculation and does not redefine the TERAD RW3 measurement geometry.

## 6. Production outputs required

The first intrinsic output set is:

- k_120,Co;
- k_140,Co;
- k_150,Co;
- k_200,Co.

Then the project must provide, for each kVp:

- F50 8 x 10 reference result;
- F40 6 x 8 geometry correction/result;
- F40 4 x 15 geometry correction/result;
- RW3-to-water correction or equivalent matched-medium response;
- direct end-to-end RW3 result for all three applicators;
- uncertainty contributions from spectrum shape, chamber geometry, applicator/field geometry and RW3 material modelling.

## 7. Stage-1 spectrum status

The accepted first-pass SpekPy spectra were fitted to the correct user-supplied HVLs in this document:

- Q120: 0.224 mm Cu;
- Q140: 0.410 mm Cu;
- Q150: 0.729 mm Cu;
- Q200: 1.452 mm Cu.

The temporary Stage-1R diagnostics based on 0.12198 / 0.22715 / 0.77398 / 1.11223 mm Cu are superseded and are not part of the production task.
