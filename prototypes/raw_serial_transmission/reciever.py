"""
Simple program which recieves raw data from the pico program compiled in this directory
"""

import serial, argparse

ROW_WIDTH = 28

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=str, default="COM3", help="The com port the mat is plugged in to")

    args = parser.parse_args()

    with serial.Serial(args.port, baudrate=115200, timeout=10) as ser:

        while True:
            bytes = ser.read(ROW_WIDTH)
            print(bytes)
            values = [x for x in bytes]
            print(values)

