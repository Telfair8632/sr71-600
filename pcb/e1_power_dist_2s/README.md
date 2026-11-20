# E1 Power-Distribution Board (e1_power_dist_2s)

The printed-circuit-board implementation of the aircraft's E1 control and power circuit (`docs/circuit_design.md`). The perfboard build documented in `docs/debug_log_2026-10-19.md` remains the bring-up rig for debug levels 5–6; this PCB is the v2 flight-intent board.

**Status: routed, verified, and ordered for fabrication on 2026-10-21** (JLC, 5 boards, delivery expected in 5–7 days). Design log: `docs/log_2026-10-21_e1_pcb.md`.

**Update 2026-11-19:** the boards arrived and the bare-board continuity was verified against the netlist. This board is now the **bench board**; it carries the battery distribution and two separate grounds (joined externally through the UBEC). Wiring reference and known blockers: `docs/pcb_v1_1_wiring.md`. The SMD successor (no on-board power distribution, 2 hand-soldered pads) is in `pcb/sr71_ctrl_v2/`.

## Board Specification

| Parameter | Value |
|---|---|
| Outline | 74.68 × 94.56 mm |
| Stackup | 2-layer, 1.6 mm, 2 oz copper |
| Parts | 41, all through-hole |
| Plated holes | 305 |
| Zones | Propulsion power distribution (XT30 → dual ESC pads → UBEC, sized for 18 A) · 5 V zone (C2 470 µF, C3 0.1 µF, indicator LED) · logic zone (Pico 2 socket headers, U1 DIP-14 socket, U2 adapter socket, Q1, resistor group, 4 test points) |
| Copper | Double-sided GND pour with 99 stitching vias; BATT 3.0 mm / +5 V 1.5 mm / +3V3 0.8 mm / signal 0.4 mm |
| Do-not-populate | R17/R18 (spare I2C pull-ups, fitted only if needed) |
| Off-board | Motor leads and the MPU6050 module connect by wire; they are not mounted on the board |

## Verification Record

- Schematic: ERC 0 errors; 27/27 nets matched against the E1 topology; footprint audit clean
- Layout/routing: 100/100 routed, DRC **0 violations, 0 unconnected** (`kicad/drc_report_routed.json`)
- Release review: two independent review rounds on the fabrication package (first round 8/10 — CPL column naming, DNP handling, BOM range notation fixed; final package passes all checks, DNP residue re-verified clean)
- Known fabrication risk flagged at order time: Q1 pad clearance 0.22 mm vs the 0.25 mm typical requirement for 2 oz copper — the fab may ask for production confirmation

## Directory Contents

```
kicad/      KiCad 10 source: schematic (.kicad_sch + PDF), board (.kicad_pcb),
            project file, board options, routed DRC report
fab/        Fabrication release 20261021_000347: Gerbers + drill, assembly BOM /
            CPL / positions (JLC column standard), both fab ZIPs (incl. the
            flat-layout variant for the JLC domestic uploader), order guide,
            fab options, coverage matrix, release manifest, LCSC procurement CSVs
renders/    Board render of the routed layout
```

Note: the release documents (order guide, fab options, coverage matrix) were generated in Chinese by the release pipeline and are presented here in English translation; `fab_manifest.json` is kept verbatim as the machine-generated provenance record (its embedded KiCad CLI output is from a zh-CN locale, and its absolute paths reference the original build machine).

The board was designed with a Windows-adapted fork of the open-source PCB-Agent-Teams pipeline plus KiCad 10.0.6; the tooling patches are public at [Telfair8632/PCB-Agent-Teams](https://github.com/Telfair8632/PCB-Agent-Teams) (branch `windows-patches`).
