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
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        sleep_ms(100);
        gpio_put(LED_PIN, 1);
    }

    uint8_t *mat = (uint8_t *)malloc(MAT_SIZE);

    // initialize the adcs
    struct adc_inst *adc1 = malloc(sizeof(struct adc_inst));
    struct adc_inst *adc2 = malloc(sizeof(struct adc_inst));
    initialize_adcs(adc1, adc2);

    // initialize the shift registers
    initialize_shreg_pins();

    
    // wait until the start reading command is issued
	char input_string[256];
	uint32_t input_pointer, ch;
    while(1) {
        input_pointer = 0;
        while(1) {
            ch=getchar();
            if ((ch=='\n') || (ch=='\r')) {
                input_string[input_pointer]=0;
                break;
            }
			input_string[input_pointer]=ch;
			input_pointer++;
        }
        if (parse_input(input_string)) {
            gpio_put(LED_PIN, 0);
            break;    
        }
    }
    
    while (1) {
        sleep_ms(2000);

        
        // indicate read is occuring by flashing led
        gpio_put(LED_PIN, 1);
        printf("Beginning read\n");
        read_mat(mat, adc1, adc2);
        printf("Exited read\n");
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        //prettyprint_mat(mat);
        sleep_ms(100);
        printf("Transmitting mat\n");
        transmit_mat(mat);
        printf("Finished transmitting mat\n");
    }

    free(mat);

    return 1;   // should never exit
}