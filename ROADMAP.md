# Project Roadmap

Single source of truth for the build plan, current status, and the gates between phases. Status date: **2026-10-21**.

## 1. Phase Plan

| ID | Item | Status | Acceptance / notes |
|---|---|---|---|
| D01 | Digital design & delivery | **DONE** | CAD, calculations, drawings, test-record templates |
| D02 | Physical measurement of materials & equipment | IN PROGRESS | Record sheet: `data/measurement_record_D02.md`; battery/connector measurements filled 2026-10-13; capacitors measured 2026-10-20 (C3 = 49 nF, retained); remaining items on arrival |
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
| F02 | Pico firmware debug level 6 (four-channel PWM) | FIRMWARE COMPILED | Compiled 2026-10-19 (`firmware/level6_pwm/`), flash + logic-analyzer verification on the Pico pin side still pending — see `docs/debug_log_2026-10-19.md` |
| P01 | E1 power-distribution PCB (v2 board) | **ORDERED** | Designed and verified 2026-10-20/21 (ERC 0, 27/27 net match, DRC 0/0, dual release review); ordered from JLC 2026-10-21 (5 boards, ~CNY 150–250, ETA 5–7 days) — see `pcb/e1_power_dist_2s/` and `docs/log_2026-10-21_e1_pcb.md` |

## 2. Firmware Verification Ladder

The staged program is defined in `docs/debug_procedure.md` — no level starts until the previous one passes, and propellers stay off through level 8.

| Level | Scope | Status |
|---|---|---|
| 0 | Arrival inspection | Partially done (measurements on arrival, see D02) |
| 1 | Unpowered electrical checks | TODO |
| 2 | BEC and the 5 V bus | TODO |
| 3 | Pico minimal firmware (heartbeat, 1 ms tick, watchdog) | **PASS** 2026-10-07 |
| 4 | MPU-6050 IMU (WHO_AM_I, calibration, 200 Hz stream) | **PASS** 2026-10-13, 1 known issue |
| 5 | RP1 receiver and transmitter binding | TODO (radio system not yet delivered) |
| 6 | Four-channel PWM output waveforms & buffer safety | Firmware compiled 2026-10-19; flash + logic-analyzer verification pending |
| 7 | Servos, mixing, stabilization direction | TODO |
| 8 | ESC and motor tests without propellers | TODO |
| 9 | Single-motor bench test with propeller | TODO |
| 10 | Twin motors and installed thrust | TODO |
| 11 | Fault injection (lost link, IMU loss, brownout) | TODO |
| 12 | Whole-airframe mechanics, weight & CG | TODO |
| 13 | Entry conditions for glide and powered flight tests | TODO |

## 3. Immediate Next Actions

Board bring-up (milestone B), firmware verification, and PCB assembly prep are running in parallel while waiting for deliveries:

1. **When the PCB arrives (≈5–7 days from 2026-10-21)**: work through the per-refdes assembly checklist; multimeter check that BATT+/− is isolated from 5V/GND before populating; solder order resistors → small capacitors → electrolytic → DIP-14 socket → Pico headers → pin headers → XT30/terminals; leave R17/R18 unpopulated.
2. **Perfboard photo review**: GND bus + C2/C3 solder joints (focus: C2 electrolytic polarity — reversed polarity under power will burst it). Once passed, solder the resistors, pin headers, C6, and the DIP-14 sockets → insert the AHCT125 → multimeter recheck (no 5 V–GND short, OE_N ≈ 5 V, all four Y ≈ 0 V) → close out milestone B; solder Q1 with the arrived LCSC parts.
3. **Level-6 firmware**: flash `sr71fc_level6.uf2` and run the logic-analyzer pre-verification on the Pico pin side (checklist in `firmware/README.md`) — needs no radio.
4. **Radio system**: order the RadioMaster Pocket (**ELRS version, not multi-protocol**) + RP1 V2 (~CNY 450). When the receiver arrives: level 7 (CRSF link); macro-photo U2's pin-1 marking before soldering it anywhere.
5. **Battery**: smell re-check + first-charge health inspection once the replacement charger arrives; measure the delivered hardware (motor hole patterns, screw lengths, propeller shaft fit) and adapt the affected drawings.

## 4. Known Issues Register

| # | Issue | Impact | Disposition |
|---|---|---|---|
| KI-1 | MPU-6050 accelerometer reads ~20% low (static \|a\| = 0.79–0.87 g vs expected 1.0 g); clone chip or residual effect of the earlier reverse-power incident | None on pitch/roll (ratio-based); gyro unaffected | Add a 1/0.80 scale correction in firmware before installation, or replace with a genuine GY-521 module |
| KI-2 | Dimensioned hole positions are nominal, not measured | CAD-to-part fit risk | Resolve in D02/D05 before final assembly |
| KI-3 | C3 measures ~49 nF vs 100 nF nominal (measured 2026-10-20); C2 not yet measured individually | None — adequate as decoupling, retained | Re-measure C2 across the two buses on the 2000 µF range (expected 400–550 µF) at the next board session |
| KI-4 (resolved) | Hardware check-in guide §5.4 listed the U2 (SN74LVC1G17) pin order shifted by one pin | None — U2 not yet soldered | Corrected 2026-10-21 in both the English guide and the Chinese original: 1=NC, 2=A, 3=GND, 4=Y, 5=VCC; verify against the datasheet before soldering |

## 5. Version 2 (1400 mm) Gate

The 1400 mm version does not start until the 600 mm prototype completes at least three controlled takeoffs and landings, all issues are closed, and the design is revised. It requires a fresh look at budget, transport size, field, aerodynamic layout, structure, propulsion, radio, and takeoff/landing method. The small version's shaping parameters and test experience carry over; the model and loads must not be scaled up directly. No version-2 procurement, model, or flight release exists today.
