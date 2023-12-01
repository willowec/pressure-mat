"""
Small program that allows for getting raw data from the mat for testing purposes
"""

import argparse
import serial, sys

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *

from modules.calibration import *
from modules.communicator import *
from modules.mat_handler import *

import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("expected_weight_lbs", type=float, help="The weight being evenly distributed over the mat")
    parser.add_argument("port", type=str, default="COM3", help="The com port the mat is plugged in to")

    args = parser.parse_args()

    expected_pressure = lbs_to_neutons(args.expected_weight_lbs) / (MAT_SIZE * SENSOR_AREA_SQM)

    # save the raw mat samples to a csv file named as the expected pressure values that should be experienced by the sensors

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

        path = f"resources/raw_data/matreading_{expected_pressure:4.4f}pa.csv"
        print(f"Saving measured mat values for expected weight {args.expected_weight_lbs:4.4f}lbs and expected pressure {expected_pressure:4.4f} to {path}")
        np.savetxt(path, data_array, fmt="%03d", delimiter=',')