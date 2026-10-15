/*
 * SR71-600 bring-up level 4: MPU-6050 readout and verification
 *
 * Wiring (direct Dupont jumper wires, no soldering; docs/debug_procedure.md level 4):
 *   MPU6050 VCC -> Pico 3V3(OUT)      (pull-ups may only be tied to 3.3 V)
 *   MPU6050 GND -> Pico GND
 *   MPU6050 SDA -> GP4
 *   MPU6050 SCL -> GP5
 *   MPU6050 INT -> GP3
 *
 * Corresponding acceptance items:
 *   1. WHO_AM_I expected to read 0x68
 *   2. 200 Hz sampling, gyro ±1000 dps, accelerometer ±8g
 *   3. DATA_RDY interrupt records a microsecond timestamp and sets the
 *      new-data flag; the main loop reads all six axes
 *   4. Gyro bias computed over 10 s at rest (runs automatically at
 *      power-up; keep the airframe still during it)
 *   5. Record continuously for 10 minutes: mean sample interval about
 *      5 ms, no consecutive sample drops / freezes / FIFO overflows
 *   6. Nose up / nose down / left wing up / right wing up to verify the
 *      sign of each axis (manual interpretation)
 *   7. Flat and at rest: angular rates near 0, accelerometer magnitude
 *      near 1 g
 *
 * Serial commands (USB CDC, any baud rate):
 *   v = toggle the 200 Hz raw data stream (CSV lines 'D,...', for the
 *      10-minute recording)
 *   c = redo the 10 s gyro bias calibration
 *   s = print statistics immediately
 *   h = help
 *
 * The 'S,...' summary line is printed every 500 ms and contains the
 * measured sample rate, maximum sample gap, count of gaps over 15 ms,
 * and the FIFO overflow count — the three pass conditions of acceptance
 * item 5.
 */
#include <stdio.h>
#include <math.h>
#include <inttypes.h>

#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/gpio.h"
#include "hardware/watchdog.h"
#include "hardware/timer.h"

#define I2C_PORT      i2c0   /* GP4/GP5 belong to I2C0; using i2c1 would hang forever due to the pin mismatch */
#define PIN_SDA       4u
#define PIN_SCL       5u
#define PIN_INT       3u
#define MPU_ADDR      0x68u
#define MPU_ADDR_ALT  0x69u

/* MPU-6050 registers */
#define REG_SMPLRT_DIV   0x19u
#define REG_CONFIG       0x1Au
#define REG_GYRO_CONFIG  0x1Bu
#define REG_ACCEL_CONFIG 0x1Cu
#define REG_INT_PIN_CFG  0x37u
#define REG_INT_ENABLE   0x38u
#define REG_INT_STATUS   0x3Au
#define REG_ACCEL_XOUT   0x3Bu
#define REG_WHO_AM_I     0x75u
#define REG_PWR_MGMT_1   0x6Bu
#define REG_PWR_MGMT_2   0x6Cu

#define WHO_EXPECTED     0x68u

/* Sample rate = 1 kHz / (1+SMPLRT_DIV) = 200 Hz (gyro outputs 1 kHz with the DLPF on) */
#define SMPLRT_DIV_VAL   4u
#define CONFIG_VAL       0x03u   /* DLPF 44Hz */
#define GYRO_CONFIG_VAL  0x10u   /* ±1000 dps -> 32.8 LSB/(deg/s) */
#define ACCEL_CONFIG_VAL 0x10u   /* ±8g -> 4096 LSB/g */

#define ACCEL_LSB_PER_G  4096.0f
#define RAD2DEG          57.29578f

#define GAP_WARN_US      15000u  /* acceptance condition: no consecutive sampling gap >15 ms */
#define CAL_SECONDS      10u
#define CAL_TARGET       (CAL_SECONDS * 200u) /* 10s @ 200Hz = 2000 samples */

/* ---- interrupt-side statistics (written only from the ISR) ---- */
static volatile uint32_t irq_count;
static volatile uint32_t max_gap_us;
static volatile uint32_t gap_over_15ms;
static volatile uint32_t fifo_ovf_count;
static volatile uint32_t last_ts_lo, last_ts_hi;
static volatile bool data_ready;

static void mpu_irq(uint gpio, uint32_t events)
{
    (void)gpio;
    (void)events;
    uint64_t now = time_us_64();
    uint64_t prev = ((uint64_t)last_ts_hi << 32) | last_ts_lo;
    if (prev != 0) {
        uint64_t gap = now - prev;
        uint32_t g32 = gap > 0xFFFFFFFFu ? 0xFFFFFFFFu : (uint32_t)gap;
        if (g32 > max_gap_us) {
            max_gap_us = g32;
        }
        if (gap > GAP_WARN_US) {
            gap_over_15ms++;
        }
    }
    last_ts_lo = (uint32_t)(now & 0xFFFFFFFFu);
    last_ts_hi = (uint32_t)(now >> 32);
    irq_count++;
    data_ready = true;
}

/* ---- MPU6050 low level ---- */
static int mpu_write(uint8_t reg, uint8_t val)
{
    uint8_t buf[2] = { reg, val };
    return i2c_write_blocking(I2C_PORT, MPU_ADDR, buf, 2, false);
}

static int mpu_read(uint8_t reg, uint8_t *dst, uint len)
{
    int st = i2c_write_blocking(I2C_PORT, MPU_ADDR, &reg, 1, true);
    if (st < 0) {
        return st;
    }
    return i2c_read_blocking(I2C_PORT, MPU_ADDR, dst, len, false);
}

static uint8_t mpu_addr_found;

static int mpu_detect(void)
{
    uint8_t who = 0;
    const uint8_t addrs[2] = { MPU_ADDR, MPU_ADDR_ALT };
    for (uint i = 0; i < 2; i++) {
        mpu_addr_found = addrs[i];
        int st = mpu_read(REG_WHO_AM_I, &who, 1);
        if (st >= 0) {
            return (int)who; /* device detected; the caller verifies the value */
        }
    }
    return -1;
}

int main(void)
{
    /* This level drives no outputs, but keeps the same power-up safety convention as level 3 */
    for (uint p = 6u; p <= 9u; p++) {
        gpio_init(p);
        gpio_set_dir(p, GPIO_OUT);
        gpio_put(p, 0);
    }
    gpio_init(2u);
    gpio_set_dir(2u, GPIO_OUT);
    gpio_put(2u, 0);

    stdio_init_all();

    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    watchdog_enable(2000u, 1);

    printf("\n[sr71imu] level4 mpu6050 | board=pico2\n");

    /* I2C0 @400kHz on GP4/GP5; the module has onboard 2.2k pull-ups, the internal pull-ups add one more layer of safety */
    i2c_init(I2C_PORT, 400u * 1000u);
    gpio_set_function(PIN_SDA, GPIO_FUNC_I2C);
    gpio_set_function(PIN_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(PIN_SDA);
    gpio_pull_up(PIN_SCL);

    /* INT rising-edge interrupt */
    gpio_init(PIN_INT);
    gpio_set_dir(PIN_INT, GPIO_IN);
    gpio_pull_down(PIN_INT);
    gpio_set_irq_enabled_with_callback(PIN_INT, GPIO_IRQ_EDGE_RISE, true, &mpu_irq);

    /* Reset and configure (the module may fail to ACK for the first few hundred ms after power-up; retry a few times) */
    int who = -1;
    for (int attempt = 0; attempt < 10 && who < 0; attempt++) {
        who = mpu_detect();
        if (who < 0) {
            sleep_ms(200);
        }
    }
    if (who < 0) {
        printf("[sr71imu] FAIL: no ACK on 0x%02x/0x%02x, check wiring VCC=3V3 GND SDA=GP4 SCL=GP5 INT=GP3\n",
               MPU_ADDR, MPU_ADDR_ALT);
        for (;;) {
            gpio_put(PICO_DEFAULT_LED_PIN, (time_us_32() >> 7) & 1u); /* fast blink = fault */
            watchdog_update();
            sleep_ms(50);
        }
    }
    printf("[sr71imu] WHO_AM_I=0x%02x (addr=0x%02x, expect 0x%02x) -> %s\n",
           (uint8_t)who, mpu_addr_found, WHO_EXPECTED,
           who == (int)WHO_EXPECTED ? "PASS" : "FAIL");

    mpu_write(REG_PWR_MGMT_1, 0x80u);  /* device reset */
    sleep_ms(100);
    mpu_write(REG_PWR_MGMT_1, 0x01u);  /* clock source = gyro X-axis PLL */
    sleep_ms(10);
    mpu_write(REG_PWR_MGMT_2, 0x00u);  /* all axes enabled */
    mpu_write(REG_SMPLRT_DIV, SMPLRT_DIV_VAL);
    mpu_write(REG_CONFIG, CONFIG_VAL);
    mpu_write(REG_GYRO_CONFIG, GYRO_CONFIG_VAL);
    mpu_write(REG_ACCEL_CONFIG, ACCEL_CONFIG_VAL);
    mpu_write(REG_INT_PIN_CFG, 0x20u); /* INT latched until INT_STATUS is read; active-high push-pull */
    mpu_write(REG_INT_ENABLE, 0x01u);  /* DATA_RDY */

    uint32_t cal_count = 0;
    int64_t cal_gx = 0, cal_gy = 0, cal_gz = 0;
    int16_t off_gx = 0, off_gy = 0, off_gz = 0;
    bool calibrated = false;
    bool calibrating = true; /* the first calibration starts automatically at power-up */

    printf("[sr71imu] gyro calibration: KEEP STILL for %us starting now...\n",
           (unsigned)CAL_SECONDS);

    bool stream = false;
    uint32_t sample_count = 0;
    uint64_t first_sample_us = 0;
    uint32_t last_summary_ms = 0;
    uint32_t prev_irq_seen = 0;
    uint32_t max_loop_us = 0;
    uint32_t stream_lines = 0;

    for (;;) {
        uint32_t t0 = time_us_32();
        bool new_sample = data_ready;
        if (new_sample) {
            data_ready = false;

            uint8_t st = 0, d[14];
            mpu_read(REG_INT_STATUS, &st, 1);      /* reading clears the latch */
            if (st & 0x80u) {
                fifo_ovf_count++;
            }
            int rs = mpu_read(REG_ACCEL_XOUT, d, 14);
            if (rs < 0) {
                printf("[sr71imu] I2C read error %d\n", rs);
            } else {
                int16_t ax = (int16_t)(((uint16_t)d[0] << 8) | d[1]);
                int16_t ay = (int16_t)(((uint16_t)d[2] << 8) | d[3]);
                int16_t az = (int16_t)(((uint16_t)d[4] << 8) | d[5]);
                int16_t tr = (int16_t)(((uint16_t)d[6] << 8) | d[7]);
                int16_t gx = (int16_t)(((uint16_t)d[8] << 8) | d[9]);
                int16_t gy = (int16_t)(((uint16_t)d[10] << 8) | d[11]);
                int16_t gz = (int16_t)(((uint16_t)d[12] << 8) | d[13]);

                if (sample_count == 0) {
                    first_sample_us = time_us_64();
                }
                sample_count++;

                if (calibrating) {
                    cal_gx += gx;
                    cal_gy += gy;
                    cal_gz += gz;
                    cal_count++;
                    if (cal_count >= CAL_TARGET) {
                        off_gx = (int16_t)(cal_gx / (int64_t)cal_count);
                        off_gy = (int16_t)(cal_gy / (int64_t)cal_count);
                        off_gz = (int16_t)(cal_gz / (int64_t)cal_count);
                        calibrated = true;
                        calibrating = false;
                        printf("[sr71imu] calibration done over %u samples: "
                               "bias gx=%d gy=%d gz=%d LSB\n",
                               (unsigned)cal_count, (int)off_gx, (int)off_gy, (int)off_gz);
                        printf("[sr71imu] now do axis check: nose up/down, left/right wing up\n");
                    }
                } else {
                    gx -= off_gx;
                    gy -= off_gy;
                    gz -= off_gz;
                }

                float axg = (float)ax / ACCEL_LSB_PER_G;
                float ayg = (float)ay / ACCEL_LSB_PER_G;
                float azg = (float)az / ACCEL_LSB_PER_G;
                float amag = sqrtf(axg * axg + ayg * ayg + azg * azg);
                /* Angles are accelerometer-based, for axis-check interpretation only; the airframe mounting orientation is confirmed manually */
                float pitch = atan2f(-axg, sqrtf(ayg * ayg + azg * azg)) * RAD2DEG;
                float roll  = atan2f(ayg, azg) * RAD2DEG;
                float tempc = (float)tr / 340.0f + 36.53f;

                if (stream) {
                    printf("D,%" PRIu64 ",%d,%d,%d,%d,%d,%d\n",
                           time_us_64(), (int)gx, (int)gy, (int)gz,
                           (int)ax, (int)ay, (int)az);
                    stream_lines++;
                }

                /* the 500 ms summary is printed in one place below; keep only the most recent attitude quantities here */
                static float s_amag, s_pitch, s_roll, s_temp;
                static int16_t s_gx, s_gy, s_gz;
                s_amag = amag; s_pitch = pitch; s_roll = roll; s_temp = tempc;
                s_gx = gx; s_gy = gy; s_gz = gz;

                uint32_t now_ms = (uint32_t)(time_us_64() / 1000u);
                if (now_ms - last_summary_ms >= 500u) {
                    last_summary_ms = now_ms;
                    uint32_t irq_now = irq_count;
                    uint32_t n_new = irq_now - prev_irq_seen;
                    prev_irq_seen = irq_now;
                    uint64_t elapsed_us = time_us_64() - first_sample_us;
                    float rate = elapsed_us > 0 ? (float)irq_now * 1000000.0f / (float)elapsed_us : 0.0f;
                    printf("S,t=%ums irq=%u new500ms=%u rate=%.1fHz maxgap=%uus gap15=%u fifo=%u "
                           "|a|=%.3fg pitch=%.1f roll=%.1f T=%.1fC "
                           "gx=%d gy=%d gz=%d %s\n",
                           (unsigned)now_ms, irq_now, n_new, (double)rate,
                           max_gap_us, gap_over_15ms, fifo_ovf_count,
                           (double)s_amag, (double)s_pitch, (double)s_roll, (double)s_temp,
                           (int)s_gx, (int)s_gy, (int)s_gz,
                           calibrated ? "CAL_OK" : (calibrating ? "CALIBRATING" : "UNCAL"));
                }
            }
        }

        int c = getchar_timeout_us(0);
        if (c == 'v') {
            stream = !stream;
            if (stream) {
                stream_lines = 0;
                printf("D,t_us,gx,gy,gz,ax,ay,az\n");
            }
            printf("[sr71imu] stream=%s\n", stream ? "ON (200Hz CSV)" : "OFF");
        } else if (c == 'c') {
            cal_count = 0;
            cal_gx = cal_gy = cal_gz = 0;
            calibrated = false;
            calibrating = true;
            printf("[sr71imu] recalibration started, KEEP STILL %us\n", (unsigned)CAL_SECONDS);
        } else if (c == 's') {
            printf("[sr71imu] irq=%u maxgap=%uus gap15=%u fifo=%u streamlines=%u maxloop=%uus\n",
                   irq_count, max_gap_us, gap_over_15ms, fifo_ovf_count, stream_lines,
                   max_loop_us);
        } else if (c == 'h') {
            printf("[sr71imu] v=toggle 200Hz stream, c=recalibrate 10s, s=stats, h=help\n");
        }

        uint32_t dt = time_us_32() - t0;
        if (dt > max_loop_us) {
            max_loop_us = dt;
        }

        watchdog_update();
    }
}
