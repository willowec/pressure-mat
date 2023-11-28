/*
    C file responsible for sending data over serial usb to the computer
*/

#include <stdbool.h>
#include <string.h>

#include "hardware/gpio.h"

#include "transmitter.h"


int parse_input(char *string)
{
    // check if the command to start reading the mat has been issued
    if (!strncmp(string, START_READING_COMMAND, sizeof(string))) {
		// start reading the mat
        return START_READING_COMMAND_ID;
	}
    else if (!strncmp(string, GET_CAL_VALS_COMMAND, sizeof(string))) {
        return GET_CAL_VALS_COMMAND_ID;
    }
    else if (!strncmp(string, PRINT_INFO_COMMAND, sizeof(string))) {
        return PRINT_INFO_COMMAND_ID;
    }
    else {
        return -1;  // no valid command read
    }
}

// definition of initialize
void initialize_transmitter()
{
    // enable UART printfs
    stdio_init_all();
}

// definition of send_row
void transmit_row(uint8_t *row)
{
    // transmits one row over serial in hexadecimal format
    int i;
    for (i = 0; i < ROW_WIDTH; i++) {
        printf("%02x", row[i]);
    }

    // does not close with newline: to finish transmission, send a newline
}

// definition of send_mat
void transmit_mat(uint8_t *mat)
{
    // transmit the data over serial in hexadecimal format
    int i;
    for (i = 0; i < MAT_SIZE; i++) {
        printf("%02x", mat[i]);
    }
    putchar('\n');
}

