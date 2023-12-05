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


def calc_percent_error(experimental, theoretical):
    return (experimental - theoretical) / theoretical * 100


p0 = [0.05, 0.05, 100]

if __name__ == "__main__":
    flat_readings = []
    expected_pressures = []

    data_files = Path("./raw_data").glob("*.csv")

    for path in data_files:
        flat_readings.append(np.loadtxt(path, dtype=np.uint8, delimiter=',').flatten())
        expected_pressures.append(float(str(path).split('_')[2].split('pa')[0]))

    flat_readings = np.asarray(flat_readings)
    max_sensval = np.max(flat_readings)
    print(f"Maximum recorded sensor value: {max_sensval}")
    expected_pressures = np.asarray(expected_pressures)

    f, axes = plt.subplots(nrows=2, ncols=2)

    # plot the aggregate readings
    for pres, read in zip(expected_pressures, flat_readings):
        axes[0][0].scatter(read, [pres] * len(read))

    axes[0][0].set_title("Sensor values for different pressures")
    axes[0][0].set_xlabel("Sensor ADC value (unitless)")
    axes[0][0].set_ylabel("Actual pressure (Pa)")
    axes[0][0].set_xlim([0, 255])
    axes[0][0].set_ylim([0, 6000])

    # plot the average readings
    avg_readings = np.asarray([np.average(flat_reading) for flat_reading in flat_readings])
    z = sorted(zip(avg_readings, expected_pressures))
    xs = np.asarray([i[0] for i in z])
    ys = np.asarray([i[1] for i in z])
    axes[0][1].plot(xs, ys, label="Average sensor value")

    axes[0][1].set_title("Average sensor values for different pressures")
    axes[0][1].set_xlabel("Average of each sensor's ADC value (unitless)")
    axes[0][1].set_ylabel("Actual pressure (Pa)")
    axes[0][1].set_xlim([0, 255])
    axes[0][1].set_ylim([0, 6000])

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
    axes[0][1].plot(xcont, fit_function(xcont, a, b, c), '--', label="Exponential curve fit")
    axes[0][1].legend()

    # to figure out if it is possible to hit our % error specifications, plot the step size of the fit curve 
    steps = []
    for i in range(1, 255):
        steps.append(fit_function(i, a, b, c) - fit_function(i-1, a, b, c))
    steps = np.asarray(steps)[0:max_sensval]

    axes[1][0].plot([fit_function(i, a, b, c) for i in range(1, max_sensval + 1)], steps)
    #axes[1][0].axvline(fit_function(max_sensval + 1, a, b, c), color='red', label="maximum recorded sensor value")
    #axes[1][0].text(max_sensval + 1, 400, "Max recorded\nsensor value", color='red', fontsize='small')

    axes[1][0].set_title("Step size of fit exponential for pressures seen by the sensors")
    axes[1][0].set_xlim([0, 6000])
    axes[1][0].set_ylim([-5, 300])
    axes[1][0].set_xlabel("Applied Pressure (Pa)")
    axes[1][0].set_ylabel("Step size (Pa)")

    # plot the %error experienced due to a single misstep
    errors = [max(abs(calc_percent_error(fit_function(i, a, b, c), fit_function(i, a, b, c) + steps[i])),
                  abs(calc_percent_error(fit_function(i, a, b, c), fit_function(i, a, b, c) + steps[i]))) 
              for i in range(1, max_sensval)]

    axes[1][1].plot(range(1, max_sensval), errors)
    axes[1][1].set_title("Percentage error in the event of an off-by-one error in the sensor value")
    axes[1][1].set_xlabel("Sensor value (unitless)")
    axes[1][1].set_ylabel("Percentage error (%)")

    # calculate the % error when a sample is taken near the greatest step size of the fit curve
    max_step_size_index = np.argmax(steps)
    value_at_max_step_size = fit_function(max_step_size_index, a, b, c)
    upper_error = calc_percent_error(value_at_max_step_size, value_at_max_step_size + steps[max_step_size_index])
    lower_error = calc_percent_error(value_at_max_step_size, value_at_max_step_size - steps[max_step_size_index])

    print(f"Errors at the maximum step size {steps[max_step_size_index]}:")
    print(f"   percentage error if the sensor value is off by one in the positive direction: {upper_error}")
    print(f"   percentage error if the sensor value is off by one in the negative direction: {lower_error}")

    f.tight_layout()

    print(errors[150])

    plt.show()

