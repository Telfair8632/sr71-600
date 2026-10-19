# SR71-600 Firmware (Pico 2 / RP2350)

Level-by-level bring-up corresponding to `docs/debug_procedure.md`. Each level is a standalone project, flashed and verified one level at a time.

**Three pre-built firmwares are included** (ready to flash as-is):
- `level3_minimal/sr71fc_level3.uf2` — bring-up level 3: minimal firmware
- `level4_imu/sr71fc_level4.uf2` — bring-up level 4: MPU-6050 readout
- `level6_pwm/sr71fc_level6.uf2` — bring-up level 6: four-channel 50 Hz PWM output waveforms

## Rebuilding

The toolchain is installed at **`D:\pico-tools`** (outside this workspace, because the ARM toolchain cannot handle non-ASCII paths):
`pico-sdk` (SDK 2.3.1), `gcc-arm` (14.2.1), `cmake`, `bin\ninja.exe`, `uf2conv.py`.

To rebuild after editing the sources (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 level3_minimal
powershell -ExecutionPolicy Bypass -File build.ps1 level4_imu
powershell -ExecutionPolicy Bypass -File build.ps1 level6_pwm
```

The script syncs the sources into `D:\pico-tools\build\` for compilation (a pure-ASCII path), then copies the resulting `.uf2/.elf` back into the level directory.

## Flashing

1. Hold the Pico 2 BOOTSEL button while plugging in USB; an `RP2350` drive appears.
2. Drag the `.uf2` onto the drive; the board reboots automatically and runs it.
3. A USB serial port (COMx) appears in Device Manager; connect with any serial terminal (any baud rate, e.g. 115200).

> Note: at startup the firmware **waits for the host to open the serial port (up to 8 seconds)
> before printing the boot banner** — otherwise the banner is dropped by USB CDC, and the key
> lines `reset cause: ...` / `WHO_AM_I=...` are never visible. So either connect within 8
> seconds of powering up, or use the script below (it captures the banner automatically).

## Level 3: Minimal Firmware (level3_minimal)

No peripheral wiring required; USB power alone is sufficient.

- [ ] On power-up prints `state=DISARMED oe_gate=OFF all_outputs=LOW`; LED flashes 60 ms every 1 s
- [ ] Prints `t=... ticks=... missed=0` once per second (missed staying 0 confirms no dropped ticks on the 1 ms time base)
- [ ] Runs continuously for **30 minutes**: no hang, no unexpected reset, no growth in missed
- [ ] Send `w` over serial: after the STALL line it should reset within ≤2 s, and the reboot log shows `reset cause: WATCHDOG`
- [ ] After the reset, the output state is still `DISARMED / oe=OFF / all_outputs=LOW`

Record results in `data/test_records.csv` (Pico stability pre-verification).

**Recommended: the automated acceptance script** (unattended monitoring + sends `w` automatically + reconnects automatically after the reset to verify the banner, and prints a direct PASS/FAIL verdict):

```powershell
python scripts/soak_level3.py --minutes 2    # 2-minute smoke test first
python scripts/soak_level3.py                # formal 30-minute run
```

A manual approach (PuTTY or any other serial terminal, any baud rate such as 115200) also works, but after the `w` reset the USB device re-enumerates, and the terminal must reconnect within 8 seconds to see the `reset cause: WATCHDOG` line — the script is recommended.

## Level 4: MPU-6050 (level4_imu)

Direct Dupont jumper-wire connections (**no soldering, no battery**):

| MPU6050 module | Pico 2 |
|---|---|
| VCC | 3V3(OUT) |
| GND | GND |
| SDA | GP4 |
| SCL | GP5 |
| INT | GP3 |

- [ ] On power-up prints `WHO_AM_I=0x68 ... PASS`
- [ ] Keep the board flat and still for 10 s → prints `calibration done ... bias gx= gy= gz=`
- [ ] Summary line `S,...` shows `rate≈200.0Hz`, `gap15=0`, `fifo=0`, `|a|≈1.0g`
- [ ] At rest gx, gy, gz are near 0; slowly raise/lower the nose and raise each wing to verify the pitch/roll directions and **write down the sign convention**
- [ ] Send `v` to start the 200 Hz data stream and record continuously for **10 minutes**: no freeze, no gap >15 ms (gap15=0), no FIFO overflow; send `v` again afterwards to stop the stream
- [ ] Record results in the IMU0 row of `data/test_records.csv`

10-minute capture command (run it in another window on the computer, or first confirm the connection with a serial terminal):

```powershell
pip install pyserial
python scripts/imu_capture.py --port COM5 --seconds 600 --out imu_10min.csv
```

## Level 6: Four-Channel 50 Hz PWM (level6_pwm)

**Do not connect servos or ESCs.** First verify with a logic analyzer directly on the Pico pins (after the buffer board is soldered, repeat the measurement on the AHCT125 output side — that is the formal acceptance of debug-procedure §6). USB power alone is sufficient.

Logic-analyzer hookup:

| Logic analyzer | Pico 2 |
|---|---|
| CH0 / CH1 / CH2 / CH3 | GP6 / GP7 / GP8 / GP9 |
| CH4 | GP2 (OE gate) |
| GND | GND |

- [ ] After power-up, the four channels **stay low for the ~0.5 s self-test window**, then the 50 Hz waveforms appear
- [ ] GP6/GP7 pulse width ≈1500 µs (servo center), GP8/GP9 ≈1000 µs (minimum throttle)
- [ ] Period steady at 20.000 ms (hardware PWM — there should be no jitter)
- [ ] Send `s` over serial: each channel in turn carries a signature pulse width for 2 s (1250/1750/1100/1150 µs) — confirm the moving channel is the intended one, **verifying no channel crosstalk**
- [ ] Send `e`/`d` over serial: CH4 (GP2) goes high/low; GP2 defaults low at power-up
- [ ] Send `w` over serial: triggers a watchdog reset — on the logic analyzer the waveforms must disappear, the pins stay low, and there are no pulses at all for 0.5 s after the reboot; serial shows `reset cause: WATCHDOG`
- [ ] Record results in `data/test_records.csv` (row PWM0, Pico pin-side pre-verification; fill in the formal result after repeating the measurement on the AHCT125 output side)
