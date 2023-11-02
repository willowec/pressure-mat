
#include "hardware/structs/sio.h"

#include "custom_multicore.h"


void launch_core1(void (*entrypoint)(void))
{
    // grab the stack pointer
    uint32_t *stack_bottom = (uint32_t *)__StackOneBottom;
    uint32_t *stack_ptr = stack_bottom + sizeof(stack_bottom) / sizeof(uint32_t);

    stack_ptr[0] = (uintptr_t) entrypoint;
    stack_ptr[1] = (uintptr_t) stack_bottom;

}

void multicore_fifo_push(uint32_t data)
{
    // Wait for the write fifo of this core to be ready
    /* 
        see https://github.com/raspberrypi/pico-sdk/blob/master/src/rp2040/hardware_structs/include/hardware/structs/sio.h,
        from this, we can see that the FIFIO_WR register offset is 0x00000054.
        as for _REG_ and _u, _REG_ does nothing and _u just appends the 'u' suffix to make a number unsigned.
        However, it is probably best to just use their existing register interface code by including sio.h
    */
    while((sio_hw->fifo_st & SIO_FIFO_ST_RDY_BITS) == 0) {
        nop();
    }

    // push the data onto the fifo
    sio_hw->fifo_wr = data;

    // fire an event to both cores
    __asm volatile ("sev");
}