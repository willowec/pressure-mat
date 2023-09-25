/*
Header file responsible for communicating via spi to the two ADC's of the project
This code is written assuming that the ADC's are max11643 chips
*/
#ifndef ADC_HEADER
#define ADC_HEADER

#include <stdint.h>
#include "hardware/spi.h"

#define CHANNELS_PER_ADC    14  // 14 pins of the adc's each are connected to the mat

#define SPI0_SCK_PIN        2
#define SPI0_TX_PIN         3
#define SPI0_RX_PIN         4

#define ADC1_EOC_PIN        0
#define ADC2_EOC_PIN        1
#define ADC1_CS_PIN         6
#define ADC2_CS_PIN         7

struct adc_inst {
    uint8_t cs_pin;
    uint8_t eoc_pin;
}

/*
    Initializes the spi channel used to talk to the ADCs, and calles initialze_adc() for both of them
*/
void initialize_adcs();

/*
    Initializes an ADC (sets setup register values, etc)
*/
void initialize_adc(adc_inst *adc);

/*
    Gets from 0 to CHANNELS_PER_ADC channels of the adc_inst 'adc' and writes their values to 'out_vals'
*/
void get_adc_values(struct adc_inst* adc, uint8_t *out_vals);



#endif