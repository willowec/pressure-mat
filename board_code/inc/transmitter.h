/*
Header file responsible for communicating via USB serial connection to the connected computer
*/

#ifndef TRANSMITTER_HEADER
#define TRANSMITTER_HEADER

#include <stdio.h>
#include <stdint.h>
#include "matterface.h"
#include "pico/stdlib.h"




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