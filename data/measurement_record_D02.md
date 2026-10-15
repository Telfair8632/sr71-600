# D02 Physical Measurement Record Sheet (companion to commissioning workflow level 0: arrival inspection)

Purpose: replace the nominal values from the digital design with the real values of this batch of physical parts on hand.
After measuring, backfill the key conclusions into the MASS and FIT rows of `data/test_records.csv` and report them to ZCode so the design can be updated.
**Non-conforming parts must not proceed to soldering** — measure first, then install.

Measuring tools: electronic scale (0.1 g resolution), calipers, multimeter. Photograph each part and store the photos in `v1_600/photos/` (new directory).

## 1. Propulsion System

### Motors ×4 (target: EX1103 KV11000, 3.8 g, 1.5 mm shaft diameter, 2-inch prop hole)
| Item | Measured value | Verdict |
|---|---|---|
| Model marking/label | | |
| Actual mass per unit (g) ×4 | To be weighed (user reports within the mass budget) | Target ≈3.8 g |
| Shaft diameter (mm) | **1.5 mm (measured 2026-10-13)** | ✓ Match |
| Prop mounting hole diameter/seat type | | Matches 2-inch 2023 prop |
| Three lead lengths | | Long enough to reach the ESC mounting position |

### ESCs ×2 (**arrived**, to be tested: AGFRC XR-20A candidate, see docs/esc_candidates.md)
| Item | Measured value | Verdict |
|---|---|---|
| Model/firmware | To be tested | 2S support, standard PWM input |
| Actual mass per unit (g) | To be weighed | |
| Whether the signal lead carries a BEC red wire | **To be tested (critical safety item: if present, the red wire must be disconnected)** | |
| Input/output connector types | To be tested | Match battery/motor |

### Propellers, 2-inch 2023 CW/CCW pair (**arrived**)
| Item | Measured value | Verdict |
|---|---|---|
| Prop hole diameter/prop type | To be tested (motor shaft 1.5 mm confirmed) | Reliable fit on the 1.5 mm motor shaft |
| CW/CCW rotation markings | To be tested | Both ultimately push air toward the tail |

## 2. Servos ×2 (ES9051, newly arrived)
| Item | Measured value | Verdict |
|---|---|---|
| Connector type and pitch | **Standard Dupont 2.54 mm ×3 pin (measured 2026-10-13)** | ✓ No adapter lead needed; plugs directly onto the pin header |
| Actual mass per unit (g) | To be weighed | |
| Outline L×W×H (mm) | To be tested | Compare with the servo mounting position |
| Horn styles/spline tooth count | To be tested | |

→ If JST 1.0 mm: add "1.0→2.54 adapter leads ×2" to the procurement list.

## 3. Battery (2S 7.4V 800mAh)
| Item | Measured value | Verdict |
|---|---|---|
| Actual mass (g) | | ≤55 g (design basis 52 g; if exceeded, follow docs/battery_52g_assessment.md) |
| Dimensions L×W×H (mm) | | Compare with the battery bay |
| Discharge lead connector | **XT30 (measured 2026-10-13)** | ✓ Matches design/ESC input |
| Balance connector type | **Suspected JST-XH 3-position (2S standard, to be confirmed by photo)** | Matches the balance charger XH port |
| Appearance (swelling/damaged sheath/odor) | Visual inspection pending | Disqualify if abnormal |

## 4. Power and Control
| Item | Measured value | Verdict |
|---|---|---|
| UBEC nominal input/output | | Input 2S, output 5 V continuous ≥3 A |
| UBEC input connector type | | |
| AHCT125N marking/package | | DIP-14, SN74AHCT125N |
| MPU6050 module pins | | VCC/GND/SCL/SDA/XDA/XCL/AD0/INT all present |
| MPU6050 board size/mounting holes | | As close to the CG as possible |
| 470µF capacitor voltage rating/diameter | | Clear polarity marking, rated ≥6.3 V (16 V recommended) |
| Logic analyzer | | 8-channel 24 MHz; with PulseView installed, do one trial capture |
| Pico 2 | | BOOTSEL enters download mode and the RP2350 drive appears |

## 5. Backfill

- `data/test_records.csv`:
  - `MASS` row: enter the summarized masses of the airframe-relevant items (motors ×4 + servos ×2 + battery + UBEC + Pico + sheet stock)
  - `FIT` row: enter the hole-position/connector matching conclusions
- If any dimension deviates from the design (overweight, connector mismatch, wrong hole positions) → stop here; after backfilling, ZCode recomputes the affected design parameters (CG, BOM, wire lengths).

## 6. Ordering reminders (must be in hand before the battery's first charge)

- [ ] 2S balance charger (selected per the balance connector type in section 3)
- [ ] ESCs ×2, RP1 V2 + Pocket ELRS transmitter (both ELRS 2.4G)
- [ ] Small-parts pack (SN74LVC1G17, 2N3904/S8050, resistor pack, XT30, silicone wire, heatshrink)
- [ ] 2-inch 2023 CW/CCW props + ES9051 adapter leads (if required per the section 2 verdict)
