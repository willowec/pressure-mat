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

    uint8_t *mat = (uint8_t *)calloc(MAT_SIZE, sizeof(uint8_t));

    // initialize the adcs 
    struct adc_inst *adc1 = malloc(sizeof(struct adc_inst));
    struct adc_inst *adc2 = malloc(sizeof(struct adc_inst));
    initialize_adcs(adc1, adc2, true);  // true for dual_channel mode

    // initialize the shift registers
    initialize_shreg_pins();

    // intiialize the matterface eoc interrupts
    initialize_EOC_interrupts();

    // Parse commands from the GUI before entering a session
	char input_string[256];
	uint32_t input_pointer, ch, parsed_command;
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

        parsed_command = parse_input(input_string);
        if (parsed_command == START_READING_COMMAND_ID) {
            // break the input loop to move to the main loop and start reading the mat
            gpio_put(LED_PIN, 0);
            break;    
        }
        else if (parsed_command == GET_CAL_VALS_COMMAND_ID) {
            // perform one read of the mat and transmit it to the GUI
            read_mat(mat, adc1, adc2);
            printf("Exited after finishing reading the mat\n");
            transmit_mat(mat);
        } 
        else if (parsed_command == PRINT_INFO_COMMAND_ID) {
            // print code info
            printf("This is PressureMat software for board v2!\n");
        } 
        else {
            printf("Unrecognized command\n");
        }
    }
    
    while (1) {
        sleep_ms(900);
        
        // indicate read is occuring by flashing led
        gpio_put(LED_PIN, 1);
        read_mat(mat, adc1, adc2);
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        //prettyprint_mat(mat);
        transmit_mat(mat);
    }

    free(mat);

    return 1;   // should never exit
}