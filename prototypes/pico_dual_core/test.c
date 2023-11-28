
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"
#include "pico/util/queue.h"

#include "custom_multicore.h"

#define LED_PIN  25


// built-in queue library help taken from https://arduino.stackexchange.com/questions/86671/rp2040-example-sketch-for-dual-core-queuing
queue_t queue;

typedef struct queueItem {
  uint32_t value;
} item;

const int QUEUE_LENGTH = 128;

int core1_main() {
    puts("hello from core 1\n");
    struct queueItem temp;
    while(1) {
        sleep_ms(500);

        // poll to see if anything is on the queue
        printf("Is there smth on the queue? %d\n", queue_is_empty(&queue));

        // try to pop
        queue_remove_blocking(&queue, &temp);

        printf("Popped %d\n", temp.value);
    }
    /*
    while (queue_try_remove(&queue, &temp)) {
        printf("Item popped from queue: %d\n", temp.value);
    }
    */
}

int main() {
    // initialize stdio for usb communication
    stdio_init_all();

    sleep_ms(5000);

    // initialize the LED GPIO pin
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    // initialize the queue
    queue_init(&queue, sizeof(item), QUEUE_LENGTH);

    // start up the second core
    launch_core1((void *)core1_main);

    uint32_t sequence[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    uint i = 0;
    while (1) {
        gpio_put(LED_PIN, 0);
        sleep_ms(500);
        gpio_put(LED_PIN, 1);
        puts("Hello World\n");
        
        struct queueItem temp;
        temp.value = sequence[i % 10];
        if (queue_try_add(&queue, &temp)) {
            printf("Added %d to queue\n", temp.value);
        }
        else {
            printf("Queue was full!\n");
        }
        sleep_ms(500);

        i++;
    }
}

