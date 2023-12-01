"""
Command line program which polls calibration data from the mat for the purpose of calibrating
    individual sensors on the mat using small weights
"""

USAGE = """
Call with the index of the sensor you want to calibrate. Follow the instrutions the program gives you.
"""

import argparse
import serial, sys

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *

from modules.calibration import *
from modules.communicator import *
from modules.mat_handler import *


expected_pressures_g_to_pa = {
    500 : 52.813,
    200 : 75.977,
    100 : 102.691,
    50  : 123.808,
    20  : 161.925,
    10  : 192.205
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument("port", type=str, default="COM4", help="The com port the mat is plugged in to")
    parser.add_argument("index_x", type=int, help="The X index of the sensor you are calibrating")
    parser.add_argument("index_y", type=int, help="The Y index of the sensor you are calibrating")

    args = parser.parse_args()

    cal_vals = {}

    print(f"Starting calibration routine for sensor ({args.index_x}, {args.index_y})")

    # get mat reading vals for each weight
    for weight, e_pres in expected_pressures_g_to_pa.items():
        input(f"Place the {weight}g weight on the sensor and press Enter: ")

        data_array = []
        # get a reading of the mat
        with serial.Serial(args.port, baudrate=115200, timeout=10) as ser:
            # send the message to start reading the mat
            ser.write((GET_CAL_VALS_COMMAND + '\n').encode('utf-8'))
        
            # mat data is transmitted as raw bytes
            bytes = ser.read(VERIFICATION_WIDTH + MAT_SIZE)
            if bytes == b'':
                print("Serial timed out!")
                quit()

            flat_mat = [x for x in bytes]

            # ensure that the verifiation message was aligned
            for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
                if not (ver == val):
                    raise Exception("Verification sequence not found in mat transmission")

            data_array = mat_list_to_array(flat_mat)

        # get just the value for the indexed sensor
        cal_vals[weight] = data_array[args.index_x, args.index_y]

        print(f"   Reading acquired for weight {weight}g")

    print(cal_vals)