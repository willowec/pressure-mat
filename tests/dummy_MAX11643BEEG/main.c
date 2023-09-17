/*

main.c file for the dummy MAX11643BEEG ADC

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