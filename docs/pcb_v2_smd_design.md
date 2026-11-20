# SR71-600 Flight-Control Board V2 (SMD, one-pass assembly)

Date: 2026-11-19. Status: **design complete, DRC clean, fabrication files generated, not yet ordered.**
Design source and generated artifacts: `pcb/sr71_ctrl_v2/`.

## 1. Why a second board

The V1.1 board (`pcb/e1_power_dist_2s/`) works, but it was designed for hand soldering:

- 41 through-hole parts, **~150 solder joints**, 1–2 hours of work per board;
- it carries the battery distribution, so it needs 2 oz copper and big terminals;
- bare board ≈ **30 g**, assembled with the Pico and terminals ≈ **60–70 g**, i.e. about a third of the 190.7 g aircraft budget.

The V2 board moves the power distribution **off the board** and converts everything to SMD so the board can be assembled by a PCB house in one pass. The electrical netlist is unchanged.

## 2. Configuration

| Item | V1.1 | **V2** |
|---|---|---|
| Power distribution (battery / ESCs / UBEC) | on board (J1–J4) | **off board** — XT30 harness |
| Board 5 V input | J5 terminal block | **J5 XT30** (kept deliberately: reverse-polarity proof, 2 solder joints) |
| Components | 41 × through-hole | **37 × SMD** (0603 passives, SOIC-14, SOT-23-5, SOT-23, 2.54 SMD headers/sockets) |
| Board size / thickness / copper | 74.6 × 94.5 mm / 1.6 mm / 2 oz | **65 × 85 mm / 1.0 mm / 1 oz** |
| Hand soldering on the board | ~150 joints | **2 joints** (J5 +/−) |
| Bare board mass | ≈ 30 g | ≈ **14 g** |
| Assembled mass incl. Pico | ≈ 60–70 g | ≈ **31 g** |

The 5 V input still uses an XT30 because it carries servo current (two ES9051, ~1–1.5 A peak) and because a keyed connector can not be plugged in backwards. Everything else — including the Pico sockets and the servo/ESC/receiver/IMU headers — is SMD and is placed by the assembly house.

## 3. Electrical design

Identical to E1/V1.1 (25 nets), with two changes only:

1. `BATT_P` / `BATT_N` and connectors J1–J4 removed; the board now starts at the 5 V rail.
2. J5 is the single power entry (`pin 4 = +5V`, `pin 3 = GND` on the XT30 footprint).

Netlist highlights (unchanged): GP6–GP9 → U1 inputs (with 10 k pull-downs R13–R16); U1 outputs → 220 Ω (R3–R6) → connectors (with 10 k pull-downs R7–R10); OE_N pulled up by R11 and pulled down by Q1 (R2/R12 from GP2); RP1 TX buffered by U2 (SN74LVC1G17) into GP1; R1 in the telemetry path to RP1 RX; I2C pull-ups R17/R18 placed but DNP; Pico VSYS tied to +5 V.

## 4. Results (2026-11-19)

| Metric | Value |
|---|---|
| Footprints | 37 components + 4 × M2 mounting holes |
| Nets | 25, **all routed** |
| Vias | 89 |
| Track width / clearance | 0.25 mm / 0.25 mm (0.6 mm for +5 V) |
| DRC | **0 violations, 0 unconnected** |
| Silkscreen | References hidden (they clash with pads); functional legend printed instead: `J5 5V-IN / J6 S-L / J7 S-R / J8 ESC-L / J9 ESC-R / J10 RP1 / J11 IMU / J12-J13 Pico`; `+5V`, `GND`, `XT30` labels at J5 |

## 5. Files

| File | Purpose |
|---|---|
| `kicad/sr71_ctrl_v2.kicad_pcb` | routed board (KiCad 10) |
| `kicad/sr71_ctrl_v2.kicad_sch`, `.net` | schematic and netlist |
| `fab/gerbers/` | Gerber + Excellon drill set (upload as-is) |
| `fab/assembly/bom_sr71_ctrl_v2.csv` | 37-line BOM (R17/R18 marked DNP) |
| `fab/assembly/sr71_ctrl_v2_positions.csv` | pick-and-place coordinates (KiCad convention, Y negative) |
| `renders/board_preview.png`, `refs_map.png` | copper preview and reference map |

## 6. Fabrication parameters

- 2 layers, **1.0 mm**, **1 oz**, green solder mask, white silk, HASL
- 5 boards; single-side SMT assembly
- Exclude R17/R18 (DNP); J5's XT30 is through-hole and is **not** placed by the assembly house
- Estimated cost: PCB CNY 50–80 + SMT CNY 50–90 + parts CNY 40–80 ≈ **CNY 150–250 for 5 boards**, 3–6 days

## 7. Open items before ordering

1. **LCSC part numbers** are not yet in the BOM (values and footprints only). Needed for JLC SMT upload.
2. **CPL format**: the exported file uses KiCad coordinates (negative Y). JLC accepts the KiCad option in its uploader; alternatively the Y axis must be flipped and rotations normalised.
3. Order confirmation and a final visual check of `renders/refs_map.png`.
