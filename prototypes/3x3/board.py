# Script which reads a 3x3 mat and transmits the data via usb serial to the host
from machine import Pin, ADC
import utime
# Columns connect to GP13, GP12, GP11
# Rows connect to ADC0, ADC1, ADC2 (GP26, GP27, GP28)
# Resistors are 470k

READ_DELAY_MS = 100
ADC_MAX = 65535

rows = [ADC(26), ADC(27), ADC(28)]
columns = [Pin(13, Pin.OUT), Pin(12, Pin.OUT), Pin(11, Pin.OUT)]


while True:
    # oh, since we have enough channels for each row, we can read all rows at once!
    # for each column pin, pull high and read all the rows:
    message = ""
    utime.sleep_ms(READ_DELAY_MS)
    for i, col in enumerate(columns):
        # pull one of the columns high
        col.on()
        utime.sleep_ms(READ_DELAY_MS)

        # read each row
        for j, row in enumerate(rows):
            val = int(row.read_u16() / ADC_MAX * 255) # convert adc value to number 0-255
            message += f"{val}|"

        col.off()

    # assemble information and send to host
    print(message)
