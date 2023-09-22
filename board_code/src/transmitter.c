/*
    C file responsible for sending data over serial usb to the computer
*/

#include "transmitter.h"


// definition of initialize
void initialize_transmitter()
{
    // enable UART printfs
    stdio_init_all();
}

// definition of send_row
void transmit_row(uint8_t *row)
{
    fwrite(row, 1, ROW_WIDTH, stdout);
    fflush(stdout);
}

// definition of send_mat
void transmit_mat(uint8_t *mat)
{
    fwrite(mat, 1, MAT_SIZE, stdout);
    fflush(stdout);
}

