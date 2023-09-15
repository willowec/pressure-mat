from machine import Pin, ADC
import utime

# flicker the board led to indicate that the device is running
board_led = Pin(25, Pin.OUT)
board_led.on()
utime.sleep_ms(1000)
board_led.off()

