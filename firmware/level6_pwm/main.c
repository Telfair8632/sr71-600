/*
 * SR71-600 debug level 6: four-channel 50 Hz PWM output waveforms
 *
 * Maps to the acceptance items (docs/debug_procedure.md, level 6):
 *   1. When disarmed, on self-test failure, or after a Pico reset,
 *      the four channels carry no valid pulses
 *   2. After the self-test passes, servo outputs start at 50 Hz, ~1500us center
 *   3. ESC outputs start at 50 Hz, ~1000us minimum throttle
 *   4. GP6/GP7 = left/right servo, GP8/GP9 = left/right ESC, no channel crosstalk
 *   5. Reset/startup glitch-free: pins stay low after pulses disappear,
 *      and no pulses at all during the self-test window after a reboot
 *
 * Implementation notes:
 *   - Hardware PWM at exactly 50 Hz: sys_clk integer-divided to a 1 MHz counter,
 *     wrap = 20000-1 (period 20.000 ms, no software jitter; a logic analyzer
 *     can read period/pulse width directly)
 *     GP6=PWM3A  GP7=PWM3B  GP8=PWM4A  GP9=PWM4B
 *   - Power-up sequence (the key to glitch-free startup):
 *       reset -> first action: force the 4 outputs + GP2 strongly low and
 *       enable internal pull-downs -> configure PWM (duty = 0) and start the
 *       counters -> self-test ~0.5 s -> only after it passes, switch the pins
 *       to the PWM function (waveforms appear only from this point)
 *   - GP2 / OE gate held low = AHCT125 high-impedance; serial 'e' raises it (arm)
 *   - Watchdog 2 s; after a reset the firmware returns to the locked state
 *
 * Serial commands (USB CDC):
 *   s = channel-identification sweep: each channel outputs a signature pulse
 *       width for 2 s in turn (verifies no channel crosstalk)
 *   c = re-center: servos 1500us / ESCs 1000us
 *   e = arm (GP2 high, buffer board gate opens)
 *   d = disarm (GP2 low, buffer board gate closes)
 *   w = deliberately stall the main loop to trigger a watchdog reset (item 5)
 */
#include <stdio.h>
#include <inttypes.h>

#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"
#include "hardware/watchdog.h"
#include "hardware/timer.h"

#define PIN_OE_GATE      2u
#define PIN_OUT_SERVO_L  6u   /* PWM3 A */
#define PIN_OUT_SERVO_R  7u   /* PWM3 B */
#define PIN_OUT_ESC_L    8u   /* PWM4 A */
#define PIN_OUT_ESC_R    9u   /* PWM4 B */
#define NUM_OUTS         4u

/* 50Hz/20ms @ 1MHz counter clock: a pulse width in us equals the CCR count, intuitive and exact */
#define PWM_TOP          (20000u - 1u)
#define SERVO_CENTER_US  1500u
#define ESC_MIN_US       1000u

#define TICK_PERIOD_MS     1u
#define WATCHDOG_PERIOD_MS 2000u
#define LED_ON_MS          60u
#define LED_PERIOD_MS      1000u
#define SELFTEST_MS        500u   /* time the self-test holds the outputs low; observable on a logic analyzer */

typedef enum {
    ST_SELFTEST = 0,
    ST_RUN,
    ST_SELFTEST_FAIL
} state_t;

static repeating_timer_t tick_timer;
static volatile uint32_t tick_count;
static volatile uint32_t tick_overrun;

static const uint out_pins[NUM_OUTS] = {
    PIN_OUT_SERVO_L, PIN_OUT_SERVO_R, PIN_OUT_ESC_L, PIN_OUT_ESC_R
};
static uint16_t pulse_us[NUM_OUTS]; /* current commanded pulse widths */

static bool on_tick(repeating_timer_t *rt)
{
    (void)rt;
    tick_count++;
    return true;
}

/* First action after reset: all outputs strongly driven low + internal pull-downs, GP2 (OE gate) low */
static void force_outputs_safe(void)
{
    for (uint i = 0; i < NUM_OUTS; i++) {
        gpio_init(out_pins[i]);
        gpio_set_dir(out_pins[i], GPIO_OUT);
        gpio_put(out_pins[i], 0);
        gpio_pull_down(out_pins[i]);
    }
    gpio_init(PIN_OE_GATE);
    gpio_set_dir(PIN_OE_GATE, GPIO_OUT);
    gpio_put(PIN_OE_GATE, 0);
}

/* Configure and start both PWM slices (duty 0 = output constantly low; not yet routed to pins) */
static bool pwm_setup_start(void)
{
    uint32_t clk_hz = clock_get_hz(clk_sys);
    uint32_t div = clk_hz / 1000000u; /* integer divide down to a 1 MHz counter */
    if (div == 0u || div > 255u || clk_hz % 1000000u != 0u) {
        return false; /* non-integer-MHz system clock: this firmware's exact division does not hold */
    }
    const uint slices[2] = {
        pwm_gpio_to_slice_num(PIN_OUT_SERVO_L),
        pwm_gpio_to_slice_num(PIN_OUT_ESC_L)
    };
    for (uint s = 0; s < 2u; s++) {
        pwm_config cfg = pwm_get_default_config();
        pwm_config_set_clkdiv_int_frac(&cfg, div, 0);
        pwm_config_set_wrap(&cfg, PWM_TOP);
        pwm_init(slices[s], &cfg, false); /* do not start yet */
        pwm_set_both_levels(slices[s], 0u, 0u); /* duty 0: constantly low once routed */
        pwm_set_enabled(slices[s], true);       /* let the counters run for the self-test */
    }
    return true;
}

/* Self-test: the 1 ms tick is advancing + both slice counters are moving */
static bool selftest(void)
{
    uint32_t t0 = tick_count;
    uint slice_s = pwm_gpio_to_slice_num(PIN_OUT_SERVO_L);
    uint slice_e = pwm_gpio_to_slice_num(PIN_OUT_ESC_L);
    uint16_t c1a = (uint16_t)pwm_get_counter(slice_s);
    uint16_t c1b = (uint16_t)pwm_get_counter(slice_e);
    sleep_ms(SELFTEST_MS); /* outputs stay low meanwhile: acceptance item "no pulses during self-test" */
    bool tick_ok  = (tick_count - t0) >= SELFTEST_MS;
    bool cnt_ok   = (uint16_t)pwm_get_counter(slice_s) != c1a
                 && (uint16_t)pwm_get_counter(slice_e) != c1b;
    return tick_ok && cnt_ok;
}

static void set_channel(uint idx, uint16_t us)
{
    pulse_us[idx] = us;
    uint slice = pwm_gpio_to_slice_num(out_pins[idx]);
    uint chan  = pwm_gpio_to_channel(out_pins[idx]);
    pwm_set_chan_level(slice, chan, us); /* double-buffered: takes effect at the frame boundary, glitch-free */
}

static void all_center(void)
{
    set_channel(0, SERVO_CENTER_US);
    set_channel(1, SERVO_CENTER_US);
    set_channel(2, ESC_MIN_US);
    set_channel(3, ESC_MIN_US);
}

/* Channel-identification sweep: each channel in turn gets a signature width for 2 s, others hold safe values */
static void channel_sweep(void)
{
    static const uint16_t feat[NUM_OUTS] = { 1250u, 1750u, 1100u, 1150u };
    static const char *name[NUM_OUTS] = {
        "servoL(GP6)", "servoR(GP7)", "escL(GP8)", "escR(GP9)"
    };
    printf("[sr71fc] sweep start: watch each channel pulse 2s\n");
    for (uint i = 0; i < NUM_OUTS; i++) {
        set_channel(i, feat[i]);
        printf("[sr71fc] ch%u %s -> %uus for 2s\n",
               i, name[i], feat[i]);
        for (uint ms = 0; ms < 2000u; ms += 50u) {
            sleep_ms(50);
            watchdog_update();
        }
        all_center();
        printf("[sr71fc] ch%u back to safe value\n", i);
    }
    printf("[sr71fc] sweep done (12s). all back to center/min\n");
}

int main(void)
{
    /* First action after reset: every output to a safe level (low), OE gate closed */
    force_outputs_safe();

    stdio_init_all();

    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    state_t state = ST_SELFTEST;
    bool pwm_ok = pwm_setup_start();

    if (!pwm_ok || !add_repeating_timer_ms(-(int32_t)TICK_PERIOD_MS,
                                           on_tick, NULL, &tick_timer)) {
        state = ST_SELFTEST_FAIL;
    } else {
        watchdog_enable(WATCHDOG_PERIOD_MS, 1);
        state = selftest() ? ST_RUN : ST_SELFTEST_FAIL;
    }

    if (state == ST_RUN) {
        /* Self-test passed: load safe pulse widths first, then switch the pins to PWM — waveforms start only now */
        all_center();
        for (uint i = 0; i < NUM_OUTS; i++) {
            gpio_set_function(out_pins[i], GPIO_FUNC_PWM);
        }
    } else {
        /* Self-test failed: pins stay as GPIO outputs driven low, never switched to PWM */
        for (uint i = 0; i < NUM_OUTS; i++) {
            pwm_set_enabled(pwm_gpio_to_slice_num(out_pins[i]), false);
            gpio_set_function(out_pins[i], GPIO_FUNC_SIO);
            gpio_set_dir(out_pins[i], GPIO_OUT);
            gpio_put(out_pins[i], 0);
        }
    }

    bool wd_reset = watchdog_caused_reboot();
    printf("\n[sr71fc] level6 pwm | board=pico2\n");
    printf("[sr71fc] reset cause: %s\n",
           wd_reset ? "WATCHDOG" : "POWERON/OTHER");
    printf("[sr71fc] selftest: %s\n",
           state == ST_RUN ? "PASS" : "FAIL(outputs forced LOW)");
    if (state == ST_RUN) {
        printf("[sr71fc] 50Hz running: servo 1500us esc 1000us, oe_gate=LOCKED\n");
        printf("[sr71fc] cmds: s=sweep c=center e=arm d=disarm w=wdt-reset\n");
    }

    uint32_t last_seen_tick = tick_count;
    uint32_t last_report_s = UINT32_MAX;

    for (;;) {
        int c = getchar_timeout_us(0);
        if (c == 'w' && state == ST_RUN) {
            printf("[sr71fc] STALL on purpose; watchdog reset in <=%ums\n",
                   (unsigned)WATCHDOG_PERIOD_MS);
            printf("[sr71fc] after reset: outputs must stay LOW until selftest\n");
            stdio_flush();
            for (;;) {
                tight_loop_contents(); /* deliberately stop feeding the watchdog, wait for reset */
            }
        } else if (c == 's' && state == ST_RUN) {
            channel_sweep();
        } else if (c == 'c' && state == ST_RUN) {
            all_center();
            printf("[sr71fc] centered: 1500/1500/1000/1000us\n");
        } else if (c == 'e' && state == ST_RUN) {
            gpio_put(PIN_OE_GATE, 1);
            printf("[sr71fc] OE gate GP2=HIGH (buffer ENABLED)\n");
        } else if (c == 'd') {
            gpio_put(PIN_OE_GATE, 0);
            printf("[sr71fc] OE gate GP2=LOW (buffer disabled)\n");
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
            printf("[sr71fc] t=%" PRIu32 "s missed=%" PRIu32
                   " pwm=%04u/%04u/%04u/%04uus oe=%s\n",
                   sec, tick_overrun,
                   pulse_us[0], pulse_us[1], pulse_us[2], pulse_us[3],
                   gpio_get(PIN_OE_GATE) ? "ARMED" : "LOCKED");
        }

        watchdog_update();
    }
}
