"""
Produces a plot based on the raw mat data readings in raw_data
"""

import matplotlib.pyplot as plt
import scipy
import numpy as np
from pathlib import Path

#   1. Load and flatten all the CSV files into a list of numpy arrays
#   2. Save the corresponding expected pressure values into another array
#   3. Plot each individual sensor on one plot
#   4. Plot the average sensor value on one plot

def fit_function(x, a, b, c):
    return a * np.exp(b * x) + c

p0 = [0.05, 0.05, 100]

if __name__ == "__main__":
    flat_readings = []
    expected_pressures = []

    data_files = Path("./raw_data").glob("*.csv")

    for path in data_files:
        flat_readings.append(np.loadtxt(path, dtype=np.uint8, delimiter=',').flatten())
        expected_pressures.append(float(str(path).split('_')[2].split('pa')[0]))

    flat_readings = np.asarray(flat_readings)
    expected_pressures = np.asarray(expected_pressures)

    f, axes = plt.subplots(nrows=2, ncols=1)

    # plot the aggregate readings
    for pres, read in zip(expected_pressures, flat_readings):
        axes[0].scatter(read, [pres] * len(read))

    axes[0].set_title("Sensor values for different pressures")
    axes[0].set_xlabel("Sensor ADC value (unitless)")
    axes[0].set_ylabel("Actual pressure (Pa)")
    axes[0].set_xlim([0, 255])
    axes[0].set_ylim([0, 6000])

    # plot the average readings
    avg_readings = np.asarray([np.average(flat_reading) for flat_reading in flat_readings])
    z = sorted(zip(avg_readings, expected_pressures))
    xs = np.asarray([i[0] for i in z])
    ys = np.asarray([i[1] for i in z])
    axes[1].plot(xs, ys)

    axes[1].set_title("Average sensor values for different pressures")
    axes[1].set_xlabel("Average of each sensor's ADC value (unitless)")
    axes[1].set_ylabel("Actual pressure (Pa)")
    axes[1].set_xlim([0, 255])
    axes[1].set_ylim([0, 6000])

    # fit an exponential to the average readings
    # help from this page: https://swharden.com/blog/2020-09-24-python-exponential-fit/
    params, cv = scipy.optimize.curve_fit(fit_function, xs, ys, p0=p0)
    a, b, c = params

    # determine quality of the fit
    squaredDiffs = np.square(ys - fit_function(xs, a, b, c))
    squaredDiffsFromMean = np.square(ys - np.mean(ys))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"Fit an exponential to the input data with R² = {rSquared}. {a=}, {b=}, {c=}")

    xcont = np.linspace(0, 255, 100)
    axes[1].plot(xcont, fit_function(xcont, a, b, c), '--', label="fitted")

    f.tight_layout()

    plt.show()

