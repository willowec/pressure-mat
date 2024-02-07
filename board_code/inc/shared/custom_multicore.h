/*
A simple multicore library for the RP2040 created for Willow Cunningham and Evan Desmond's capstone project
*/

#include <stdint.h>

// Use the same default stack size as the pico multicore library
#define CORE1_STACK_SIZE    0x800

// we can grab the stack pointer for core1 from the ld file by using extern
extern const uint32_t __StackOneBottom[];

/*
unoptimizable function for use with empty while loops
*/
static __force_inline void nop(void) {}

/*
launches core 1 at the entrypoint
*/
void launch_core1(void (*entrypoint)(void));

/*
Pushes a 32 bit value onto the multicore write fifo. Blocks until there is space on the FIFO
For communications other than these nescesary to launch core 1, it is best to use a queue instead of the FIFO
see note here: https://www.raspberrypi.com/documentation/pico-sdk/high_level.html#multicore_fifo 
*/
void multicore_fifo_push(uint32_t data);

/*
Pops a 32 bit value off of the multicore read fifo. Blocks until there is data to pop
*/
uint32_t multicore_fifo_pop(void);


/*
Empties the read fifo
*/
void multicore_fifo_drain(void);