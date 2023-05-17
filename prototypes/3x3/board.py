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
indicator = Pin(25, Pin.OUT)
cal_button = Pin(15, Pin.IN)

indicator.off() # ensure indicator is off even if in previous run it was on

calibration_vals = [0 for i in range(len(rows) * len(columns))]


def calibrate(grid: list):
    """
    Calculates the calibration vals so that all pixels at rest are equal
    """
    avg = 0
    for val in grid:
        avg += val
    avg = avg / len(grid)

    cal_vals = []
    for val in grid:
        cal_vals.append(avg - val)

    return cal_vals


while True:
    # oh, since we have enough channels for each row, we can read all rows at once!
    # for each column pin, pull high and read all the rows:
    utime.sleep_ms(READ_DELAY_MS)

    grid = []

    for i, col in enumerate(columns):
        # pull one of the columns high
        col.on()
        utime.sleep_ms(READ_DELAY_MS)

        # read each row
        for j, row in enumerate(rows):
            val = int(row.read_u16() / ADC_MAX * 255) # convert adc value to number 0-255
            grid.append(val)

        col.off()

    # if a button is pressed, calibrate the board
    if cal_button.value() == 1:
        calibration_vals = calibrate(grid)

    # modify grid based on calibrated average
    for i in range(len(grid)):
        grid[i] = int(grid[i] + calibration_vals[i])

    # assemble information and send to host
    message = ""
    for val in grid:
        message += f"{val}|"

    print(message)
