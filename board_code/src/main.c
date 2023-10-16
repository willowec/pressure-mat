/*

main.c file for the RP2040 code for the pressure matrix project

*/

#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "pico/multicore.h"

#include "transmitter.h"
#include "adc.h"
#include "matterface.h"

#define LED_PIN         25


int main() {
    initialize_transmitter();

    // Delay with some LED blinking on startup
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    for (int i = 0; i < 5; i++) {
        sleep_ms(500);
        gpio_put(LED_PIN, 0);
        sleep_ms(1000);
        gpio_put(LED_PIN, 1);
    }

    uint8_t *mat = (uint8_t *)malloc(MAT_SIZE);
    for (int i=0; i < MAT_SIZE; i++) {
        mat[i] = (i + '0') % (255);
    }

    uint8_t *row = (uint8_t *)calloc(ROW_WIDTH, 1);

    // initialize the adcs
    struct adc_inst *adc1 = malloc(sizeof(struct adc_inst));
    struct adc_inst *adc2 = malloc(sizeof(struct adc_inst));
    initialize_adcs(adc1, adc2);

    // initialize the shift registers
    initialize_shreg_pins();

    while (1) {
        sleep_ms(1000);

        printf("Reading mat...\n");
        read_mat(mat, adc1, adc2);
        transmit_mat(mat);
        //prettyprint_mat(mat);

    }

    free(mat);
    free(row);

    return 1;   // should never exit
}