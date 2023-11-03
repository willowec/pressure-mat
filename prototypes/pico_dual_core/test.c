
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"

#include "custom_multicore.h"

#define LED_PIN  25


int core1_main() {
    puts("hello from core 1\n");
    while (1) {
        sleep_ms(1000);
        puts("core 1 is going\n");
    }
}

int main() {
    // initialize stdio for usb communication
    stdio_init_all();

    // initialize the LED GPIO pin
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    launch_core1((void *)core1_main);

    while (1) {
        gpio_put(LED_PIN, 0);
        sleep_ms(250);
        gpio_put(LED_PIN, 1);
        puts("Hello World\n");
        sleep_ms(1000);
    }
}

