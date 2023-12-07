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

    min_r2, avg_r2 = calibration.calculate_calibration_curves(drop_values_greater_than=500)
    print(f"Minimum R2 of all curves: {min_r2}. Average R2 for all curves: {avg_r2}")

    # save the calibration curves to a default
    np.save("default_calibration_curves.npy", calibration.cal_curves_array, allow_pickle=False)
    print("Saved calibrations to default_calibration_curves.npy")

    plt.figure(1)

    # plot the calibration curves
    x = np.linspace(0, 255, 100)
    curves = calibration.cal_curves_array
    for i in range(curves.shape[0]):
        for j in range(curves.shape[1]):
            params = curves[i, j]
            plt.plot(x, calibration.fit_function(x, *params))

    plt.title("Calculated Calibration Curves")
    plt.xlabel("Mat sensor reading (unitless)")
    plt.ylabel("Mapped pressure value (Pa)")
    plt.xlim([0, 210])
    plt.ylim([-5, 50])
    plt.axvline(207, color='red')

    plt.figure(2)
    # plt.plot(calibration.fit_function(x, *list(avg_cal_curves[0][0])))
    plt.xlabel("Mat sensor reading (unitless)")
    plt.ylabel("Mapped pressure value (Pa)")
    plt.title("Averaged Calibration Curve")

    # Lets also fit a vurve to the average of all the calibration curves to see if it is nicer overall
    average_curve = []
    for point in range(255):
        point_sum = 0
        n = 0
        for i in range(curves.shape[0]):
            for j in range(curves.shape[1]):
                params = curves[i, j]
                point_sum += calibration.fit_function(point, *params)
                n += 1

        average_curve.append(point_sum / n)

    avg_params, cv = scipy.optimize.curve_fit(fit_function, list(range(255)), average_curve, p0=p0)

    squaredDiffs = np.square(average_curve - fit_function(np.asarray(list(range(255))), *avg_params))
    squaredDiffsFromMean = np.square(average_curve - np.mean(average_curve))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R2 for averaged curve is {rSquared}")

    # save out the average cal curves
    avg_cal_curves = np.empty_like(calibration.cal_curves_array)
    for i in range(avg_cal_curves.shape[0]):
        for j in range(avg_cal_curves.shape[1]):
            avg_cal_curves[i, j] = np.asarray(avg_params)

    np.save("averaged_calibration_curves.npy", avg_cal_curves, allow_pickle=False)


    plt.plot([calibration.fit_function(i, *avg_params) for i in range(255)])
    plt.xlim([0, 210])
    plt.ylim([-5, 50])
    plt.show()



