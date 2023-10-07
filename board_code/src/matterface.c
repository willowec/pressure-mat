
#include "matterface.h"
#include "hardware/gpio.h"
#include "pico/stdlib.h"


void initialize_shreg_pins()
{
    gpio_init(SH_CLK_PIN);
    gpio_set_dir(SH_CLK_PIN, GPIO_OUT);

    gpio_init(SH_CLR_PIN);
    gpio_set_dir(SH_CLR_PIN, GPIO_OUT);

    gpio_init(SH_SERIN_PIN);
    gpio_set_dir(SH_SERIN_PIN, GPIO_OUT);

    gpio_init(SH_SEROUT_PIN);
    gpio_set_dir(SH_SEROUT_PIN, GPIO_IN);
}

void shift_shreg(int inval)
{
    // write the serial input value to serial
    gpio_put(SH_SERIN_PIN, inval);

    // clock the shift registers once
    gpio_put(SH_CLK_PIN, 1);
    sleep_us(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLK_PIN, 0);
}

void clear_shreg()
{
    // flicker the clear pin
    gpio_put(SH_CLR_PIN, 1);
    sleep_us(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLR_PIN, 0);
}

void read_mat(uint8_t *mat) 
{
    /*
    to read the mat:
        1. Clear the shift registers
        2. Shift a 1 into the start of the shift registers
        3. Until finished: Read every column via the ADC's and shift the bit forward by 1
    */
    int i;
    
    for (i = 0; i < COL_HEIGHT; i++) {

    }
}
