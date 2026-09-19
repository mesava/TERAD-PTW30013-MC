# Stage 10A — clinical orientation + experimental RW3 validation

## Purpose

Stage 10A is the practical closeout of the completed Monte Carlo programme. It does **not** create a new Monte Carlo coefficient family.

It originally answered two concrete questions:

1. **Which MC field orientation corresponds to the real TERAD/PTW30013 setup? — CLOSED.**
2. **Does the measured relative chamber response in water versus RW3 agree with the MC-predicted chamber-response transfer? — CURRENT TASK.**

The clinical orientation was confirmed on 2026-09-19: the **first field dimension is parallel to the PTW30013 longitudinal axis**. Therefore the real setup matches the Stage 8S3d baseline convention and the current nominal K table is the applicable orientation table. Stage 9B rotated values remain sensitivity results only.

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

### 1.2 Confirmed clinical orientation

The project now explicitly adopts the clinical convention confirmed by the user:

| Applicator | Nominal field | Side parallel to PTW30013 longitudinal axis | Transverse side | MC mapping |
|---|---|---:|---:|---|
| F40 | 4x15 | **4 cm** | **15 cm** | Stage 8S3d baseline 4x15 |
| F40 | 6x8 | **6 cm** | **8 cm** | Stage 8S3d baseline 6x8 |
| F50 | 8x10 | **8 cm** | **10 cm** | Stage 8S3b/8S3d baseline 8x10 |

This closes the orientation-selection question. A photograph/sketch is optional documentation, not a prerequisite for coefficient selection.

### 1.3 F40 coefficients available for both model orientations

| Q | baseline 4x15 | rotated 15x4 | baseline 6x8 | rotated 8x6 |
|---|---:|---:|---:|---:|
| Q120 | 0.900806 | 0.890606 | 0.897761 | 0.892892 |
| Q140 | 0.924808 | 0.914491 | 0.916203 | 0.927511 |
| Q150 | 0.951920 | 0.937132 | 0.943819 | 0.944426 |
| Q200 | 0.966342 | 0.956138 | 0.961850 | 0.959177 |

The rotated values are retained only as Stage 9B sensitivity results for a hypothetical 90-degree rotation. **No orientation correction is applied to the clinical coefficients.**

For F50 the confirmed clinical convention is also the baseline convention: 8 cm along X and 10 cm along Y. Therefore no F50 10x8 calculation is required for the current clinical setup.

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

### 2.1 Existing MC targets for the experiment

No new transport is required. The archived Stage 8S3d/8S3b chamber scores give:

| Q | F40 4x15 V_MC | u_rel(V_MC) | F40 6x8 V_MC | u_rel(V_MC) | F50 8x10 V_MC | u_rel(V_MC) |
|---|---:|---:|---:|---:|---:|---:|
| Q120 | **0.959695** | 0.562% | **0.963116** | 0.496% | **0.955912** | 0.615% |
| Q140 | **0.975530** | 0.567% | **0.970685** | 0.499% | **0.961926** | 0.618% |
| Q150 | **0.997085** | 0.574% | **0.981965** | 0.503% | **0.983346** | 0.621% |
| Q200 | **1.000153** | 0.554% | **0.992860** | 0.488% | **0.991253** | 0.602% |

Machine-readable targets:

- `results/stage10a_mc_validation_targets.csv`.

The experimental ratio should be compared to these values, not directly to the clinical K coefficient.

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

The clinical orientation is already confirmed as the baseline convention, so all Stage 10A comparisons use the baseline targets above.

---

## 5. Operational procedure — step by step

### 5.1 Before irradiation

1. Use **PTW30013 SN013488** and the same electrometer/range for water and RW3.
2. Use the routine clinical polarity and chamber voltage. Do not change voltage between paired water/RW3 measurements.
3. Allow the chamber/electrometer and the TERAD tube to reach their normal measurement-ready state.
4. Check zero/leakage before the series and again after the series.
5. Use the established beam settings for Q120/Q140/Q150/Q200; do not refit HVL or filtration for the experiment.
6. For each Q choose an irradiation time/exposure in the stable operating region, long enough that timer start/end effects are negligible for the required precision. Keep that irradiation setting **identical for water and RW3** for the same Q and geometry.
7. If a waterproof sleeve or any extra entrance material would be required in water, record it explicitly. Do not silently introduce material that is absent from the MC geometry.

### 5.2 Preferred measurement order

Scientifically, the cleanest order is to keep the water/RW3 measurements for one geometry as close in time as practical:

1. F40 4x15 — water, Q120/Q140/Q150/Q200.
2. F40 4x15 — RW3, Q120/Q140/Q150/Q200.
3. F40 6x8 — water, all four Q.
4. F40 6x8 — RW3, all four Q.
5. F50 8x10 — water, all four Q.
6. F50 8x10 — RW3, all four Q.

This reduces bias from long-term tube-output drift.

If repeated water/RW3 phantom exchange is impractical, an all-water block followed by an all-RW3 block is acceptable **only if beam-output drift is measured or included in the experimental uncertainty**.

### 5.3 Set up the water point

For each applicator:

1. Set the applicator to its clinical SSD: F40 = 40 cm, F50 = 50 cm, referenced to the **water surface**.
2. Set the exit/contact plane of the applicator to the water surface without adding an unmodelled plate.
3. Place the PTW30013 horizontally, axis perpendicular to the beam.
4. Put the chamber reference point/geometric centre used in the MC at a **physical depth of 20.0 mm** below the water surface.
5. Do **not** apply a water-equivalent-depth conversion or an EPOM displacement shift: Stage 10A must reproduce the geometric MC setup.
6. Orient the chamber so that the first field dimension is along the chamber longitudinal axis:
   - 4x15: 4 cm along chamber, 15 cm transverse;
   - 6x8: 6 cm along chamber, 8 cm transverse;
   - 8x10: 8 cm along chamber, 10 cm transverse.
7. Centre the chamber reference point on the beam central axis.
8. Allow temperature equilibrium; record temperature and pressure.

### 5.4 Acquire the water readings

For each Q:

1. After changing Q, make the normal warm-up/pre-irradiation exposure(s); do not count them.
2. Acquire **5 independent readings** using exactly the chosen irradiation setting.
3. Record raw charge, T, P and any applied correction factors.
4. Calculate the mean, standard deviation and coefficient of variation.
5. If one reading is visibly affected by an operational error, document the reason before excluding it; do not remove points only because they worsen agreement.

### 5.5 Build the RW3 point

1. Use the 30x30 cm RW3 stack and U19 holder.
2. Place PTW30013 horizontally on the central axis with the **same chamber orientation** used in water.
3. Geometry to chamber centre:
   - 13 mm RW3 above U19;
   - U19 H1 = 7 mm to chamber centre;
   - total physical depth = **20.0 mm**.
4. Keep approximately 10 cm RW3 downstream of the chamber centre.
5. Put the applicator in direct contact with the RW3 surface.
6. Set SSD to that RW3 surface: F40 = 40 cm, F50 = 50 cm.
7. Do not insert foil, paper, film or an air gap unless it is intentionally being investigated and recorded.

### 5.6 Acquire the RW3 readings

For each Q:

1. Use **the same irradiation setting** as the paired water measurement.
2. Acquire **5 independent readings**.
3. Record T and P independently from the water measurement.
4. Apply the same accepted correction chain.
5. Calculate mean, SD and CV.

### 5.7 Corrections used in the ratio

For each medium calculate a corrected reading:

`M_corr = M_raw * k_TP * k_s * k_pol * k_elec * ...`

Practical treatment:

- `N_D,w(Co)` is **not needed** for V_exp and cancels.
- `k_elec` cancels if the same electrometer/range is used, but keep it documented.
- `k_TP` must be applied separately to water and RW3 because T/P are measured at different times.
- `k_s` and `k_pol` should use the current accepted values for the relevant Q/measurement regime. They do not need to be remeasured for every repeat if already established.
- any known beam-output drift between the water and RW3 measurements must either be corrected by an independent monitor/reference or included as an uncertainty component.

### 5.8 Calculate the validation ratio

For each Q and geometry:

1. Calculate mean corrected reading in water: `Mbar_water`.
2. Calculate mean corrected reading in RW3: `Mbar_RW3`.
3. Calculate

   `V_exp = Mbar_water / Mbar_RW3`

4. Take the corresponding `V_MC` from `results/stage10a_mc_validation_targets.csv`.
5. Calculate

   `F = V_exp / V_MC`

   `Delta_V(%) = 100 * (F - 1)`

6. For diagnostic use only, an experimentally informed coefficient can be written as

   `K_hybrid = K_nominal * F`

   but **do not replace K_nominal by K_hybrid automatically**. A significant discrepancy first triggers investigation of setup/measurement/model consistency.

### 5.9 Repositioning experiment

To obtain a real setup component for Stage 10B, use at least one deliberately sensitive point:

- preferred primary point: **Q120, F40 4x15**.

Perform at least **3 independent complete rebuilds** of the setup. For each rebuild, acquire at least 3 readings. Use the between-setup dispersion as an empirical positioning/rebuild contribution.

If convenient, repeat the same check at Q150 F40 4x15, where Stage 9B showed the largest orientation sensitivity.

---

## 6. Readings

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

## 7. Experimental uncertainty and compatibility

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

## 8. What Stage 10A can and cannot conclude

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

## 9. Stage 10A deliverables

1. Completed orientation record for F40 4x15, F40 6x8 and F50 8x10 — **already closed and stored in data/stage10a_orientation_record.csv**.
2. Raw/corrected measurement table for water and RW3.
3. Experimental `V_exp` for all measured Q/g.
4. Existing-MC `V_MC` extracted from archived Stage 8S3d/8S3b point summaries — **no new transport required**.
5. `Delta_V`, uncertainty and z compatibility table.
6. Decision on which F40 orientation-specific K values map to the real clinical setup.
7. Measured setup/repositioning contribution for the final uncertainty budget.

After Stage 10A the next core task is Stage 10B: final uncertainty budget and clinical coefficient table.
