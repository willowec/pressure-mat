
#include <stdio.h>
#include <stdbool.h>

#include "hardware/gpio.h"
#include "pico/stdlib.h"

#include "matterface.h"
#include "transmitter.h"


// For the interrupt-based mat read to function, some global variables are required
queue_t *mat_queue_ptr;
uint8_t row_data[ROW_WIDTH] = {-1};
struct queueItem row_item;

int column;
struct adc_inst *adc1_instance;
struct adc_inst *adc2_instance;
bool waiting_for_adc1;
bool waiting_for_adc2;
volatile bool reading_mat;  // must be volatile for global changes


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

    // make sure the shift registers are initialized to zero
    clear_shreg();
}

void shift_shreg(int inval)
{
    // write the serial input value to serial
    gpio_put(SH_SERIN_PIN, inval);

    // clock the shift registers once
    gpio_put(SH_CLK_PIN, 1);
    busy_wait_us_32(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLK_PIN, 0);
}

void clear_shreg()
{
    // flicker the clear pin
    gpio_put(SH_CLR_PIN, 0);
    busy_wait_us_32(SHREG_GPIO_SLEEP_US);
    gpio_put(SH_CLR_PIN, 1);
}

/*
    Callback function that is triggered by either of the EOC pins going low.
*/
void EOC_callback(uint gpio, uint32_t events) 
{
    if (!reading_mat) {
        return;   // do not process events if not reading the mat
    } 

    /* 
     * An EOC pin just went low! Let's handle this
     * 1. for the EOC pin:
     *  1.1. read results from corresponding ADC
     *  1.2. insert results into the proper point in mat_ptr
     *  1.3. set waiting_for_adcx to false
     * 2. if waiting_for_adc1 and waiting_for_adc2 are both false:
     *  2.1. shift the shregs
     *  2.2. inc column
     *  2.3. request a new conversion from both ADCs
     */

    int i;

    // define a temp array for storing and processing the values returned from the ADCs
    uint8_t *resp = (uint8_t *)malloc(ADC_RESPONSE_LENGTH);

    // step 1
    if (gpio == ADC1_EOC_PIN) {
        // handle ADC1 results
        waiting_for_adc1 = false;

        // read the conversion results
        adc_read_blocking(adc1_instance, 0, resp, ADC_RESPONSE_LENGTH);
        cleanup_adc_response(resp, row_data);
    }
    else if (gpio == ADC2_EOC_PIN) {
        // handle ADC2 results
        waiting_for_adc2 = false;

        // read the conversion results
        adc_read_blocking(adc2_instance, 0, resp, ADC_RESPONSE_LENGTH);
        cleanup_adc_response(resp, row_data + CHANNELS_PER_ADC);
    }

    // step 2
    if ((!waiting_for_adc1) && (!waiting_for_adc2)) {
        // Both adc's have been read! push the row data onto the queue
        row_item.row_data = row_data;
        queue_add_blocking(mat_queue_ptr, &row_item);

        shift_shreg(0);
        column++;

        // if column == COL_HEIGHT, then we are finished and should not send more readings
        if (column == COL_HEIGHT) {
            reading_mat = false;
        }
        else {
            // delay before the next ADC request set
            busy_wait_us_32(ADC_READ_SLEEP_US); // cannot call sleep_us within interrupt handlers

            // request all channels from both ADCs
            waiting_for_adc1 = true;
            waiting_for_adc2 = true;
            uint8_t conv_req = 0b10000000 | ((CHANNELS_PER_ADC - 1) << 3);
            adc_write_blocking(adc1_instance, &conv_req, 1);
            adc_write_blocking(adc2_instance, &conv_req, 1);
        }
    }

    free(resp);
}

void initialize_EOC_interrupts() 
{
    reading_mat = false;

    // set up both EOC pins to trigger a callback on falling edge (falling edge occurs when the ADC completes its read)   
    gpio_set_irq_enabled_with_callback(ADC1_EOC_PIN, GPIO_IRQ_EDGE_FALL, true, &EOC_callback);
    gpio_set_irq_enabled(ADC2_EOC_PIN, GPIO_IRQ_EDGE_FALL, true);
}

void read_mat(queue_t *mat_queue, struct adc_inst *adc1, struct adc_inst *adc2)
{
    // start with a one in the shregs
    shift_shreg(1); // shift in a one
    shift_shreg(0); // move the one to the output line

    // set up the global variables for interrupt handling
    mat_queue_ptr = mat_queue;
    adc1_instance = adc1;
    adc2_instance = adc2;
    
    waiting_for_adc1 = false;
    waiting_for_adc2 = false;

    column = 0;

    // indicate that a read is currently happening
    reading_mat = true;

    // do one initial wait for good measure
    sleep_us(ADC_READ_SLEEP_US);

    // send the first ADC read requests to get things started
    // write a conversion request in scan mode 00 for channels 0 -> (CHANNELS_PER_ADC - 1), for CHANNELS_PER_ADC total channels
    uint8_t conv_req = 0b10000000 | ((CHANNELS_PER_ADC - 1) << 3);
    adc_write_blocking(adc1_instance, &conv_req, 1);
    adc_write_blocking(adc2_instance, &conv_req, 1);

    // now just busy-wait until the mat is completely read.
    int i = 0;
    while(reading_mat) 
        i++;
    
    //printf("Waited %d cycles for mat to finish reading\n", i);

    return;
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