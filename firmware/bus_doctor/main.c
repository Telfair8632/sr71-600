/*
 * SR71-600 bus doctor firmware: reports GP4(SDA)/GP5(SCL) levels and
 * runs a release test
 *
 * Purpose: locate where the MPU6050 I2C bus is being clamped low
 * (miswiring or a damaged module).
 * One line per second:
 *   read:    level read while floating (pull-up only); 0 = pulled low =
 *            something is clamping the bus
 *   release: actively pull low for 2 ms, release, then read back;
 *            0 = still low after release = hard short to ground
 * BUS-FREE = both lines return high (bus healthy, ready for I2C)
 *
 * Usage (while troubleshooting):
 *   1. With everything connected, note which line reads 0 — that is
 *      the clamped line
 *   2. Unplug one Dupont header at a time and re-check — if it goes
 *      to 1, the clamping comes from the module side of that wire
 *   3. Still 0 with everything unplugged — the problem is the wiring
 *      position on the Pico side
 */
#include <stdio.h>

#include "pico/stdlib.h"
#include "hardware/i2c.h"

#define PIN_SDA 4u
#define PIN_SCL 5u

static int sense_pin(uint pin)
{
    gpio_init(pin);
    gpio_set_dir(pin, GPIO_IN);
    gpio_pull_up(pin);
    sleep_ms(10); /* let the external pull-up settle */
    return gpio_get(pin);
}

static int release_test(uint pin)
{
    gpio_set_dir(pin, GPIO_OUT);
    gpio_put(pin, 0); /* pull low */
    sleep_ms(2);
    gpio_set_dir(pin, GPIO_IN); /* release (high impedance) */
    gpio_pull_up(pin);
    sleep_ms(10);
    return gpio_get(pin);
}

int main(void)
{
    stdio_init_all();

    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    printf("\n[sr71bus] GP4=SDA GP5=SCL bus doctor v2\n");

    int sda = sense_pin(PIN_SDA);
    int scl = sense_pin(PIN_SCL);
    int sda_rel = release_test(PIN_SDA);
    int scl_rel = release_test(PIN_SCL);
    printf("[sr71bus] DC: SDA=%d SCL=%d release: SDA=%d SCL=%d -> %s\n",
           sda, scl, sda_rel, scl_rel,
           (sda_rel && scl_rel) ? "BUS-FREE" : "BUS-STUCK");

    /* key test: probe the MPU6050 on GP4/GP5 with the I2C0 controller */
    printf("[sr71bus] init I2C0 @400k on GP4/GP5...\n");
    i2c_init(i2c0, 400u * 1000u);
    gpio_set_function(PIN_SDA, GPIO_FUNC_I2C);
    gpio_set_function(PIN_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(PIN_SDA);
    gpio_pull_up(PIN_SCL);

    const uint8_t addrs[2] = { 0x68u, 0x69u };
    uint8_t reg = 0x75u; /* WHO_AM_I */
    uint32_t n = 0;
    for (;;) {
        int found = -1;
        uint8_t who = 0;
        for (int i = 0; i < 2; i++) {
            uint8_t v = 0;
            int st = i2c_write_blocking(i2c0, addrs[i], &reg, 1, true);
            if (st < 0) {
                continue;
            }
            st = i2c_read_blocking(i2c0, addrs[i], &v, 1, false);
            if (st >= 0) {
                found = (int)addrs[i];
                who = v;
                break;
            }
        }
        if (found >= 0) {
            printf("[sr71bus] #%u *** MPU6050 FOUND at 0x%02x, WHO_AM_I=0x%02x ***\n",
                   (unsigned)n++, (uint8_t)found, who);
        } else {
            printf("[sr71bus] #%u no ACK (0x68/0x69) -- swap SDA/SCL or reseat plug now\n",
                   (unsigned)n++);
        }
        gpio_put(PICO_DEFAULT_LED_PIN, found >= 0);
        sleep_ms(1000);
    }
}
