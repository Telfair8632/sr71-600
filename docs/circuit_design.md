# SR-71 / 600 V1 Complete Circuit Design

Version: E1, 2026-09-30. Applies to: 2S battery, two EX1103 motors, two independent brushless ESCs, Pico 2, RP1 V2, MPU6050, two ES9051 servos, and a 5V UBEC.

This is not a certified production flight controller; it is the solderable control and power circuit for the first prototype. Do not fit propellers to the motors until the prop-off testing, throttle lockout, and control-surface direction checks have all passed.

Companion drawing: `electronics/wiring_diagram_E1.svg`; print version: `docs/circuit_design_E1.pdf`.

## 1. Overall Architecture

The battery feeds a three-way power distribution point: the left ESC, the right ESC, and the UBEC input each take one way. Motor current never passes through the perfboard, the Pico, or the servo connectors. The UBEC's 5V output then splits into a servo branch and a logic branch; the two branches take separate leads from the same 5V star point, but all grounds end up common.

```text
2S LiPo / XT30
  ├─ ESC-L ─ Motor L
  ├─ ESC-R ─ Motor R
  └─ 5V UBEC ─ 5V star point ─┬─ left/right servos
                              └─ Pico, RP1, AHCT125, MPU6050
```

An ESC's three-wire signal lead connects only `SIGNAL` and `GND`. If the ESC carries a BEC, the red 5V wire must be depinned from the connector and insulated separately with heat-shrink; the completed aircraft allows only the UBEC to power the 5V bus.

## 2. Power and Capacitors

| Node | Connects to | Wire/installation requirements |
|---|---|---|
| BATT+ / BATT- | XT30, both ESC power inputs, UBEC input | Use a soldered star point or a small PDB; battery main leads 18-20AWG, ESC branches 20-22AWG; keep the battery-to-ESC DC leads as short as possible |
| 5V_STAR | Distribution point of the UBEC output | Each servo gets its own dedicated 24-26AWG positive/negative pair; the logic board gets a separate 26-28AWG pair |
| 5V_SERVO | Positive/negative leads of the two servos | At the distribution point parallel C1: 470uF/10V low-ESR, capacitor positive to 5V, negative to GND |
| 5V_LOGIC | Pico VSYS, RP1, AHCT125 | At the perfboard entry parallel C2: 470uF/10V low-ESR and C3: 0.1uF ceramic |
| 3V3 | Pico `3V3(OUT)`, MPU6050, U2 | Must not connect to the servos, the RP1, or the 5V pins of the AHCT125; near the MPU6050 parallel C4: 10uF/25V and C5: 0.1uF |

UBEC requirements: the input must reach down to about 6.0V at the end of 2S discharge; the output is fixed 5V or regulated at 5V; 3A continuous is the floor and 5A gives margin; the output must not exceed 5.25V. Two small digital servos draw large short-duration currents when stalled or thrown rapidly to full deflection, so before any propeller goes on, run a "both servos sweeping full travel repeatedly + receiver + Pico" voltage-sag test; 5V must not fall below 4.75V and the Pico must not reboot.

A `10uF/25V` cannot replace a 470uF low-ESR part. The former handles high-frequency minor disturbances; the latter handles the transient voltage dip caused by sudden servo current. If an ESC's battery input lead is stretched past 100mm during installation, add a suitably rated low-ESR electrolytic capacitor across its input per the purchased ESC's manual; capacitors on the 2S power bus must be rated at least 16V — do not substitute 10V parts.

## 3. Pico 2 Pins and Signal Circuits

| Pico pin | Connection | Function |
|---|---|---|
| GP0 / UART0 TX | Through R1 1k to RP1 `RX` | Sends CRSF telemetry to the receiver; recommended to keep even if the receiver has no telemetry requirement |
| GP1 / UART0 RX | U2 output | Receives CRSF control data from RP1 `TX` |
| GP2 | Through R2 4.7k to the Q1 base | The sole hardware enable signal; all four outputs are permitted only when it is high |
| GP3 | MPU6050 `INT` | Data-ready interrupt |
| GP4 | MPU6050 `SDA` | I2C0 data |
| GP5 | MPU6050 `SCL` | I2C0 clock |
| GP6 | U1-1A (pin 2) | Left servo PWM |
| GP7 | U1-2A (pin 5) | Right servo PWM |
| GP8 | U1-3A (pin 9) | Left ESC PWM |
| GP9 | U1-4A (pin 12) | Right ESC PWM |
| VSYS | 5V_LOGIC | Pico board-level power input; never connect to the 3V3 pin |
| 3V3(OUT) | MPU6050 and U2 VCC | Serves only as the low-current 3.3V logic supply |
| GND | All signal grounds | Must be common with 5V and the power negative return |

### Receiver Serial Protection U2

`U2 = SN74LVC1G17`, on an SOT-23-5-to-DIP adapter board: VCC to 3V3, GND to ground, A to RP1 TX, Y to Pico GP1. This device's inputs tolerate up to 5.5V while its output follows its 3.3V supply, so even if the RP1 TX measured high level exceeds 3.6V, Pico GP1 only ever sees 3.3V logic. A 0.1uF capacitor must sit next to U2.

RP1 RX is driven directly from Pico GP0 through R1 (1k). The RP1 uses CRSF full-duplex UART: RP1 TX must go to Pico RX, and RP1 RX to Pico TX. The receiver's 5V and GND must also be connected. Before the first power-up, use a multimeter to confirm RP1 TX is not shorted to ground; after power-up, measure its static high level and record it in the debug sheet.

### MPU6050

Power the MPU6050 module from 3V3 only — never 5V. If the module lacks on-board pull-ups, add 4.7k from each of SDA/SCL to 3V3; if it already has them, do not parallel a second set. The I2C bus must never be pulled up to 5V. Mount the MPU6050 firmly near the airframe center of gravity with the sensor axes aligned to the body axes, and keep it away from the UBEC, the ESCs, and high-current power leads.

## 4. Four 5V PWM Outputs and the Hardware Fail-Safe

`U1 = SN74AHCT125N`: pin 14 to 5V_LOGIC, pin 7 to GND, with C6 0.1uF beside pins 14 and 7.

| U1 channel | A side (from Pico) | Y side (to device) | Output wiring |
|---|---|---|---|
| 1 | pin 2 ← GP6 | pin 3 → left servo signal | R3 220Ω in series on Y; R7 10k pulls down to GND on the connector side |
| 2 | pin 5 ← GP7 | pin 6 → right servo signal | R4 220Ω in series on Y; R8 10k pulls down to GND on the connector side |
| 3 | pin 9 ← GP8 | pin 8 → left ESC signal | R5 220Ω in series on Y; R9 10k pulls down to GND on the connector side |
| 4 | pin 12 ← GP9 | pin 11 → right ESC signal | R6 220Ω in series on Y; R10 10k pulls down to GND on the connector side |

All four U1 enable pins (1, 4, 10, 13) tie together as `OE_N` and are pulled up to 5V_LOGIC by R11 (10k). `Q1` is a 2N3904, S8050, or similar NPN: emitter to GND, collector to OE_N, base to Pico GP2 through R2 (4.7k), and base also to GND through R12 (10k).

| State | GP2 | Q1 | OE_N | U1 outputs |
|---|---:|---|---|---|
| Unpowered, Pico reset, firmware crash | Floating or low | Off | Pulled to 5V by R11 | High impedance; all four signals held low by R7-R10 |
| Self-test passed and a safe low-throttle frame received | High | On | Low | All four PWM outputs enabled |
| Lost link, sensor error, watchdog error | Firmware drives GP2 low | Off | High | Outputs disabled |

This is more reliable than tying OE directly to 3.3V: when the UBEC or the AHCT125 starts before the Pico, U1 is still held off by the 5V pull-up. The firmware must also hold GP2 low before it starts sending PWM and clamp both ESC commands to minimum throttle.

To keep the Pico's unconfigured pins from floating, each of U1's four A-side pins (2, 5, 9, 12) gets a 10k pull-down to GND (R13-R16). That brings the required 10k count to ten: four A-side pull-downs, four Y-side pull-downs, one OE pull-up, and one Q1 base pull-down.

## 5. Perfboard Layout and Harness Rules

Populate the perfboard from left to right: the 5V/GND input end and C2 → the Pico socket → U2 and the RP1 socket → U1 and Q1 → the four output connector groups. Run 5V and GND as one continuous thick tinned-copper bus bar each; the power battery leads never enter the perfboard.

* Place the UBEC, ESCs, and motors in the nacelles; place the Pico, MPU6050, and RP1 in the forward bay.
* The two motor phase leads may be extended; keep the battery-to-ESC positive/negative leads parallel, short, and away from the MPU6050 and the RP1 antenna.
* Every PWM lead must be routed as a pair with a GND lead, especially the leads going to the two ESCs.
* Keep the RP1 antenna ends straight and at least 30mm away from carbon tubes, the UBEC, the motors, and the ESCs; route the two antennas roughly 90 degrees apart.
* Label both ends of every connector lead: `S-L`, `S-R`, `ESC-L`, `ESC-R`, `RX`, `IMU`. Identify with heat-shrink first, then solder permanently.

## 6. Soldering Order and First Checks

1. Solder the 5V/GND bus bars, U1, Q1, U2, and all resistors and capacitors first — do not attach the Pico, RP1, IMU, servos, or ESCs yet.
2. On the multimeter continuity range, confirm 5V-GND, 3V3-GND, and BATT+-BATT- are not shorted; confirm the polarity of both 470uF capacitors.
3. Feed the UBEC input from a current-limited power supply at 7.4V, 0.2A; confirm 5V is 4.75-5.25V, then confirm Pico 3V3 is 3.20-3.35V.
4. Plug in the Pico and confirm: with no firmware running, U1's OE_N sits near 5V and the four Y pins sit near 0V — that is the hardware lockout behaving correctly.
5. Connect only the RP1 and the MPU6050 and confirm CRSF frames and I2C identification. Do not connect the ESCs at this point.
6. Connect one servo; have the firmware output 50Hz with small throws and check direction; then connect the second servo.
7. Connect both ESCs with no propellers mounted and calibrate minimum throttle first. On radio lost link, receiver unplugged, and Pico reset, confirm GP2 returns low, OE_N returns high, and both ESCs stop.
8. Finish with the 5V sag test: both servos sweeping back and forth and both ESCs running at low throttle. Only after it passes may propellers go on for the powertrain bench.

## 7. Parts To Add or Update in Procurement

Beyond the original plan, the complete circuit adds the following small parts:

| Part | Qty | Function |
|---|---:|---|
| SN74LVC1G17DBV + SOT-23-5-to-DIP adapter board | 1 set | 3.3V-safe input buffer from RP1 TX to Pico RX |
| 2N3904 or S8050 NPN transistor | 1 | Hardware enable switch for U1 |
| 220Ω resistors | 4 | Series current limiting on the four PWM outputs |
| 1kΩ resistor | 1 | Series protection from Pico TX to RP1 RX |
| 4.7kΩ resistors | 3 | One in series with the Q1 base; two for I2C external pull-ups if needed |
| 10kΩ resistors | 10 | Default states of the U1 inputs/outputs and the hardware fail-safe |

Flight safety of the completed aircraft still requires software lost-link protection, a watchdog, IMU mounting-orientation confirmation, ground vibration checks, and progressive flight testing. This circuit aims to drive down the hardware risk of "motors spinning when the Pico resets or has not booted"; it cannot replace those verifications.
