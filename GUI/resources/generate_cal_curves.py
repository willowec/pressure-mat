"""
File which calculates calibration curves from the raw_data directory
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *
from modules.mat_handler import *


def fit_function(x, a, b, c):
    return a * np.exp(b * x) + c

p0 = [0.0007204221429716851, 0.04216285053306005, 0.047785412782311236] # the initial parameters are taken from the averaged curve fit

if __name__ == "__main__":
    mat_readings = []

    data_files = Path("./raw_data").glob("*.csv")

    calibration = Calibration(ROW_WIDTH, COL_HEIGHT, 2)

    print("Attempting to generate calibration curves...")

    for path in data_files:
        # create a MatReading for each saved mat reading and append it to the calibrator
        reading = MatReading(ROW_WIDTH, COL_HEIGHT, 0, np.loadtxt(path, dtype=np.uint8, delimiter=','))
        reading.actual_pressure = float(str(path).split('_')[2].split('pa')[0])
        calibration.add_reading(reading)

    calibration.calculate_calibration_curves()

    # save the calibration curves to a default
    np.save("default_calibration_curves.npy", calibration.cal_curves_array, allow_pickle=False)
    print("Saved calibrations to default_calibration_curves.npy")


    # also calculate an average calibration curve that can be applied to all sensors
    data_files = Path("./raw_data").glob("*.csv")
    avgs = []
    pressures = []
    for path in data_files:
        avgs.append(np.average(np.loadtxt(path, dtype=np.uint8, delimiter=',').flatten()))
        pressures.append(float(str(path).split('_')[2].split('pa')[0]))
    
    print(avgs, pressures)

    params, cv = scipy.optimize.curve_fit(fit_function, avgs, pressures, p0=p0)

    avg_cal_curves = np.empty_like(calibration.cal_curves_array)
    for i in range(avg_cal_curves.shape[0]):
        for j in range(avg_cal_curves.shape[1]):
            avg_cal_curves[i, j] = np.asarray(params)

    np.save("averaged_calibration_curves.npy", avg_cal_curves, allow_pickle=False)


    f, axes = plt.subplots(nrows=1, ncols=1)

    # plot the calibration curves
    x = np.linspace(0, 255, 100)
    curves = calibration.cal_curves_array
    for i in range(curves.shape[0]):
        for j in range(curves.shape[1]):
            params = curves[i, j]
            axes.plot(x, calibration.fit_function(x, *params))

    axes.set_title("Calculated Calibration Curves")
    axes.set_xlabel("Mat sensor reading (unitless)")
    axes.set_ylabel("Mapped pressure value (Pa)")
    axes.set_ylim([0, 1000])

    f.tight_layout()

    plt.show()



