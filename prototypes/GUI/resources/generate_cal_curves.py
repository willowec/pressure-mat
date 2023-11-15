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


if __name__ == "__main__":
    mat_readings = []

    data_files = Path("./raw_data").glob("*.csv")

    calibration = Calibration(ROW_WIDTH, COL_HEIGHT, 2)

    for path in data_files:
        # create a MatReading for each saved mat reading and append it to the calibrator
        reading = MatReading(ROW_WIDTH, COL_HEIGHT, 0, np.loadtxt(path, dtype=np.uint8, delimiter=','))
        reading.actual_pressure = float(str(path).split('_')[2].split('pa')[0])
        calibration.add_reading(reading)

    calibration.calculate_calibration_curves()

    f, axes = plt.subplots(nrows=1, ncols=1)

    # plot the calibration curves
    x = np.linspace(0, 255, 100)
    curves = calibration.cal_curves_array.flatten()
    for poly in curves:
        axes.plot(x, poly(x))

    axes.set_title("Calculated Calibration Curves")
    axes.set_xlabel("Mat sensor reading (unitless)")
    axes.set_ylabel("Mapped pressure value (Pa)")

    f.tight_layout()

    plt.show()



