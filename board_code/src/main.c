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

#define LED_PIN         25


int main() {
    initialize_transmitter();

    uint8_t *mat = (uint8_t *)malloc(MAT_SIZE);
    for (int i=0; i < MAT_SIZE; i++) {
        mat[i] = (i + '0') % (255);
    }

    uint8_t *row = (uint8_t *)malloc(ROW_WIDTH);

    // initialize the adcs
    struct adc_inst *adc1 = malloc(sizeof(struct adc_inst));
    struct adc_inst *adc2 = malloc(sizeof(struct adc_inst));
    initialize_adcs(adc1, adc2);

    while (1) {
        sleep_ms(1000);

        // read from both adc's
        printf("Reading adc values\n");
        get_adc_values(adc1, row);
        get_adc_values(adc2, row + CHANNELS_PER_ADC);

        transmit_row(row);
    }

    free(mat);
    free(row);
}