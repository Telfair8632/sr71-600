# Fab Vendor Options (JLCPCB vs PCBWay)

> Source: `.claude/skills/fab/references/jlcpcb.md` / `.claude/skills/fab/references/pcbway.md` (pipeline references)
> Generated 2026-10-21 00:03 JST

## Process Comparison

| Item | JLCPCB | PCBWay |
|---|---|---|
| Min trace / space | 3.5 mil / 3.5 mil | 3 mil / 3 mil |
| Min hole | 0.2 mm (with copper) | 0.15 mm (laser-drilled) |
| Thickness range | 0.4–2.0 mm | 0.2–6.0 mm |
| Copper weight | 1–2 oz (standard) / 4 oz upcharge | 1–6 oz |
| Solder mask colors | green/red/yellow/blue/white/black | green/red/yellow/blue/white/black/purple/matte black |
| Assembly | SMT parts must be in the LCSC catalog | turnkey (global sourcing) |
| Minimum order | 5 boards | 5 boards |

## Turnkey Fit for This Board

- LCSC coverage: 4/4 → **JLCPCB one-stop is viable**
- DigiKey JP coverage: 0/4
- Mouser JP coverage: 0/4

## Recommendation per User Preferences

Phase 2 channel preference: **LCSC + JLCPCB → JLCPCB turnkey first choice**

LCSC coverage 4/4:
- ✅ Full coverage — JLCPCB turnkey directly viable (follows the stated preference)

Full fab-vendor rules: `.claude/skills/release/references/fab_internals.md` or the workspace CLAUDE.md (pipeline-internal references).
