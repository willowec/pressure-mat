"""
Produces a plot based on the raw mat data readings in raw_data
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

#   1. Load and flatten all the CSV files into a list of numpy arrays
#   2. Save the corresponding expected pressure values into another array
#   3. Plot each individual sensor on one plot
#   4. Plot the average sensor value on one plot

if __name__ == "__main__":
    flat_readings = []
    expected_pressures = []

    data_files = Path("./raw_data").glob("*.csv")

    for path in data_files:
        flat_readings.append(np.loadtxt(path, dtype=np.uint8, delimiter=',').flatten())
        expected_pressures.append(float(str(path).split('_')[2].split('pa')[0]))

    f, axes = plt.subplots(nrows=2, ncols=1)

    # plot the aggregate readings
    for pres, read in zip(expected_pressures, flat_readings):
        axes[0].scatter(read, [pres] * len(read))

    # plot the average readings
    avgs = [np.average(flat_reading) for flat_reading in flat_readings]
    print(avgs)
    z = sorted(zip(avgs, expected_pressures))
    x = [i[0] for i in z]
    y = [i[1] for i in z]
    axes[1].plot(x, y)

    plt.show()

