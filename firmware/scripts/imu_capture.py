#!/usr/bin/env python3
"""SR71-600 bring-up level 4: MPU6050 10-minute capture script.

Connects to the Pico USB serial port, writes the 200 Hz data stream
('D,' lines) to a CSV file, and displays the sample rate, maximum gap,
and count of >15 ms gaps ('S,' lines) in real time.

Usage:
    python imu_capture.py --port COM5 --seconds 600 --out imu_10min.csv
Dependencies:
    pip install pyserial
"""
import argparse
import csv
import re
import sys
import time

import serial

S_RE = re.compile(
    r"S,t=(\d+)ms irq=(\d+) new500ms=(\d+) rate=([\d.]+)Hz "
    r"maxgap=(\d+)us gap15=(\d+) fifo=(\d+)"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="Pico COM port, e.g. COM5")
    ap.add_argument("--seconds", type=float, default=600.0, help="recording duration in seconds")
    ap.add_argument("--out", default="imu_10min.csv", help="output CSV file")
    args = ap.parse_args()

    ser = serial.Serial(args.port, 115200, timeout=1)
    ser.reset_input_buffer()
    ser.write(b"v")  # start the 200 Hz data stream
    rows = 0
    max_gap = 0
    gap15 = 0
    rate = 0.0
    start = time.time()
    print(f"Recording {args.seconds}s from {args.port} -> {args.out}")

    with open(args.out, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["t_us", "gx", "gy", "gz", "ax", "ay", "az"])
        try:
            while time.time() - start < args.seconds:
                line = ser.readline().decode("ascii", errors="ignore").strip()
                if line.startswith("D,"):
                    parts = line[2:].split(",")
                    if len(parts) == 7:
                        wr.writerow(parts)
                        rows += 1
                elif line.startswith("S,"):
                    m = S_RE.search(line)
                    if m:
                        rate = float(m.group(4))
                        max_gap = int(m.group(5))
                        gap15 = int(m.group(6))
                        remain = int(args.seconds - (time.time() - start))
                        print(f"rows={rows} rate={rate:.1f}Hz "
                              f"maxgap={max_gap}us gap15={gap15} "
                              f"remaining={remain}s", flush=True)
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            try:
                ser.write(b"v")  # stop the data stream
            except serial.SerialException:
                pass

    print(f"Done: {rows} samples, rate={rate:.1f}Hz, "
          f"maxgap={max_gap}us, gap15={gap15}")
    if gap15 > 0:
        print("FAIL: >15ms sampling gap detected")
        sys.exit(1)
    print("PASS criterion (no freeze / no >15ms gap) met at capture level; "
          "verify gap15/fifo in firmware summary too")


if __name__ == "__main__":
    main()
