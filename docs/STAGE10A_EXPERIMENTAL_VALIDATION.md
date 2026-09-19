# Stage 10A — clinical orientation + experimental RW3 validation

## Purpose

Stage 10A is the practical closeout of the completed Monte Carlo programme. It does **not** create a new Monte Carlo coefficient family.

It answers two concrete questions:

1. **Which MC field orientation corresponds to the real TERAD/PTW30013 setup?**
2. **Does the measured relative chamber response in water versus RW3 agree with the MC-predicted chamber-response transfer?**

The nominal MC coefficients already exist. Stage 10A determines how they should be mapped to the real setup and tests the experimentally observable part of the RW3 transfer.

---

## 1. Orientation closeout

### 1.1 MC coordinate convention

The PTW30013 longitudinal chamber axis is X.

Therefore the Stage 8S3d F40 baseline fields mean:

- `4x15`: 4 cm along the chamber longitudinal axis, 15 cm transverse;
- `6x8`: 6 cm along the chamber longitudinal axis, 8 cm transverse.

Stage 9B calculated a 90-degree rotation:

- `4x15 -> 15x4`;
- `6x8 -> 8x6`.

### 1.2 What must be established physically

For each applicator, record:

- applicator ID / label;
- nominal field dimensions;
- which physical side is parallel to the PTW30013 longitudinal axis/stem direction;
- chamber stem direction;
- beam central-axis direction;
- a photograph or sketch with dimensions marked.

Do not infer orientation from the written order of field dimensions alone.

### 1.3 F40 coefficients available for both model orientations

| Q | baseline 4x15 | rotated 15x4 | baseline 6x8 | rotated 8x6 |
|---|---:|---:|---:|---:|
| Q120 | 0.900806 | 0.890606 | 0.897761 | 0.892892 |
| Q140 | 0.924808 | 0.914491 | 0.916203 | 0.927511 |
| Q150 | 0.951920 | 0.937132 | 0.943819 | 0.944426 |
| Q200 | 0.966342 | 0.956138 | 0.961850 | 0.959177 |

The rotated values are Stage 9B sensitivity results. They are not selected until the real physical orientation is documented.

For F50 the current nominal convention is 8 cm along X and 10 cm along Y. A 10x8 orientation was not calculated. If the real F50 setup is opposite, record this as an unresolved geometry item first; only then decide whether a targeted F50 orientation calculation is justified.

---

## 2. Experimental validation observable

The most useful validation that does not require an independent kV absorbed-dose calibration is the ratio of corrected readings of the **same PTW30013** in water and RW3.

For the same beam quality Q and geometry g:

`V_exp(Q,g) = M_corr,water(Q,g) / M_corr,RW3(Q,g)`

The corresponding MC observable is:

`V_MC(Q,g) = D_cav,water(Q,g) / D_cav,RW3(Q,g)`

Therefore compare:

`Delta_V(%) = 100 * [V_exp / V_MC - 1]`

The calibration coefficient `N_D,w(Co)` cancels from this relative test.

This test directly checks the chamber-response transfer between water and RW3, including the real setup, chamber orientation and phantom response.

### Important limitation

This is **not** an independent absolute validation of the complete direct coefficient

`K_Q,g,Co^(RW3->w) = [D_w,water / D_cav,RW3] / R_Co`.

It validates the experimentally observable water/RW3 chamber-response part.

A fully independent absolute validation of K would require an independent traceable estimate of absorbed dose to water at the same Q/g, for example a suitable independently calibrated/reference kV dosimetry method.

---

## 3. Measurement geometry

Use the same geometry as the MC model.

### RW3

- RW3 phantom 30x30 cm;
- PTW30013 horizontal;
- chamber centre on the central axis;
- chamber longitudinal axis perpendicular to the beam;
- stem direction recorded explicitly;
- physical chamber-centre depth = 2.0 cm;
- 13 mm RW3 above the U19 chamber plate plus U19 H1 = 7 mm to centre;
- approximately 10 cm RW3 downstream;
- applicator in contact with the phantom surface;
- SSD measured to the phantom surface;
- nominal field size defined at the surface/contact plane.

### Water

- same Q and applicator;
- same SSD to water surface;
- chamber centre at physical depth 2.0 cm;
- same chamber longitudinal orientation relative to the field;
- same field dimensions at water surface.

The comparison requires **physical-depth matching**, not water-equivalent-depth matching.

---

## 4. Efficient measurement matrix

All 12 Q/geometry validation points can be acquired with only six physical phantom setups:

| Setup | Medium | Geometry | Q measured |
|---|---|---|---|
| 1 | water | F40 4x15 | Q120, Q140, Q150, Q200 |
| 2 | RW3 | F40 4x15 | Q120, Q140, Q150, Q200 |
| 3 | water | F40 6x8 | Q120, Q140, Q150, Q200 |
| 4 | RW3 | F40 6x8 | Q120, Q140, Q150, Q200 |
| 5 | water | F50 8x10 | Q120, Q140, Q150, Q200 |
| 6 | RW3 | F50 8x10 | Q120, Q140, Q150, Q200 |

If the physical orientation mapping shows that an F40 field corresponds to the rotated Stage 9B convention, use the matching rotated MC interpretation.

---

## 5. Readings

For each Q/setup:

- use the same chamber SN013488 and electrometer chain;
- keep polarity and operating voltage fixed;
- allow normal chamber/electrometer stabilization;
- acquire at least 5 repeat readings;
- record temperature and pressure for each medium/setup;
- calculate `M_corr` using the accepted clinical correction chain;
- record `k_TP`, `k_s`, `k_pol`, `k_elec` where applicable;
- use the mean corrected reading for the water/RW3 ratio.

Because water and RW3 measurements are not simultaneous, environmental corrections must be applied separately rather than assumed to cancel.

### Repositioning check

For at least one sensitive F40 geometry, preferably 4x15, perform a complete teardown/rebuild and repeat the measurement. If practical, use three independent setups.

This provides a real experimental estimate of setup/repositioning repeatability and can later support Stage 9A-type uncertainty without inventing arbitrary geometric perturbations.

---

## 6. Experimental uncertainty and compatibility

For each Q/g obtain:

- `V_exp`;
- relative standard uncertainty `u_rel(V_exp)`, including repeatability and, when available, repositioning;
- `V_MC`;
- `u_rel(V_MC)` from the existing MC chamber scores.

For a first compatibility assessment:

`u_rel(ratio) = sqrt[u_rel(V_exp)^2 + u_rel(V_MC)^2]`

`z = (V_exp / V_MC - 1) / u_rel(ratio)`

where relative uncertainties are expressed as fractions.

Interpretation:

- `|z| <= 2`: experimentally compatible with MC at the chosen uncertainty model;
- `|z| > 2`: investigate setup/orientation/corrections/model mismatch before changing K.

Do not retune the MC geometry or measured HVL merely to improve agreement.

---

## 7. What Stage 10A can and cannot conclude

### If validation agrees

The result supports:

- the real orientation mapping;
- RW3 physical geometry;
- the relative water/RW3 chamber-response transfer;
- clinical use of the existing nominal K table subject to the final uncertainty budget.

### If validation disagrees

Investigate, in this order:

1. real field/chamber orientation;
2. physical chamber-centre depth;
3. SSD/contact condition;
4. actual RW3 stack and U19 placement;
5. measurement corrections and repeatability;
6. field identification/dimensions;
7. only then consider whether a targeted new MC sensitivity is justified.

Do not immediately introduce a new chamber or source model.

---

## 8. Stage 10A deliverables

1. Completed orientation record for F40 4x15, F40 6x8 and F50 8x10.
2. Raw/corrected measurement table for water and RW3.
3. Experimental `V_exp` for all measured Q/g.
4. Existing-MC `V_MC` extracted from archived Stage 8S3d/8S3b point summaries — **no new transport required**.
5. `Delta_V`, uncertainty and z compatibility table.
6. Decision on which F40 orientation-specific K values map to the real clinical setup.
7. Measured setup/repositioning contribution for the final uncertainty budget.

After Stage 10A the next core task is Stage 10B: final uncertainty budget and clinical coefficient table.
