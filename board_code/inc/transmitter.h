#ifndef TRANSMITTER
#define TRANSMITTER

#include <stdio.h>
#include <stdint.h>
#include "pico/stdlib.h"


#define ROW_WIDTH   28
#define COL_HEIGHT  56
#define MAT_SIZE    1568


/*
    Function responsible for initializing the transmitter
*/
void initialize_transmitter();

/*
    Function which transmits one row of the mat (28, 8-bit values) over serial USB to the connected computer
*/
void transmit_row(uint8_t *row);


/*
    Function which transmits a full mat image (56 x 28, 8-bit values) over serial USB
*/
void transmit_mat(uint8_t *mat);


#endif