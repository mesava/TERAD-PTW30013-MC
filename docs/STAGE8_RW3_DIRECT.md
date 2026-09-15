# Stage 8 — TERAD RW3 matched/direct transfer

## Purpose

Stage 5 established the water reference response for all 12 TERAD configurations:

`R_Q,g(water) = D_w / D_cav,water`.

Stage 8 now calculates the same PTW 30013 Model B1 response in the real RW3 measurement geometry. Combining the new RW3 chamber score with the already persisted Stage 5 water score gives a direct mapping from the chamber reading in RW3 to absorbed dose to water.

For each clinical configuration:

`k_RW3→w = D_cav,water / D_cav,RW3`

`R_Q,g^(RW3→w) = D_w,water / D_cav,RW3`

`k_Q,g,Co^(RW3→w) = R_Q,g^(RW3→w) / R_Co`

The calculation also scores:

`R_Q,g(RW3) = D_RW3 / D_cav,RW3`

and the matched medium ratio:

`D_w,water / D_RW3`.

The water numerator is not recomputed: `results/stage5_absolute_scores.csv` preserves the absolute Stage 5 `D_w/history` and `D_cav,water/history` scores.

## Real RW3 geometry

User-supplied geometry is authoritative:

- RW3 transverse size: 30 × 30 cm²;
- PTW 30013 horizontal;
- chamber axis perpendicular to beam CAX;
- chamber reference point on CAX;
- stem to the right;
- 1.3 cm RW3 physically above the chamber body;
- approximately 10 cm RW3 below/downstream of the chamber region;
- applicator in contact with the RW3 surface;
- F40 SSD = 40 cm; F50 SSD = 50 cm.

For the fixed Model B1 outer chamber radius 0.3475 cm, the nominal physical centre depth is therefore

`1.3 + 0.3475 = 1.6475 cm`.

This is the direct physical geometry corresponding to the user's experimentally stated 2.0 cm water-equivalent chamber-centre depth. No artificial movement to 2.0 cm physical depth is made in RW3.

The nominal downstream boundary is placed 10 cm below the chamber body, i.e. at `z = +10.3475 cm` relative to chamber centre.

## RW3 nominal material model

The user's slab composition has not been independently chemically measured. Stage 8 therefore uses an explicit nominal material model, separate from the hard geometry inputs:

- density = 1.045 g/cm³;
- H mass fraction = 0.0759;
- C mass fraction = 0.9041;
- O mass fraction = 0.0080;
- Ti mass fraction = 0.0120;
- equivalent description: approximately 98% polystyrene + 2% TiO2 by mass.

This composition is stored in `data/rw3_nominal_material.csv` and must be treated as a model assumption with a later material sensitivity/uncertainty contribution.

PTW describes RW3 as water-equivalent for high-energy therapy beams (photon range starting at Co-60), not specifically for 120–200 kV. Therefore low-energy equivalence is not assumed; it is calculated here.

## Source / applicator model

The same accepted TERAD spectra and the same aperture convention as Stage 5 are used.

The source-to-RW3-surface distance remains the clinical SSD. Because the chamber centre is at 1.6475 cm physical depth in RW3, the source position relative to the chamber centre is:

- F40: z = -41.6475 cm;
- F50: z = -51.6475 cm.

The applicator field is specified at the RW3 surface and projected to the chamber reference plane.

As in Stage 5, proprietary applicator-wall material/thickness/internal geometry is not known and is not invented.

## Chamber / transport model

- PTW 30013 Model B1 is unchanged;
- cavity mass = `7.832972283369083e-04 g`;
- EGSnrc commit = `f4d029f625a6c96ef3456e0b6d91d46ffce613e7`;
- PCUT = 0.001 MeV;
- ECUT = 0.512 MeV;
- XCSE = 64;
- Russian Roulette = 64;
- Radiative Compton = On;
- TmpPhsp/IPSS architecture retained.

The local variance-reduction shell around the chamber and the RW3 scoring target use RW3 material, not water.

## Production statistics

Nominal production run:

- 12 clinical configurations;
- 300M histories each;
- 30 batches;
- max 4 concurrent jobs.

Predeclared gate for the direct clinical transfer coefficient:

`u(R_Q,g^(RW3→w)) / R_Q,g^(RW3→w) <= 1%`.

## Outputs

For all 12 configurations the summary will contain:

- `D_w,water/history` from Stage 5;
- `D_cav,water/history` from Stage 5;
- `D_RW3/history` from Stage 8;
- `D_cav,RW3/history` from Stage 8;
- `D_w/D_RW3`;
- `k_RW3→w`;
- `R_Q,g^(RW3→w)`;
- `k_Q,g,Co^(RW3→w)`;
- MC statistical uncertainties;
- point gate.

## What this stage does not yet close

After nominal Stage 8, the following remain uncertainty/sensitivity tasks rather than hidden tuning parameters:

- RW3 composition / TiO2 fraction and density;
- exact slab/adaptor geometry around the chamber;
- exact rectangular-field orientation relative to chamber axis;
- proprietary applicator-body scatter;
- spectrum non-uniqueness at fixed measured HVL;
- residual PTW30013 model-form uncertainty.
