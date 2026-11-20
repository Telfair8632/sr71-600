# SR71-600 Flight-Control Board V2 (SMD)

Board: 65 × 85 mm, 2 layers, 1.0 mm, 1 oz copper, 37 SMD parts + 4 × M2 mounting holes.
Designed 2026-11-19; DRC clean (0 violations / 0 unconnected); **not yet ordered**.

This board replaces the through-hole `pcb/e1_power_dist_2s/` board as the flight-intent control board. The battery / ESC / UBEC distribution moved off the board, so the board now starts at 5 V and can be assembled by a PCB house in one pass.

- Electrical design and rationale: `docs/pcb_v2_smd_design.md`
- Wiring of the previous board (for reference): `docs/pcb_v1_1_wiring.md`
- Design log: `docs/debug_log_2026-11-19.md`

## Contents

```
kicad/sr71_ctrl_v2.kicad_pcb    routed board (KiCad 10)
kicad/sr71_ctrl_v2.kicad_sch    schematic
kicad/sr71_ctrl_v2.net          netlist
fab/gerbers/                    Gerber + Excellon drill set
fab/assembly/bom_sr71_ctrl_v2.csv        37-line BOM (R17/R18 = DNP)
fab/assembly/sr71_ctrl_v2_positions.csv  pick-and-place (KiCad coordinates, Y negative)
renders/board_preview.png       copper preview (top)
renders/refs_map.png            reference designator map
```

## Fabrication

| Option | Value |
|---|---|
| Layers / thickness / copper | 2 / **1.0 mm** / **1 oz** |
| Surface / mask / silk | HASL / green / white |
| Quantity | 5 |
| Assembly | single-side SMT, 5 boards |
| Not placed | R17, R18 (DNP); J5 XT30 (through-hole, hand-solder 2 pads) |

Estimated cost: CNY 150–250 for five assembled boards, 3–6 days.

## Electrical summary

Same netlist as E1 minus the power section (25 nets):

- J5 = 5 V input (XT30; pin 4 = +5 V, pin 3 = GND) — the only hand-soldered joint
- J6/J7 = servo L/R (signal, +5 V, GND); J8/J9 = ESC signal L/R
- J10 = RP1 receiver (5 V, GND, TX → U2 → GP1, RX ← R1 ← GP0)
- J11 = MPU-6050 (3V3, GND, SDA, SCL, INT) — note the SDA/SCL cross against the GY-521 header
- J12/J13 = Pico 2 sockets (SMD, 2 × 20 pins)
- U1 = SN74AHCT125 (SOIC-14), U2 = SN74LVC1G17 (SOT-23-5), Q1 = MMBT3904 (SOT-23)

## Open items

1. Add LCSC part numbers to the BOM for the assembly order.
2. Confirm CPL orientation (KiCad vs JLC convention) in the uploader preview.
3. Order, assemble, then run the bring-up sequence from `docs/debug_procedure.md` levels 1–2 before inserting the Pico.
