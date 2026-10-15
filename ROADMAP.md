# Project Roadmap

Single source of truth for the build plan, current status, and the gates between phases. Status date: **2026-10-15**.

## 1. Phase Plan

| ID | Item | Status | Acceptance / notes |
|---|---|---|---|
| D01 | Digital design & delivery | **DONE** | CAD, calculations, drawings, test-record templates |
| D02 | Physical measurement of materials & equipment | IN PROGRESS | Record sheet: `data/measurement_record_D02.md`; battery/connector measurements filled 2026-10-13, remaining items on arrival |
| D03 | Structural specimen testing | TODO | Load / deflection / permanent set; close out defects |
| D04 | Propulsion bench | TODO | Thrust, current, temperature rise, voltage drop, consistency |
| D05 | Whole-airframe dry fit, mass & CG | TODO | Update BOM and CG from real hardware |
| D06 | Electrical & lost-link checks | TODO | Three lost-link cases, bus loading, directions, range |
| D07 | Field & launch operations plan | TODO | School field permission, clearance, local requirements, assisted-launch verification |
| D08 | Unpowered glide trim | TODO | Judged by an experienced pilot |
| D09 | First powered flight | TODO | Short pattern, conservative timing, issue log |
| D10 | Three-flight acceptance | TODO | Close issues, roll design revision |
| D11 | 1400 mm version 2 | DEFERRED | Separate budget and design after the small version passes |
| F01 | Pico firmware debug levels 3–4 | **DONE** | Level 3 PASS 2026-10-07 (30-min soak, watchdog); level 4 PASS 2026-10-13 (MPU-6050 @ 200 Hz, 10-min log). Ladder continues as RX0/PWM0/... rows in `data/test_records.csv` |

## 2. Firmware Verification Ladder

The staged program is defined in `docs/debug_procedure.md` — no level starts until the previous one passes, and propellers stay off through level 8.

| Level | Scope | Status |
|---|---|---|
| 0 | Arrival inspection | Partially done (measurements on arrival, see D02) |
| 1 | Unpowered electrical checks | TODO |
| 2 | BEC and the 5 V bus | TODO |
| 3 | Pico minimal firmware (heartbeat, 1 ms tick, watchdog) | **PASS** 2026-10-07 |
| 4 | MPU-6050 IMU (WHO_AM_I, calibration, 200 Hz stream) | **PASS** 2026-10-13, 1 known issue |
| 5 | RP1 receiver and transmitter binding | TODO |
| 6 | Four-channel PWM output waveforms & buffer safety | TODO |
| 7 | Servos, mixing, stabilization direction | TODO |
| 8 | ESC and motor tests without propellers | TODO |
| 9 | Single-motor bench test with propeller | TODO |
| 10 | Twin motors and installed thrust | TODO |
| 11 | Fault injection (lost link, IMU loss, brownout) | TODO |
| 12 | Whole-airframe mechanics, weight & CG | TODO |
| 13 | Entry conditions for glide and powered flight tests | TODO |

## 3. Immediate Next Actions

1. Measure the delivered hardware: motor hole patterns, usable screw lengths, propeller shaft fit, and real dimensions of all purchased equipment; adapt the affected drawings. (D02 record sheet)
2. Build the motor saddles, main-spar bonded specimens, and the thrust test bench; test load capacity, thrust, current draw, and temperature rise.
3. Weigh the actual parts, dry-fit the airframe, fix the battery position, re-measure the CG, then close the structure.
4. Complete prop-off electrical / lost-link checks, radio checks, and unpowered glide trim; then a supervised first flight by an experienced pilot.
5. School field: permission, clearance, and people segregation must be confirmed separately — until then no field is treated as an approved flying site.

## 4. Known Issues Register

| # | Issue | Impact | Disposition |
|---|---|---|---|
| KI-1 | MPU-6050 accelerometer reads ~20% low (static \|a\| = 0.79–0.87 g vs expected 1.0 g); clone chip or residual effect of the earlier reverse-power incident | None on pitch/roll (ratio-based); gyro unaffected | Add a 1/0.80 scale correction in firmware before installation, or replace with a genuine GY-521 module |
| KI-2 | Dimensioned hole positions are nominal, not measured | CAD-to-part fit risk | Resolve in D02/D05 before final assembly |

## 5. Version 2 (1400 mm) Gate

The 1400 mm version does not start until the 600 mm prototype completes at least three controlled takeoffs and landings, all issues are closed, and the design is revised. It requires a fresh look at budget, transport size, field, aerodynamic layout, structure, propulsion, radio, and takeoff/landing method. The small version's shaping parameters and test experience carry over; the model and loads must not be scaled up directly. No version-2 procurement, model, or flight release exists today.
