# Stage 8 — TERAD RW3 direct RW3→water production

## Status

**PASS — 12/12 clinical configurations.**

Workflow run: `34959596116`

Head commit: `db2369c7d4ae45fc0002a2583d11773f8abad9e8`

Final gate:

- `gate_pass=true`
- `points=12`
- `max_u_R_direct_pct=0.44695`
- `max_abs_direct_consistency_pct=0.00406`

## Geometry

Matched physical geometry is used between Stage 5 water and Stage 8 RW3:

- PTW 30013 horizontal, axis perpendicular to beam, reference point on CAX, stem right;
- RW3 phantom 29672, chamber plate 29672/U19;
- U19 chamber axis is 7 mm below its upper face;
- 13 mm additional RW3 is placed above U19;
- total physical chamber-centre depth from phantom surface = **20 mm = 2.0 cm**;
- SSD = 40 cm for F40 applicators and 50 cm for F50, measured to phantom surface;
- applicator contacts phantom surface;
- same 12 clinical Q/applicator configurations as Stage 5.

Thus Stage 5 and Stage 8 preserve the same SSD, field definition and 2.0 cm physical reference-point depth; the intended material change is water → RW3.

The former draft interpretation `1.3 cm + chamber radius = 1.6475 cm` is superseded and is not used in the accepted production run.

## RW3 nominal material model

Manufacturer anchors used by the nominal calculation:

- density = `1.045 g/cm3`;
- polystyrene `(C8H8)` with nominal `2.0% TiO2` by mass;
- manufacturer TiO2 tolerance = `±0.4 percentage points`;
- electron density = `1.012 × water`;
- mean `Z/A = 0.536`.

The nominal EGSnrc elemental mass fractions are:

- H = 0.0759
- C = 0.9041
- O = 0.0080
- Ti = 0.0120

The TiO2 tolerance is not fitted; it is reserved for sensitivity/uncertainty propagation.

## Definitions

Stage 5 supplies matched-water absolute scores:

`D_w,water / history` and `D_cav,water / history`.

Stage 8 supplies:

`D_RW3 / history` and `D_cav,RW3 / history`.

Derived quantities:

`R_RW3 = D_RW3 / D_cav,RW3`

`D_w/D_RW3 = D_w,water / D_RW3`

`k_RW3→water = D_cav,water / D_cav,RW3`

Direct response for a chamber reading made in RW3 but reported as absorbed dose to water:

`R_Q,g^(RW3→w) = D_w,water / D_cav,RW3`

Clinical Co-60-referenced coefficient:

`k_Q,g,Co^(RW3→w) = R_Q,g^(RW3→w) / R_Co`

with fixed Stage 4 denominator:

`R_Co = 1.12016676 ± 0.00104473`.

## Results

| Config | R_RW3 | u(R_direct), % | k_RW3→water | R_direct RW3→water | k_Q,g,Co direct RW3→water |
|---|---:|---:|---:|---:|---:|
| Q120 F40 4×15 | 0.89289 | 0.40342 | 0.965005 | 1.013484 | 0.904762 |
| Q120 F40 6×8 | 0.89038 | 0.35439 | 0.968267 | 1.010743 | 0.902315 |
| Q120 F50 8×10 | 0.88214 | 0.43834 | 0.952711 | 0.997722 | 0.890691 |
| Q140 F40 4×15 | 0.92978 | 0.40910 | 0.978303 | 1.038613 | 0.927195 |
| Q140 F40 6×8 | 0.92316 | 0.35831 | 0.981353 | 1.032862 | 0.922061 |
| Q140 F50 8×10 | 0.91029 | 0.44128 | 0.957577 | 1.014479 | 0.905650 |
| Q150 F40 4×15 | 0.97106 | 0.41086 | 0.983063 | 1.062059 | 0.948126 |
| Q150 F40 6×8 | 0.97307 | 0.36203 | 0.996552 | 1.064590 | 0.950385 |
| Q150 F50 8×10 | 0.95578 | 0.44695 | 0.976071 | 1.045640 | 0.933468 |
| Q200 F40 4×15 | 1.01466 | 0.39851 | 0.994113 | 1.083798 | 0.967533 |
| Q200 F40 6×8 | 1.00819 | 0.35164 | 0.987655 | 1.076843 | 0.961324 |
| Q200 F50 8×10 | 1.00702 | 0.43440 | 0.989742 | 1.074094 | 0.958870 |

Full-precision values are persisted in `results/stage8_rw3_direct_summary.csv`; gate metadata are in `results/stage8_gate.txt`.

## Internal consistency check

The direct expression

`D_w,water / D_cav,RW3`

was compared with the factorized form

`(D_w,water / D_cav,water) × (D_cav,water / D_cav,RW3)`.

The maximum absolute discrepancy over all 12 configurations was only:

**0.00406%**.

This confirms numerical consistency of the Stage 5 → Stage 8 transfer architecture within the MC precision of the calculation.

## Interpretation

The nominal direct clinical coefficients increase with beam quality, from approximately 0.89–0.90 at Q120 to 0.96–0.97 at Q200, while retaining a non-negligible geometry/applicator dependence.

These are **nominal production coefficients**, not yet the final uncertainty-qualified clinical values. They still require sensitivity propagation for at least:

1. RW3 TiO2 composition tolerance;
2. RW3 geometric/slab-position uncertainty and possible air gaps;
3. rectangular-field orientation relative to the chamber axis;
4. TERAD spectrum ambiguity compatible with measured HVL;
5. chamber-model uncertainty already constrained by the Czarnecki benchmark;
6. missing proprietary applicator-wall/head-scatter geometry.

No nominal parameter is to be retuned to reduce these uncertainty contributions.
