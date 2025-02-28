/*
Mat interface code for V1 of the PMI software
*/

#include <stdio.h>

#include "hardware/gpio.h"
#include "pico/stdlib.h"

#include "matterface.h"

void initialize_shreg_pins()
{
    // set up shift register control GPIO pins
    gpio_init(SH_CLK_PIN);
    gpio_set_dir(SH_CLK_PIN, GPIO_OUT);

    gpio_init(SH_CLR_PIN);
    gpio_set_dir(SH_CLR_PIN, GPIO_OUT);

    gpio_init(SH_SERIN_PIN);
    gpio_set_dir(SH_SERIN_PIN, GPIO_OUT);

    gpio_init(SH_SEROUT_PIN);
    gpio_set_dir(SH_SEROUT_PIN, GPIO_IN);

    // make sure the shift registers are initialized to zero
    clear_shreg();
}

void shift_shreg(int inval)
{
    // write the next value into the shift registers
    gpio_put(SH_SERIN_PIN, inval);

    // clock the shift registers once
    gpio_put(SH_CLK_PIN, 1);
    sleep_us(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLK_PIN, 0);
}

void clear_shreg()
{
    // flicker the clear pin of the shift registers to wipe their memory
    gpio_put(SH_CLR_PIN, 0);
    sleep_us(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLR_PIN, 1);
}

void read_mat(uint8_t *mat, struct adc_inst *adc1, struct adc_inst *adc2)
{
    /*
    to read the mat:
        1. Shift a 1 into the start of the shift registers
        2. Until finished: Read every column via the ADC's, and shift the bit forward by 1
    */
    int i;

    // start with a one in the shregs
    shift_shreg(1); // shift in a one
    shift_shreg(0); // move the one to the output line

    for (i = 0; i < COL_HEIGHT; i++) {
        sleep_ms(4);    // to meet spec, needs to take under (250ms / 56rows = 4.464ms per row)

        // read from both adcs
        get_adc_values(adc1, mat + (i * ROW_WIDTH));
        get_adc_values(adc2, mat + (i * ROW_WIDTH) + CHANNELS_PER_ADC);

        // finally, shift the bit forward in the shregs
        shift_shreg(0);
    }
}

void prettyprint_mat(uint8_t *mat)
{
    int i;
    for (i = 0; i < MAT_SIZE; i++)
    {
        if ((i % ROW_WIDTH) == 0) {
            printf("\b  \n");   // on every row, clear the trailing comma and add a newline
        }

        printf("%02x, ", mat[i]);
    }

    printf("\b  \n");
}