
#include "hardware/structs/sio.h"
#include "hardware/structs/scb.h"
#include "hardware/irq.h"

#include "custom_multicore.h"


void launch_core1(void (*entrypoint)(void))
{
    // grab the stack pointer
    uint32_t *stack_bottom = (uint32_t *)__StackOneBottom;
    uint32_t *stack_ptr = stack_bottom + sizeof(stack_bottom) / sizeof(uint32_t);

    stack_ptr[0] = (uintptr_t) entrypoint;
    stack_ptr[1] = (uintptr_t) stack_bottom;

    // disable the fifo irq for this operation
    bool enabled = irq_is_enabled(SIO_IRQ_PROC0);
    irq_set_enabled(SIO_IRQ_PROC0, false);

    // a sequence of FIFO values that will start up core1
    const uint32_t sequence[6] = {0, 0, 1, (uintptr_t) scb_hw->vtor, (uintptr_t) stack_ptr, (uintptr_t) entrypoint};

    // transmit the command sequence that starts up core1
    uint32_t i = 0;
    while(i < 6) {
        if (sequence[i] == 0) {
            // according to the rpi multicore library, "Always drain the READ FIFO (from core 1) before sending a 0"
            multicore_fifo_drain();
        }

        multicore_fifo_push(sequence[i]);
        uint32_t response = multicore_fifo_pop();

        // if core1 echoed the command, continue. Otherwise, start over from the beginning
        if (response == sequence[i]) {
            i++;
        }
        else {
            i = 0;
        }
    }

    // restore the fifo IRQ to its previous state
    irq_set_enabled(SIO_IRQ_PROC0, enabled);
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

uint32_t multicore_fifo_pop()
{
    // wait for the read fifo to have data on it
    while((sio_hw->fifo_st & SIO_FIFO_ST_VLD_BITS) == 0) {
        nop();
    }

    return sio_hw->fifo_rd;    
}

void multicore_fifo_drain(void)
{
    // while there is something present in the read fifo, pop it
    while(!((sio_hw->fifo_st & SIO_FIFO_ST_VLD_BITS) == 0)) {
        (void) sio_hw->fifo_rd;
    }
}