# SR71-600 Control Board V1.1 — Wiring and Bring-Up Reference

Date: 2026-11-19. Board silkscreen: `SR71-600 主控板 V1.1 261821`, received bare (no parts fitted).
Design source: `D:\pcb-agent-teams\Projects\e1_power_dist_2s` (KiCad + fab release `20261021_000347`).
This note supersedes the perfboard sections of `hardware_checkin_guide.md`; the electrical netlist is unchanged from E1.

## 1. What the board is

The V1.1 board merges two things that were separate in the E1 paper design: the **battery power-distribution point** and the **flight-control logic**. That is why the measured continuity looks "wrong" at first:

- There are **two 5 V-class domains**: the 7.4 V battery bus (`BATT_P` / `BATT_N`) and the 5 V logic rail (`+5V` / `GND`).
- **There are two ground nets on the board.** `BATT_N` and `GND` are separate nets in the netlist; the PCB has only `GND` copper pours. They are joined **externally**, through the UBEC (input − ↔ output −) and through the ESCs' internal grounds.

`BATT_N` = J1.3, J2.2, J3.2, J4.2 (4 pins). `GND` = 34 pins (caps, Pico sockets, U1.7, U2.3, Q1.E, connector grounds).

**Before first power-up:** with the UBEC wired, measure `J4.2 (BATT_N) ↔ J5.2 (GND)`. It must read ~0 Ω. If it does not, the UBEC is isolated and a short link wire must be added, otherwise the logic ground floats.

## 2. Connector pinout (from `e1_power_dist_2s.net`)

### Power section

| Ref | Function | Pin 1 | Pin 2 | Notes |
|---|---|---|---|---|
| J1 | Battery, XT30(2+2) | — | — | **Pin 3 = BATT_N, pin 4 = BATT_P**; pins 1/2 are mechanical only |
| J2 | ESC-L power | BATT_P | BATT_N | 5.0 mm screw terminal |
| J3 | ESC-R power | BATT_P | BATT_N | 5.0 mm screw terminal |
| J4 | UBEC input | BATT_P | BATT_N | 5.0 mm screw terminal |
| J5 | UBEC output → board | +5V | GND | 5.0 mm screw terminal; the only 5 V source on the board |

### Logic and signals

| Ref | Function | Pins |
|---|---|---|
| J6 | Servo L | 1 = SV_L_PWM (after R3 220 Ω), 2 = +5V, 3 = GND |
| J7 | Servo R | 1 = SV_R_PWM (after R4), 2 = +5V, 3 = GND |
| J8 | ESC L signal | 1 = ESC_L_PWM (after R5), 2 = GND |
| J9 | ESC R signal | 1 = ESC_R_PWM (after R6), 2 = GND |
| J10 | RP1 receiver | 1 = +5V, 2 = GND, 3 = RP1 TX → U2.A, 4 = RP1 RX ← R1 1 k ← GP0 |
| J11 | MPU-6050 | 1 = +3V3, 2 = GND, 3 = SDA, 4 = SCL, 5 = INT (GP3) |
| J12 | Pico pins 1–20 | GP0, GP1, GND, GP2, GP3, GP4, GP5, GND, GP6–GP9, GND … |
| J13 | Pico pins 21–40 | GND ×4, 3V3(OUT) at pin 36, VSYS at pin 39 (tied to +5V) |

**IMU wiring trap:** the GY-521 module header is `VCC / GND / SCL / SDA / XDA / XCL / AD0 / INT`, while J11 is `3V3 / GND / SDA / SCL / INT`. Straight-across wiring swaps SDA and SCL. Correct mapping: board 1→module VCC, 2→GND, **3→module SDA (pin 4)**, **4→module SCL (pin 3)**, 5→module INT (pin 8).

## 3. Measurements taken on the bare board (2026-11-19)

Continuity only (no power applied), which confirmed the netlist:

| From | To | Result |
|---|---|---|
| J1 pin 3 (BATT_N) | J2 pin 2 | beep — power ground bus confirmed |
| J5 pin 2 | C2 "−" pad | beep — logic ground confirmed |
| J5 pin 1 | C2 "+" pad, U1 pin 14, J10 pin 1 | beep — 5 V rail confirmed |
| J1 pin 3 | J5 pin 2 | **open** — the two grounds are separate, by design |
| J1 pin 4 | C2 "+", U1 pin 14 | **open** — battery bus vs logic rail, by design |

C1/C2 polarity: the **round pad is positive** (the `+` silkscreen is beside it); the square pad is on the negative side, opposite to the usual "square = pin 1 = +" convention. Trust the silkscreen, not the pad shape.

## 4. Assembly notes and known blockers

| # | Item | Status / action |
|---|---|---|
| 1 | J2–J5 5.0 mm screw terminals (MX126-5.0-2P ×4) | Not purchased; either buy them or solder wires directly into the pads |
| 2 | J1 XT30(2+2)PB-M board connector | Buy, or solder two 18 AWG leads |
| 3 | **U2 socket is 1×5 SIP**, but the purchased SOT-23-5 adapter is dual-row | Options: (a) buy a SOT-23-5 → SIP-5 adapter; (b) dead-bug the LVC1G17 onto the five socket holes; (c) skip U2 and jumper J10.3 → J12.2 (RP1 is 3.3 V, direct is safe but loses the buffer) |
| 4 | R17/R18 | Do not populate (module already has I2C pull-ups) |
| 5 | Mass | Bare board ≈ 30 g (74.6 × 94.5 mm, 1.6 mm, 2 oz); assembled with Pico and terminals ≈ 60–70 g, i.e. ~1/3 of the 190.7 g budget — the main reason for the V2 redesign |
| 6 | No reverse-polarity protection | Check J1 polarity with a meter before every battery connection |

## 5. Solder order (when parts arrive)

1. Resistors R1–R16 (leave R17/R18 out) → Q1 → U1 (or its DIP-14 socket).
2. Capacitors: C4 10 µF, C3/C5/C6/C7 100 nF, then C1/C2 470 µF (`+` into the round pad).
3. Connectors: J2–J5 terminals → J6–J11 headers → J12/J13 sockets last.
4. After each group: check `+5V↔GND`, `+3V3↔GND`, `+5V↔+3V3` are all open.

First power-up (no battery, no modules): 5 V / 0.2 A into J5 (1 = +, 2 = −); idle current should be < 20 mA; with the Pico inserted, J11.1–J11.2 should read 3.3 V.
