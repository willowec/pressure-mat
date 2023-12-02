"""
Command line program which polls calibration data from the mat for the purpose of calibrating
    individual sensors on the mat using small weights
"""

USAGE = """
Call with the index of the sensor you want to calibrate. Follow the instrutions the program gives you.
"""

import argparse, os
from pathlib import Path
import serial, sys
import matplotlib.pyplot as plt
import numpy as np

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *

from modules.calibration import *
from modules.communicator import *
from modules.mat_handler import *

# calibration paths folder
cal_curves_folder = Path("individual_cal_curves")


def fit_function(x, a, b, c):
    return a * np.exp(b * x) + c

p0 = [0.05, 0.05, 100]

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

    # ensure a directory exists to put the cal curves in
    try:
        cal_curves_folder.mkdir()
    except FileExistsError:
        pass # ignore folder already existing

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

    print("Fitting curve...")

    params, cv = scipy.optimize.curve_fit(fit_function, list(cal_vals.keys()), list(cal_vals.values()), p0=p0)

    print(f"Fit parameters: {params}")

    # save the cal curves
    np.save(cal_curves_folder.joinpath(f"cal_curve_({args.index_x}, {args.index_y}).npy"), np.array(params))

    # plot the calibration curve
    x = np.linspace(0, 255, 100)
    plt.plot(x, fit_function(x, *params))
    plt.title(f"Calibration curve for sensor {args.index_x}, {args.index_y}")
    plt.xlabel("Sensor value")
    plt.ylabel("Pressure (Pa)")
    plt.show()