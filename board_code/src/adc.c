#include "adc.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

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

    // send the setup register messages to each adc
    initialize_adc(adc1);
    initialize_adc(adc2);
}


void initialize_adc(struct adc_inst *adc)
{
    // TODO: Complete this function

    // setup to configure: clock mode 10 (spi) and ref mode 00 (internal, no wakeup)
    // 01   10  00  dd
    uint8_t setup_message = 0b01100000;

    spi_write_blocking(spi0, &setup_message, 1);
    spi_write_blocking(spi0, &setup_message, 1);
}


void get_adc_values(struct adc_inst* adc, uint8_t *out_vals)
{
    // write a conversion request for cahnnels 0 - CHANNELS_PER_ADC
    uint8_t conv_req = 0b10000000 | (CHANNELS_PER_ADC << 1);
    adc_write_blocking(adc, &conv_req, 1);

    // wait for EOCbar (end of conversion) to go low, indicating that the operation has finished and data will now be written back
    // TODO: Change to use interrupts so that both ADC's can do conversions at the same time?
    while (gpio_get(adc->eoc_pin));

    // read the conversion results
    adc_read_blocking(adc, 0, out_vals, CHANNELS_PER_ADC);
}


void adc_write_blocking(struct adc_inst* adc, uint8_t *src, size_t len)
{
    // enable the CS pin to talk to the adc
    gpio_put(adc->cs_pin, 1);

    spi_write_blocking(spi0, src, len);

    // disable the CS pin
    gpio_put(adc->cs_pin, 0);
}


void adc_read_blocking(struct adc_inst* adc, uint8_t repeated_tx_data, uint8_t *dst, size_t len)
{
    // enable the CS pin to talk to the adc
    gpio_put(adc->cs_pin, 1);

    spi_read_blocking(spi0, repeated_tx_data, dst, len);

    // disable the CS pin
    gpio_put(adc->cs_pin, 0);
}