from machine import Pin
import utime

# flicker the board led to indicate that the device is running
board_led = Pin(25, Pin.OUT)
board_led.on()
utime.sleep_ms(1000)
board_led.off()

# approximate the ADC

"""
ADC Datasheet:
Explanation of the serial protocol starts at p12
For the serial interface, refer to clock mode 10

Things this needs to support:
    input data byte
    setup register
    conversion register
    (maybe) reset register
"""

# set up SPI pins
CS = Pin(5, mode=Pin.IN)
DIN = Pin(4, mode=Pin.IN)       # RX
DOUT = Pin(3, mode=Pin.OUT)     # TX
SCLK = Pin(2, mode=Pin.IN)      # cannot be clocked at over 10MHz
# EOCbar may not be necessary


# main loop
while True:
    pass