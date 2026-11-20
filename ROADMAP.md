# Project Roadmap

Single source of truth for the build plan, current status, and the gates between phases. Status date: **2026-11-19**.

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
| P01 | E1 power-distribution PCB (V1.1 board) | **RECEIVED** | Designed/verified 2026-10-20/21, ordered 2026-10-21, **received 2026-11-19**. Bare-board continuity verified against the netlist; two separate grounds confirmed (`BATT_N` vs `GND`, joined externally through the UBEC). Three items still missing before assembly (4 × 5.0 mm terminals, XT30 board connector, 1×5 SIP adapter for U2). Becomes the bench board — see `docs/pcb_v1_1_wiring.md` |
| P02 | SMD flight-control board V2 (`sr71_ctrl_v2`) | **DESIGNED** | 65 × 85 mm, 1.0 mm, 1 oz, 37 SMD parts, 25 nets routed, DRC 0/0; hand-soldering reduced to 2 pads (XT30 power entry). Not ordered — LCSC part numbers and CPL format to finish. See `pcb/sr71_ctrl_v2/`, `docs/pcb_v2_smd_design.md` |

## 2. Firmware Verification Ladder

The staged program is defined in `docs/debug_procedure.md` — no level starts until the previous one passes, and propellers stay off through level 8.

| Level | Scope | Status |
|---|---|---|
| 0 | Arrival inspection | Partially done (measurements on arrival, see D02) |
| 1 | Unpowered electrical checks | TODO |
| 2 | BEC and the 5 V bus | TODO |
| 3 | Pico minimal firmware (heartbeat, 1 ms tick, watchdog) | **PASS** 2026-10-07 |
| 4 | MPU-6050 IMU (WHO_AM_I, calibration, 200 Hz stream) | **PASS** 2026-10-13; scale correction added to firmware 2026-11-19 (re-check `\|a\|` only) |
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

The V1.1 board is on the bench; the V2 SMD board is designed and waiting for an order. In parallel:

1. **V1.1 board (bench)**: buy the three missing items (4 × 5.0 mm terminal blocks, XT30 board connector, 1×5 SIP adapter for U2, or jumper J10.3→J12.2 and skip U2), then solder in the order resistors → capacitors → connectors → Pico sockets. Before first power: `J4.2 ↔ J5.2` must read ~0 Ω (the two grounds join through the UBEC), and C1/C2 must be fitted with `+` on the round pad.
2. **V2 board (flight)**: add LCSC part numbers to `pcb/sr71_ctrl_v2/fab/assembly/bom_sr71_ctrl_v2.csv`, check the CPL orientation in the JLCPCB uploader, then order 5 boards (1.0 mm, 1 oz, single-side SMT).
3. **Level-6 firmware**: flash `sr71fc_level6.uf2` and run the logic-analyser pre-verification on the Pico pin side (checklist in `firmware/README.md`) — needs no radio. The UF2 was rebuilt and verified byte-identical on 2026-11-19.
4. **Radio system**: order the RadioMaster Pocket (**ELRS version, not multi-protocol**) + RP1 V2. When the receiver arrives: level 5 (CRSF link).
5. **Level 4 re-check**: flash the corrected level-4 build and confirm `|a| ≈ 1.0 g` (the other six criteria already passed).

## 4. Known Issues Register

| # | Issue | Impact | Disposition |
|---|---|---|---|
| KI-1 | MPU-6050 accelerometer reads ~20% low (static \|a\| = 0.79–0.87 g vs expected 1.0 g); clone chip or residual effect of the earlier reverse-power incident | None on pitch/roll (ratio-based); gyro unaffected | **Mitigated 2026-11-19**: ×1.25 (1/0.80) scale correction added to `firmware/level4_imu/main.c` and the UF2 rebuilt; re-check `\|a\| ≈ 1.0 g`. Revert to 1.0 if the module is replaced with a genuine GY-521 |
| KI-2 | Dimensioned hole positions are nominal, not measured | CAD-to-part fit risk | Resolve in D02/D05 before final assembly |
| KI-3 | C3 measures ~49 nF vs 100 nF nominal (measured 2026-10-20); C2 not yet measured individually | None — adequate as decoupling, retained | Re-measure C2 across the two buses on the 2000 µF range (expected 400–550 µF) at the next board session |
| KI-4 (resolved) | Hardware check-in guide §5.4 listed the U2 (SN74LVC1G17) pin order shifted by one pin | None — U2 not yet soldered | Corrected 2026-10-21 in both the English guide and the Chinese original: 1=NC, 2=A, 3=GND, 4=Y, 5=VCC; verify against the datasheet before soldering |
| KI-5 | V1.1 board's U2 footprint is a 1×5 SIP socket, while the purchased SOT-23-5 adapter is dual-row and cannot plug in | U2 (receiver buffer) cannot be fitted as planned | Buy a SOT-23-5 → SIP-5 adapter, dead-bug the chip onto the socket holes, or bypass U2 with a wire between J10.3 and J12.2 (RP1 is 3.3 V; loses the buffer) |
| KI-6 | V1.1 still lacks 4 × 5.0 mm terminal blocks (J2–J5) and the XT30 board connector (J1) | Board cannot be wired up yet | Order them, or solder wires directly into the through-hole pads |
| KI-7 | V1.1 assembled mass ≈ 60–70 g against a 190.7 g aircraft budget (bare board ≈ 30 g) | Mass margin almost exhausted | V2 SMD board (P02) reduces the bare board to ≈14 g and the assembled board to ≈31 g; the electronics mass budget in the BOM should be re-baselined |

## 5. Version 2 (1400 mm) Gate

The 1400 mm version does not start until the 600 mm prototype completes at least three controlled takeoffs and landings, all issues are closed, and the design is revised. It requires a fresh look at budget, transport size, field, aerodynamic layout, structure, propulsion, radio, and takeoff/landing method. The small version's shaping parameters and test experience carry over; the model and loads must not be scaled up directly. No version-2 procurement, model, or flight release exists today.
