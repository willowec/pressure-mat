/*

main.c file for the dummy MAX11643BEEG ADC

*/

#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "pico/multicore.h"

#define LED_PIN         25

#define SPI0_SCK_PIN    2
#define SPI0_TX_PIN     3
#define SPI0_RX_PIN     4
#define SPI0_CSN_PIN    5
#define SPI1_SCK_PIN    10
#define SPI1_TX_PIN     11
#define SPI1_RX_PIN     12
#define SPI1_CSN_PIN    13

#define CLOCK_SPEED 1000000 // 1MHz

#define N_ADC_VALUES 256
uint8_t ADC_VALUES[N_ADC_VALUES] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 
                            0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 
                            0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 
                            0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0x42, 0x43, 
                            0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x53, 0x54, 
                            0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 
                            0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 
                            0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 
                            0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 
                            0x99, 0x9a, 0x9b, 0x9c, 0x9d, 0x9e, 0x9f, 0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 
                            0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 
                            0xbb, 0xbc, 0xbd, 0xbe, 0xbf, 0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 
                            0xcc, 0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xdb, 0xdc, 
                            0xdd, 0xde, 0xdf, 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 
                            0xee, 0xef, 0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff};
/*
    Generates n_values bytes of ADC readings and writes them to the array at out
*/
void generate_ADC_values(uint8_t *out, int n_values) {
    static uint32_t values_idx = 0;  // index into the ADC values array

    for (int i = 0; i < n_values; i++) {
        values_idx = (values_idx + 1) % N_ADC_VALUES;
        out[i] = ADC_VALUES[values_idx];
    }
}


/*
    Prints a buffer
*/
void print_buffer(uint8_t *buf, size_t len) {
    for (int i = 0; i < len; i++) {
        printf("%02x ", buf[i]);
    }
    printf("\n");
}

/*
    Function which processes the input data byte which has been sent over SPI
    See page 13 of the datasheet linked in the Readme for details
*/
void process_input_byte(uint8_t byte) {
    printf("ADC recieved: %d\n", byte);

    if ((byte >> 7) == 1) {
        // 1XXXXXXX means Conversion register
        printf("ADC says: conversion register | %d\n", (byte >> 7));

        uint8_t *buf;

        // handle scan mode 00
        if ((byte & 0b00000110) == 0) {
            // scan channels 0 - N (return N generated values)
            size_t n = (((byte) & 0b01111000) >> 3) + 1; // read N from CHSEL3-CHSEL0 in the input data byte

            buf = (uint8_t *)malloc(n);
            generate_ADC_values(buf, n);

            printf("ADC generated: "); 
            print_buffer(buf, n);

            // write the adc values back over SPI
            spi_write_blocking(spi0, buf, n);

            free(buf);
        }
    }
    else if ((byte >> 6) == 1) {
        // 01XXXXXX means Setup register
        printf("ADC says: setup register | %d\n", (byte >> 6));

    }
    else if ((byte >> 5) == 1) {
        // 001XXXXX means Averaging register
        printf("ADC says: averaging register | %d\n", (byte >> 5));

    }
    else if ((byte >> 4) == 1) {
        // 0001XXXX means Reset register
        printf("ADC says: reset register | %d\n", (byte >> 4));

    }
    else {
        // Invalid input byte
        printf("ADC says: invalid input byte\n");
    }
}

/*
    Sends an input data byte over SPI to the "adc" requesting a conversion. 
        chsel - 4 bits corresponding to CHSEL3, CHSEL2, CHSEL1, CHSEL0 from the datasheet
*/
void request_conversion(uint8_t chsel) {
    uint8_t outbuf = 0b10000000 | (chsel << 3);
    uint8_t inbuf[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

    printf("Requesting conversion %x\n", chsel);
    spi_write_blocking(spi1, &outbuf, 1);

    sleep_ms(10);

    spi_read_blocking(spi1, 0, inbuf, chsel + 1);

    printf("Conversion recieved:\n");
    print_buffer(inbuf, chsel + 1);

}


/*
    Second core: controller spi
*/
void core1_main() {
    // initialize SPI1 as a controller
    spi_init(spi1, CLOCK_SPEED);
    gpio_set_function(SPI1_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_TX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_CSN_PIN, GPIO_FUNC_SPI);

    while(1) {
        // Main loop. Make conversion requests here!

        request_conversion(0b1111); // request 16 values
        sleep_ms(1000);
    }
}

/*
    First core: fake ADC
*/
int main () {
    // enable UART printfs
    stdio_init_all();

    // Blink the board led to indicate booting was successful
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    for (int i = 0; i < 5; i++) {
        sleep_ms(500);
        gpio_put(LED_PIN, 0);
        sleep_ms(250);
        gpio_put(LED_PIN, 1);
    }

    // initialize SPI0 as a client
    spi_init(spi0, CLOCK_SPEED);
    spi_set_slave(spi0, true);
    gpio_set_function(SPI0_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_TX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_CSN_PIN, GPIO_FUNC_SPI);

    // launch the second core
    multicore_launch_core1(core1_main);


    uint8_t input_byte;

    // main loop
    while (1) {
        // read one byte from SPI
        spi_read_blocking(spi0, 0, &input_byte, 1);

        // handle the input
        process_input_byte(input_byte);
    }
}