# 52 g Battery Impact Assessment

## Premises

- The original weight calculation used a 32 g battery.
- The battery actually available is 52 g, a direct 20 g increase.
- The manufacturer peak thrust of the two motors totals 243.8 gf; installed thrust must be re-measured on the bench.
- The current flight-release gate for powered flight remains a measured static thrust-to-weight ratio of no less than 1.2.

## Two Weight Bases

| Scenario | Takeoff mass | Manufacturer peak thrust-to-weight | Thrust-to-weight assuming 20% installation loss |
|---|---:|---:|---:|
| 20 g growth reserve and 16 g nose ballast both counted in | 217.89 g | 1.119 | 0.895 |
| Growth reserve and nose ballast not installed | 181.89 g | 1.340 | 1.072 |

The 20 g growth reserve is not a physical part. The 52 g battery itself shifts the CG forward, so the 16 g nose ballast is expected to be unnecessary. A reasonable target is to hold the true takeoff mass near 182–192 g; above 200 g the current powertrain has almost no margin left for installation loss.

## Center of Gravity

With the 20 g growth reserve and the 16 g nose ballast not installed, placing the center of the 52 g battery about 138 mm from the nose tip puts the CG near the middle of the current window. That position lies within the existing 120–220 mm battery adjustment range. The final position is still set by the measured CG of the complete aircraft.

## Flight-Release Thrust Formula

Maximum permitted takeoff mass:

`max takeoff mass (g) = measured twin-motor installed static thrust (gf) / 1.2`

| Measured twin-motor static thrust | Maximum permitted takeoff mass |
|---:|---:|
| 220 gf | 183.3 g |
| 230 gf | 191.7 g |
| 240 gf | 200.0 g |
| 243.8 gf | 203.2 g |

## Decisions

1. The 52 g battery may be purchased, but only after confirming that it is 2S, that its dimensions fit the battery bay, and that it can sustain the twin-motor peak current of about 18.4 A.
2. Do not pre-install steel nose ballast.
3. Make the final judgment from the true as-built weight and the true installed thrust.
4. If the thrust-to-weight ratio falls below 1.2, first strip adhesive, harness, cosmetic, and non-essential structural weight.
5. If still short, re-select the motor, propeller, and ESC combination; never simply fit a larger propeller on the EX1103 without bench testing current and temperature rise.
