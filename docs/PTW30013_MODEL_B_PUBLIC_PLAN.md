# PTW 30013 Model B-public — construction policy

## Purpose

Model A was intentionally a simplified public/aggregate geometry. Stage 3G showed a systematic benchmark discrepancy at high statistics. Stage 3H first corrects benchmark-spectrum fidelity; if Stage 3H-1 still fails, the next controlled step is Model B-public.

Model B-public is **not** claimed to reproduce proprietary PTW manufacturer drawings. It is a transparent geometry constrained by public specifications, with unknown internal details represented only by bounded sensitivity models.

Machine-readable constraints: `data/ptw30013_modelB_public_constraints.csv`.

## Publicly fixed constraints

The following values are treated as fixed unless a stronger primary source supersedes them:

- nominal sensitive volume: 0.6 cm3;
- sensitive radius: 3.05 mm;
- sensitive length: 23.0 mm;
- PMMA wall: 0.335 mm, density 1.19 g/cm3;
- graphite wall: 0.09 mm, density 1.85 g/cm3;
- central electrode: Al 99.98, diameter 1.15 mm;
- reference point: on chamber axis, 13 mm from chamber tip;
- design: guarded;
- recommended incidence: radial.

These are public PTW specifications and must not be tuned against the Czarnecki benchmark.

## Unknown / proprietary internal details

The following are not established from the public specification used by this repository:

- exact internal tip shape and cavity-front termination;
- exact guard-ring length, radius and material distribution;
- insulator shape/material distribution;
- exact central-electrode axial length/base geometry;
- exact stem internal geometry and transition from chamber body to stem.

No single guessed value for these quantities may be labelled as the real PTW 30013 construction.

## Difference from Model A

Model A currently uses an effective internal cavity length of 21.80 mm and a simple five-layer cone-stack representation with simplified 0.30 mm axial end regions. It does not contain a realistic guard, insulator, electrode base, tip or stem transition.

The public specification lists a sensitive-volume length of 23.0 mm. Model B-public therefore starts from the public 23.0 mm sensitive-length constraint rather than silently retaining the Model A 21.80 mm effective length.

## Planned geometry hierarchy

If Stage 3H-1 confirms that paper-faithful spectrum/air treatment does not validate Model A, Model B-public will be developed in controlled increments:

1. **B0 — public sensitive-volume envelope**
   - radius 3.05 mm;
   - length 23.0 mm;
   - public graphite/PMMA radial wall;
   - public Al electrode diameter;
   - cavity mass recalculated consistently from the modeled net air volume.

2. **B1 — tip sensitivity family**
   - introduce a physically explicit chamber-tip region;
   - vary only undocumented tip dimensions over a declared sensitivity range;
   - no fit-to-target selection.

3. **B2 — guard / insulator sensitivity family**
   - introduce guard and insulating regions as separate materials/volumes;
   - use documented existence of the guarded design;
   - unknown dimensions remain sensitivity variables.

4. **B3 — stem-transition sensitivity family**
   - include a finite stem/body transition rather than replacing both chamber ends by symmetric water/PMMA shells;
   - evaluate effect under radial incidence.

At each level, volume, air mass, region labels and VRT enhancement regions must be validated automatically before MC execution.

## Acceptance logic

Model B-public is not selected because it happens to hit `k100,250 = 0.95355`. A geometry family is considered scientifically useful if:

- every fixed parameter is traceable to a public source or explicit aggregate constraint;
- unknown dimensions are labelled as sensitivities;
- MC implementation passes mass/volume/region checks;
- independent benchmark qualities are reproduced within the combined uncertainty without beam-specific retuning;
- sensitivity trends are physically interpretable and stable with statistics.

After any candidate survives CCRI100/250, CCRI135 and CCRI180 must be calculated as independent intermediate-quality validation before the chamber model is accepted for TERAD production.
