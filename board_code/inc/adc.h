/*
Header file responsible for communicating via spi to the two ADC's of the project
This code is written assuming that the ADC's are max11643 chips
*/
#ifndef ADC_HEADER
#define ADC_HEADER

#include <stdint.h>
#include "hardware/spi.h"

#define ADC_RESPONSE_LENGTH 28
#define CHANNELS_PER_ADC    14  // 14 pins of the adc's each are connected to the mat

#define SPI0_SCK_PIN        2
#define SPI0_TX_PIN         3
#define SPI0_RX_PIN         4

#define SPI_CLOCKSPEED      1000000 // 1MHz
#define CS_SELECT           0
#define CS_DESELECT         1

#define ADC1_EOC_PIN        0
#define ADC2_EOC_PIN        1
#define ADC1_CS_PIN         6
#define ADC2_CS_PIN         7


struct adc_inst {
    uint8_t cs_pin;
    uint8_t eoc_pin;
};

/*
    Initializes the spi channel used to talk to the ADCs, and calles initialze_adc() for both of them
*/
void initialize_adcs(struct adc_inst *adc1, struct adc_inst *adc2);

/*
    Initializes an ADC (sets setup register values, etc)
*/
void initialize_adc(struct adc_inst *adc);

/*
    Gets from 0 to CHANNELS_PER_ADC channels of the adc_inst 'adc' and writes their values to 'out_vals'
*/
void get_adc_values(struct adc_inst* adc, uint8_t *out_vals);

/*
    Wraps spi_write_blocking to communcicate with an adc
*/
void adc_write_blocking(struct adc_inst* adc, uint8_t *src, size_t len);

/*
    Wraps spi_read_blocking to communcicate with an adc
*/
void adc_read_blocking(struct adc_inst* adc, uint8_t repeated_tx_data, uint8_t *dst, size_t len);

#endif