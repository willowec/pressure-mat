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

#define LED_PIN         25

#define SPI0_SCK_PIN    2
#define SPI0_TX_PIN     3
#define SPI0_RX_PIN     4
#define SPI0_CSN_PIN    5
#define SPI1_SCK_PIN    10
#define SPI1_TX_PIN     11
#define SPI1_RX_PIN     12
#define SPI1_CSN_PIN    13


int main() {
    initialize_transmitter();

    uint8_t *mat = (uint8_t *)malloc(MAT_SIZE);
    for (int i=0; i < MAT_SIZE; i++) {
        mat[i] = (i + '0') % (255);
    }

    while (1) {
        sleep_ms(1000);
        transmit_mat(mat);
    }
}