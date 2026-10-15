/*
 * SR71-600 bring-up level 3: Pico 2 minimal firmware
 *
 * Corresponding acceptance items (docs/debug_procedure.md, level 3):
 *   1. Run only the LED, USB logging, and the 1 ms system tick
 *   2. Run continuously for 30 minutes with no hang and no unexpected reset
 *   3. Watchdog enabled; after a deliberate main-loop stall (send 'w' over
 *      serial) the board must reset, and throttle/servo outputs must remain
 *      disabled after the reset
 *   4. Disarmed by default at power-up; the AHCT125 stays off (none of the
 *      four outputs produces a valid pulse)
 *
 * Pin assignment (docs/circuit_design.md, E1 schematic):
 *   GP2      -> NPN base (through 4.7k). Low = transistor cut off, OE_N
 *               pulled high by 10k, all four AHCT125 outputs
 *               high-impedance (failsafe state)
 *   GP6/GP7  -> left/right servo PWM (buffered through the AHCT125)
 *   GP8/GP9  -> left/right ESC PWM (buffered through the AHCT125)
 *
 * Serial commands (USB CDC, any baud rate):
 *   w = deliberately stall the main loop to trigger a watchdog reset
 *      (acceptance item 3)
 */
#include <stdio.h>
#include <inttypes.h>

#include "pico/stdlib.h"
#include "hardware/watchdog.h"
#include "hardware/timer.h"

#define PIN_OE_GATE      2u
#define PIN_OUT_SERVO_L  6u
#define PIN_OUT_SERVO_R  7u
#define PIN_OUT_ESC_L    8u
#define PIN_OUT_ESC_R    9u
#define NUM_OUTS         4u

#define TICK_PERIOD_MS     1u
#define WATCHDOG_PERIOD_MS 2000u
#define LED_ON_MS          60u
#define LED_PERIOD_MS      1000u

static repeating_timer_t tick_timer;
static volatile uint32_t tick_count;
static volatile uint32_t tick_overrun; /* cumulative dropped ticks when the interval between two loop passes exceeds 1 ms */

static bool on_tick(repeating_timer_t *rt)
{
    (void)rt;
    tick_count++;
    return true;
}

static void force_outputs_safe(void)
{
    const uint pins[NUM_OUTS] = {
        PIN_OUT_SERVO_L, PIN_OUT_SERVO_R, PIN_OUT_ESC_L, PIN_OUT_ESC_R
    };
    for (uint i = 0; i < NUM_OUTS; i++) {
        gpio_init(pins[i]);
        gpio_set_dir(pins[i], GPIO_OUT);
        gpio_put(pins[i], 0);
    }
    gpio_init(PIN_OE_GATE);
    gpio_set_dir(PIN_OE_GATE, GPIO_OUT);
    gpio_put(PIN_OE_GATE, 0);
}

int main(void)
{
    /* First thing after reset: every pin that could drive a control surface or the throttle goes to a safe level */
    force_outputs_safe();

    stdio_init_all();

    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    if (!add_repeating_timer_ms(-(int32_t)TICK_PERIOD_MS, on_tick, NULL, &tick_timer)) {
        panic("1ms tick timer failed");
    }

    watchdog_enable(WATCHDOG_PERIOD_MS, 1);

    bool wd_reset = watchdog_caused_reboot();
    printf("\n[sr71fc] level3 minimal | board=pico2\n");
    printf("[sr71fc] reset cause: %s\n",
           wd_reset ? "WATCHDOG" : "POWERON/OTHER");
    printf("[sr71fc] state=DISARMED oe_gate=OFF all_outputs=LOW\n");
    printf("[sr71fc] send 'w' to stall main loop (watchdog test)\n");

    uint32_t last_seen_tick = tick_count;
    uint32_t max_loop_us = 0;
    uint32_t last_report_s = UINT32_MAX;

    for (;;) {
        uint32_t t0 = time_us_32();

        int c = getchar_timeout_us(0);
        if (c == 'w') {
            printf("[sr71fc] STALL on purpose; watchdog reset in <=%ums\n",
                   (unsigned)WATCHDOG_PERIOD_MS);
            stdio_flush();
            for (;;) {
                tight_loop_contents(); /* deliberately stop feeding the watchdog, wait for the reset */
            }
        }

        uint32_t now_tick = tick_count;
        uint32_t elapsed = now_tick - last_seen_tick;
        last_seen_tick = now_tick;
        if (elapsed > 1) {
            tick_overrun += elapsed - 1;
        }

        uint32_t phase = now_tick % LED_PERIOD_MS;
        gpio_put(PICO_DEFAULT_LED_PIN, phase < LED_ON_MS);

        uint32_t sec = now_tick / 1000u;
        if (sec != last_report_s) {
            last_report_s = sec;
            printf("[sr71fc] t=%" PRIu32 "s ticks=%" PRIu32
                   " missed=%" PRIu32 " maxloop=%" PRIu32
                   "us state=DISARMED oe=OFF\n",
                   sec, now_tick, tick_overrun, max_loop_us);
            max_loop_us = 0;
        }

        uint32_t dt = time_us_32() - t0;
        if (dt > max_loop_us) {
            max_loop_us = dt;
        }

        watchdog_update();
    }
}
