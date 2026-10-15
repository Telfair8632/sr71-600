# Hardware Check-In and Circuit Assembly Guide

Date: 2026-10-01. Applies to: control circuit E1 (see `circuit_design.md`).
This document changes nothing in the original design; it does three things: verify the physical parts on hand, list the gaps, and land the circuit on specific solder points of the perfboard.
All test gates follow `debug_procedure.md`; where the two conflict, the debug procedure prevails.

## 1. Arrival Check-In Table

| Item | Status | Circuit role | On-arrival to-dos |
|---|---|---|---|
| Pico 2 | Arrived | Main controller | Confirm the USB cable carries data (not charge-only) |
| Capacitors (470µF low-ESR ×2, 0.1µF, 10µF) | Verified consistent | C1–C6 | Measure capacitance and electrolytic polarity of each unit before board-up |
| SN74AHCT125N ×1 | Arrived | U1, four-channel PWM buffer | — |
| MPU-6050 ×1 | Arrived | Attitude sensor | Confirm the INT pin is broken out; record the module's measured mass |
| Single-sided tinned perfboard | Arrived | Carrier board | Pick one at least 5×7 cm |
| 24M 8-channel logic analyzer | Arrived | Debug instrument | 24Msps is sufficient for 400kHz I2C / CRSF / 50Hz PWM |
| ES9051 servos ×2 | Arrived (new purchase) | Left/right elevons | Check authenticity, 4.0–5.5V range, **connector pitch** (EMAX micro servos are mostly JST 1.0mm; if so, the board-edge headers need 1.0→2.54 adapter leads) |
| UBEC 5V/6A | Arrived (new purchase) | Sole source of the 5V bus | On power-up, measure output ≤5.25V and confirm 2S input support; 6A is more generous than the 3A design requirement, leaving more margin in the dual-servo stall sag test |
| KV11000 motors ×4 | To be verified | Powerplant (2 installed, 2 spare) | **Must confirm EX1103 spec**: about 3.8g, 1.5mm shaft, 2-inch prop mount; measure hole spacing and usable screw length. If not EX1103-class, the motor-mount STLs, thrust data, and weight budget are all recalculated |
| 2S 800mAh battery | To be measured | Powerplant | Weigh it (target ≤55g, the basis used by the 52g assessment document), burst current ≥25A (twin-motor peak about 18.4A), whether the dimensions fit the battery bay, and which discharge connector it ships with |

## 2. Still To Buy

### 2.1 Electronics (power and radio testing cannot start without them)

| Part | Qty | Budget (CNY) | Key points |
|---|---:|---:|---|
| Brushless ESC, 15–20A, 2S, ordinary PWM, no BEC | 2 | 180 | First choice AGFRC XR-20A, see `esc_candidates.md`; before ordering, send the seller the confirmation wording at the end of that document |
| Receiver RadioMaster RP1 V2 (ELRS 2.4G) | 1 | 150 | Must share protocol and band with the transmitter |
| Transmitter RadioMaster Pocket (ELRS 2.4G) | 1 | 650 | Ground equipment |
| 2-inch props, 2023-series CW/CCW pair | 1 pair + spares | 60 | Fitted only at the bench stage; not buying them now blocks none of the earlier tests |
| Small parts: SN74LVC1G17 + SOT-23-5-to-DIP adapter board, 2N3904 (or S8050), resistors 220Ω×4 / 1k×1 / 4.7k×3 / 10k×10, XT30 ×2 pairs, silicone wire 18/20/26AWG, heat-shrink | 1 set | 60 | Semiconductors from LCSC (C22469943, C124482), consumables from Taobao; combine each into one order to save shipping |
| 2S balance charger | 1 | 350 | **Must be on hand before the battery's first charge**; an 800mAh 2S must never be direct-charged without balancing. New packs ship about half-charged, enough for early ground debugging, but charging must work before the powertrain bench — if bought in stages, the charger arrives no later than the ESCs |

### 2.2 Airframe Materials (does not block ground electronics testing; must arrive before final assembly)

3mm paperless foam (main wing / fuselage), 2mm foam (nacelle cosmetics), 4×2mm carbon tube 380mm, 2mm carbon rod 215mm ×2, 1mm thin plywood, foam adhesive / CA (502), control horns, pushrods, hinge tape, light finish.
Eight 3D-printed parts (STLs in `print/`); arrange a printing channel, printed in PETG.

### 2.3 Tools (if not already owned)

Multimeter (required — many checks depend on it), temperature-controlled iron + solder + flux, data-capable USB cable; a power meter and a small electronic scale are recommended additions (needed for the thrust bench and weigh-ins).

## 3. Concept To Establish First: Four "Islands"

The circuit is four islands that join into **one common ground** only at the battery distribution point:

1. **Power island**: battery XT30 → ESCs ×2 → motors ×2. **The large currents never enter the perfboard**; the ESC power leads solder straight to the battery distribution point.
2. **5V island**: UBEC input at the battery distribution point → 5V star point at the output → splits into two branches: the two servos and the logic board.
3. **3V3 island**: derived from the Pico's 3V3(OUT), feeding only the MPU6050 and U2. **Never connected to 5V.**
4. **Signal island**: all PWM/I2C/UART signals on the board; every signal lead is routed as a pair with a GND lead.

## 4. Perfboard Layout (about 5×7 cm, single-sided)

```text
              ┌──────────────────────────────────────────────────────┐
 5V input ○──┤ [C2 470µF][C3 0.1µF]                                 │
 UBEC +/−    │ ═══════ 5V bus ════════════════════════════════       │
             │ ═══════ GND bus ═══════════════════════════════       │
             │              ┌────────────┐     ┌───────────┐        │
 RP1 socket ○┤ [U2 adapter] │ Pico 2     │     │ U1        │ [C6]   │
 3-pin (+5V/ │              │ socket     │     │ AHCT125N  │        │
  GND/TX)    │              └────────────┘     └───────────┘        │
             │ [Q1][R2][R12]     [R3–R6 220Ω] [R7–R10 10k pulldn]   │
             │  ▲ OE_N network (R11 10k pull-up)                    │
 Servo L ○   │  [header: signal/5V/GND]                             │
 Servo R ○   │  [header: signal/5V/GND]                             │
 ESC L   ○   │  [header: signal/GND]                                │
 ESC R   ○   │  [header: signal/GND]                                │
             └──────────────────────────────────────────────────────┘
```

Principles (matching `circuit_design.md` §5): one continuous thick tinned-copper rail each for 5V and GND, spanning the board; C2 near the 5V entry, C6 tight against U1 pins 14/7, 0.1µF beside U2; the four output header groups at the board edge; the RP1 is socketed, not soldered direct (antenna placement rules apply when the receiver goes into the airframe).

## 5. Pin-Level Wiring Tables

### 5.1 Pico 2 (physical pin numbers; Pico 2 and Pico 1 pins are compatible)

| Physical pin | GPIO | Connects to |
|---:|---|---|
| 1 | GP0 / UART0 TX | Through R1 1k → RP1 RX |
| 2 | GP1 / UART0 RX | Y of U2 |
| 4 | GP2 | Through R2 4.7k → Q1 base |
| 5 | GP3 | MPU6050 INT |
| 6 | GP4 | MPU6050 SDA |
| 7 | GP5 | MPU6050 SCL |
| 9 | GP6 | U1 pin 2 (1A) |
| 10 | GP7 | U1 pin 5 (2A) |
| 11 | GP8 | U1 pin 9 (3A) |
| 12 | GP9 | U1 pin 12 (4A) |
| 36 | 3V3(OUT) | MPU6050 VCC, U2 VCC, top end of the I2C pull-ups |
| 39 | VSYS | 5V_LOGIC (UBEC 5V arriving via the bus) |
| 3/8/13/18/23/28/33/38 | GND | GND bus |

### 5.2 U1 = SN74AHCT125N (DIP-14, notch to the left)

| Pin | Name | Connects to |
|---:|---|---|
| 14 / 7 | VCC / GND | 5V_LOGIC / GND bus; C6 0.1µF tight against these two pins |
| 1, 4, 10, 13 | 1OE̅–4OE̅ | Tied together as OE_N: R11 10k pull-up to 5V_LOGIC; also to the Q1 collector |
| 2 / 5 / 9 / 12 | 1A–4A | GP6 / GP7 / GP8 / GP9; each pin also gets R13–R16 10k pull-down to GND |
| 3 / 6 / 8 / 11 | 1Y–4Y | Each through R3–R6 220Ω to the output header signal pin; R7–R10 10k pull-down to GND on the header side |

### 5.3 Q1 = 2N3904 (TO-92, flat face toward you, order E/B/C; varies by manufacturer — the datasheet rules)

| Pin | Connects to |
|---|---|
| E emitter | GND |
| C collector | OE_N |
| B base | R2 4.7k ← Pico GP2; R12 10k → GND |

### 5.4 U2 = SN74LVC1G17 (SOT-23-5: 1=A, 2=GND, 3=Y, 4=NC, 5=VCC; datasheet rules)

| Pin | Connects to |
|---|---|
| A | RP1 socket TX pin |
| Y | Pico GP1 |
| VCC | 3V3 (0.1µF alongside) |
| GND | GND bus |

### 5.5 MPU6050 (GY-521-type 8-pin module)

VCC→3V3; GND→GND; SDA→GP4; SCL→GP5; INT→GP3; XDA/XCL/AD0 left unconnected (AD0 floating gives address 0x68).
If the module has no on-board pull-ups: add 4.7k from each of SDA/SCL to 3V3; if pull-ups already exist, do not add more. Pull-ups to 3V3 only.

### 5.6 Board-Edge Connectors

| Connector | Pin definition | Notes |
|---|---|---|
| Servo L / Servo R | Signal (after 220Ω) / +5V / GND | Use adapter leads if the ES9051 has a 1.0mm connector |
| ESC L / ESC R | Signal (after 220Ω) / GND | Signal and ground only; if the ESC's third wire carries BEC 5V, it must be depinned and insulated with heat-shrink (the UBEC is the aircraft's only 5V source) |
| RP1 socket | +5V / GND / RP1 TX→U2.A / U2 side back to RP1 RX (through R1) | Antenna at least 30mm from carbon tubes, the UBEC, and the ESCs; the two antennas about 90° apart |
| 5V input | UBEC output +/− | The board's only 5V source |

## 6. Soldering Order (four stages keyed to arrival milestones)

**Milestone A — doable right now, zero solder joints required:**

1. Pico minimal firmware (debug procedure §3): LED, USB logging, 1ms tick, watchdog; run 30 minutes straight.
2. Direct MPU6050 hookup (debug procedure §4): five Dupont jumper wires straight from Pico to IMU (3V3, GND, GP4, GP5, GP3), USB power; hang the logic analyzer on SDA/SCL/INT to view the 400kHz waveforms; read WHO_AM_I=0x68; 10-minute data log.
3. Measure the on-arrival to-dos: weigh the battery, verify the motor spec, measure the UBEC output voltage.

**Milestone B — after the small parts arrive:**

4. Solder per the §4 layout: bus rails → C2/C3 → U1 socket, Q1, U2 adapter board, all resistors and capacitors. Leave the chips unplugged for now.
5. Multimeter checks: no shorts on 5V–GND or 3V3–GND; both 470µF polarities correct; continuity of the OE_N network to the Q1 collector and to the R11 top end.
6. Plug in U1 only (no Pico): OE_N ≈ 5V and the four Y pins ≈ 0V — the hardware lockout is healthy.

**Milestone C — UBEC in hand and Pico firmware ready:**

7. Feed the UBEC input from a current-limited supply at 7.4V / 0.2A; measure the output at 4.75–5.25V; then bring in the Pico and the board logic step by step, re-measuring voltage and current at each level.
8. Plug in the Pico for the waveform stage (debug procedure §6): logic analyzer on the four outputs — no pulses before arming; after the self-test passes, servos at 50Hz / 1500µs and ESCs at 50Hz / 1000µs; pressing reset must shut the outputs off immediately with no wide-pulse glitch.

**Milestone D1 — after the servos, receiver, and transmitter arrive (the ESCs can catch up later):**

9. Enter debug procedure §5–§7: CRSF link and lost-link detection, servo direction and mixing, stabilization direction checks, dual-servo sag test. No ESCs and no propellers throughout. With the servos and UBEC already on hand, this milestone waits only for the receiver and transmitter.

**Milestone D2 — after the ESCs arrive:**

10. Enter debug procedure §8–§10: prop-off ESC calibration, single-motor bench, twin-motor installed thrust. Before this point, never let the motor wiring carry a propeller, and run no power test of any kind.

## 7. Red Lines (violation means rework, no exceptions)

- The high-current leads of the battery, ESCs, and motors never enter the perfboard.
- 5V never connects to 3V3; I2C pull-ups go to 3V3 only.
- The whole board shares one ground; the power negative return ties to control ground at the battery distribution point.
- Before any propeller goes on: lost-link protection, Pico reset protection, and the dual-servo + logic sag test must all pass.
- Charge the battery only with a balance charger; before connecting the battery, confirm polarity and the absence of shorts with a multimeter.
