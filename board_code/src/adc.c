#include "adc.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

#include <stdio.h>

void initialize_adcs(struct adc_inst *adc1, struct adc_inst *adc2)
{
    // initialize the spi channels
    spi_init(spi0, SPI_CLOCKSPEED);
    gpio_set_function(SPI0_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_TX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_RX_PIN, GPIO_FUNC_SPI);

    // set up the adc1 and adc2 structs
    adc1->cs_pin = ADC1_CS_PIN;
    adc1->eoc_pin = ADC1_EOC_PIN;
    adc2->cs_pin = ADC2_CS_PIN;
    adc2->eoc_pin = ADC2_EOC_PIN;

    // start the CS pins in not selected mode
    gpio_init(adc1->cs_pin);
    gpio_set_dir(adc1->cs_pin, GPIO_OUT);
    gpio_put(adc1->cs_pin, CS_DESELECT);
    gpio_init(adc2->cs_pin);
    gpio_set_dir(adc2->cs_pin, GPIO_OUT);
    gpio_put(adc2->cs_pin, CS_DESELECT);

    // send the setup register messages to each adc
    initialize_adc(adc1);
    initialize_adc(adc2);
}


void initialize_adc(struct adc_inst *adc)
{
    // setup the ADC's epc pin
    gpio_init(adc->eoc_pin);
    gpio_set_dir(adc->eoc_pin, GPIO_IN);

    // setup to configure: clock mode 10 (spi) and ref mode 01 (external)
    // 01   10  01  dd
    uint8_t setup_message = 0b01100100;
    adc_write_blocking(adc, &setup_message, 1);
}


void get_adc_values(struct adc_inst* adc, uint8_t *out_vals)
{
    // write a conversion request in scan mode 00 for channels 0 -> (CHANNELS_PER_ADC - 1), for CHANNELS_PER_ADC total channels
    uint8_t conv_req = 0b10000000 | ((CHANNELS_PER_ADC - 1) << 3);
    adc_write_blocking(adc, &conv_req, 1);

    // wait for EOCbar (end of conversion) to go low, indicating that the operation has finished and data will now be written back
    // TODO: Change to use interrupts so that both ADC's can do conversions at the same time?
    uint32_t i = 0;
    while (gpio_get(adc->eoc_pin))
        i ++;
    
    //printf("Waited %d cycles for EOC\n", i);

    // read the conversion results
    adc_read_blocking(adc, 0, out_vals, CHANNELS_PER_ADC);
}


void adc_write_blocking(struct adc_inst* adc, uint8_t *src, size_t len)
{
    // enable the CS pin to talk to the adc
    gpio_put(adc->cs_pin, CS_SELECT);
    sleep_us(1);
    spi_write_blocking(spi0, src, len);

    // disable the CS pin
    sleep_us(1);
    gpio_put(adc->cs_pin, CS_DESELECT);
}


void adc_read_blocking(struct adc_inst* adc, uint8_t repeated_tx_data, uint8_t *dst, size_t len)
{
    // enable the CS pin to talk to the adc
    gpio_put(adc->cs_pin, CS_SELECT);
    sleep_us(1);

    spi_read_blocking(spi0, repeated_tx_data, dst, len);

    // disable the CS pin
    sleep_us(1);
    gpio_put(adc->cs_pin, CS_DESELECT);
}