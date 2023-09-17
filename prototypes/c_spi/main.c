/*

C SPI example
made with code from this digikey tutorial:
https://www.digikey.com/en/maker/projects/raspberry-pi-pico-rp2040-spi-example-with-micropython-and-cc/9706ea0cf3784ee98e35ff49188ee045

*/

#include <stdio.h>
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

#define BUF_LEN         0x100

void printbuf(uint8_t buf[], size_t len) {
    int i;
    for (i = 0; i < len; i++) {
        if (i % 16 == 15)
            printf("%02x\n", buf[i]);
        else
            printf("%02x ", buf[i]);
    }

    // append trailing newline if one was missed
    if (i % 16) {
        putchar('\n');
    }
}

// main function for the second core
void core1_main() {
    printf("hello world from core 2\n");

    // initialize SPI1 as a controller
    spi_init(spi1, 1000000);  // clock at 1MHz
    gpio_set_function(SPI1_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_TX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI1_CSN_PIN, GPIO_FUNC_SPI);

    uint8_t out_buf[BUF_LEN], in_buf[BUF_LEN];

    // Initialize the output buffer
    for (size_t i = 0; i < BUF_LEN; i++) {
        out_buf[i] = i;
    }

    for(size_t i = 0; ; i++) {
        printf("Reading/writing as controller\n");
        // write the buffer to MOSI, and read from MISO at the same time
        spi_write_read_blocking(spi1, out_buf, in_buf, BUF_LEN);
        //printf("read as controller:\n");
        //printbuf(in_buf, BUF_LEN);

        // sleep for a seconds
        sleep_ms(1000);
    }
}

int main() {
    stdio_init_all();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    // do a bit of a blinky
    for (int i = 0; i < 5; i++) {
        sleep_ms(500);
        gpio_put(LED_PIN, 0);
        sleep_ms(250);
        gpio_put(LED_PIN, 1);
    }

    multicore_launch_core1(core1_main);
    printf("hello world from core 1\n");

    // initialize SPI0 as a client
    spi_init(spi0, 1000000);  // clock at 1MHz
    spi_set_slave(spi0, true);
    gpio_set_function(SPI0_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_TX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI0_CSN_PIN, GPIO_FUNC_SPI);

    uint8_t out_buf[BUF_LEN], in_buf[BUF_LEN];

    // initialize the output buffer
    for (size_t i = 0; i < BUF_LEN; i++) {
        out_buf[i] = ~i;
    }

    for (size_t i = 0; ; i++) {
        // Write the output to MISO, and at the same time read from MOSI
        printf("reading/writing as client\n");

        spi_write_read_blocking(spi0, out_buf, in_buf, BUF_LEN);

        
        // Write to stdio hatever came in from MOSI
        printf("Spi client says: read page %d from the MOSI line:\n", i);
        printbuf(in_buf, BUF_LEN);
    }
}