/*

C SPI example
made with code from this digikey tutorial:
https://www.digikey.com/en/maker/projects/raspberry-pi-pico-rp2040-spi-example-with-micropython-and-cc/9706ea0cf3784ee98e35ff49188ee045

*/

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "pico/multicore.h"

// main function for the second core
void core1_main() {
    while (1) {
        printf("Code running on the second core\n");
        sleep_ms(1000);
    }
}

int main() {
    stdio_init_all();

    multicore_launch_core1(core1_main);
    printf("hello world\n");


    uint32_t i = 0;

    while (1)
    {
        printf("hello nice %u\n", i++);
        sleep_ms(1000);
    }
}