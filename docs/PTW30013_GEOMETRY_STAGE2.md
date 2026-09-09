# Stage 2 — PTW 30013 geometry model

## Goal

Create a transparent first-pass `egs_chamber` geometry for the user's PTW 30013 without pretending that publicly available dimensions are equivalent to a manufacturer blueprint.

## Public PTW data used

Current PTW specifications for Type 30013 report:

- nominal sensitive volume: 0.6 cm3;
- sensitive-volume radius: 3.05 mm;
- sensitive-volume length: 23.0 mm;
- wall: 0.335 mm PMMA, rho = 1.19 g/cm3;
- graphite: 0.09 mm, rho = 1.85 g/cm3;
- central electrode: Al 99.98 %, diameter 1.15 mm;
- reference point: chamber axis, 13 mm from the tip;
- recommended incidence direction: radial.

Source: PTW Farmer Ionization Chamber 30013 product specifications / detector catalog.

## Why a literal public-dimension cylinder is not sufficient

A straight cylinder with radius 3.05 mm and length 23.0 mm has gross volume

`pi * 0.305^2 * 2.30 = 0.67217 cm3`.

If a full-length 1.15 mm diameter Al electrode is removed, the remaining air volume is about

`0.64828 cm3`,

which is not the nominal 0.6 cm3. This is expected because a real Farmer chamber contains end geometry, guard/dead-volume regions and construction details not captured by the public one-line dimensions.

Therefore Stage 2 does **not** force the public 23 mm length into the production model as if it were an exact active-cylinder length.

## Additional published geometry constraint

Puxeu Vaqué et al. (ESTRO 2017, PV-0419, *The impact that geometric variability in ionization chamber construction has on kQ,Q0*) reported for the nominal PTW 30013 geometry used in their Monte Carlo study:

- internal cavity volume: 637.1 mm3;
- central-electrode volume: 22.02 mm3;
- net cavity volume: 615.1 mm3.

Their chamber geometries were derived from manufacturer dimensional/tolerance information. The publication does not provide enough detail to reconstruct the complete proprietary chamber geometry, but these aggregate volumes are useful independent constraints.

## Model A: public-volume-constrained active body

Model A uses the public PTW radial dimensions/materials, while choosing straight-cylinder lengths that reproduce the above published aggregate volumes:

- air-cavity radius = 3.05 mm;
- internal cavity length = 21.80 mm;
- Al electrode radius = 0.575 mm;
- Al electrode length = 21.20 mm;
- graphite thickness = 0.09 mm;
- PMMA thickness = 0.335 mm.

This produces approximately:

- internal cavity = 0.63710 cm3;
- central electrode = 0.02202 cm3;
- net air cavity = 0.61508 cm3.

The electrode is centered longitudinally, leaving 0.30 mm air-only sections at each end of the modeled active body.

### Material handling

`521icru` contains `170C521ICRU` at rho = 1.7 g/cm3. PTW specifies graphite at 1.85 g/cm3. In the Model A `EGS_ConeStack`, only the graphite regions are therefore assigned a relative-density multiplier

`1.85 / 1.70 = 1.088235294117647`.

PMMA, air, Al and water use the corresponding 521icru media.

## What Model A intentionally excludes

Model A does **not** claim to reproduce:

- detailed tip shape;
- guard-ring geometry and electric-field-defined dead volume;
- exact electrode base;
- detailed stem/cable construction;
- manufacturing tolerances of chamber serial 013488.

Those effects are not silently ignored. They become a later geometry-model sensitivity term. A more detailed Model B will only be introduced where dimensions are supported by literature/manufacturer information or explicitly labelled as a sensitivity surrogate.

## Stage 2 smoke geometry

The first executable test places Model A:

- in a 30 x 30 x 30 cm3 water phantom;
- chamber axis perpendicular to the beam (x-axis chamber, z-axis beam);
- chamber reference point at 2 cm water depth;
- nominal TERAD F50 geometry, SSD = 50 cm;
- Q120 Stage 1 spectrum;
- field scaled so that an 8 x 10 cm2 surface field corresponds to 8.32 x 10.40 cm2 at the chamber plane.

The purpose of this run is only to prove geometry/source/scoring compatibility and finite cavity dose. It is **not** accepted as a clinical `k_Q` result.

## Stage 2 acceptance

Stage 2 Model A is accepted for benchmark work only when:

1. analytic geometry invariants reproduce the published aggregate volumes;
2. `egs_chamber` parses the geometry and identifies the intended cavity regions;
3. a Q120 smoke calculation finishes without geometry errors/segmentation fault and gives finite non-zero cavity dose;
4. no unsupported stem/guard/tip dimensions are presented as manufacturer truth.

After this, Stage 3 uses published medium-kV beam-quality benchmarks to determine whether the simplified geometry is adequate for `k_Q` or requires refinement before TERAD production results are trusted.
