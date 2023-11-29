
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"
#include "transmitter.h"

#define LED_PIN  25


uint8_t row[28] = {0};


int main() {
    // initialize stdio for usb communication
    stdio_init_all();

    // initialize the LED GPIO pin
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    int i = 0;
    int j = 0;

    while (1) {
        gpio_put(LED_PIN, 0);
        sleep_ms(500);
        gpio_put(LED_PIN, 1);

        // feed in row
        for (i = 0; i < 28; i++) {
            row[i] = j;
            j = (j + 1) % 256;
        }

        transmit_row(row);
        sleep_ms(500);
    }
}

