/*
Header file responsible for communicating via USB serial connection to the connected computer
*/

#ifndef TRANSMITTER_HEADER
#define TRANSMITTER_HEADER

#include <stdio.h>
#include <stdint.h>
#include "matterface.h"
#include "pico/stdlib.h"


#define START_READING_COMMAND   "start_reading"
#define GET_CAL_VALS_COMMAND    "get_cal_vals"
#define PRINT_INFO_COMMAND      "print_info"

#define START_READING_COMMAND_ID    1
#define GET_CAL_VALS_COMMAND_ID     2
#define PRINT_INFO_COMMAND_ID       3

#define TRANSMIT_SLEEP_US           1000  // amount of time to sleep between transmissions

// Each queueItem contains one row of the mat
typedef struct queueItem {
  uint8_t *row_data;
} item;

/*
    Function which takes a string that has passed over serial and decides what to do based on it
*/
int parse_input(char *string);


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