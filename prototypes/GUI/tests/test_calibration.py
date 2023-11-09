"""
Unit tests for the calibration module
"""
import numpy as np

from modules.calibration import MatReading, Calibration
from modules.mat_handler import ROW_WIDTH, COL_HEIGHT


def test_two_samples_ideal():
    """
    Test which covers fitting a curve to two flawless samples of the mat
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=1)

    # add two samples 
    array = np.zeros((ROW_WIDTH, COL_HEIGHT))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 1, array)
    cal.add_reading(reading)

    array = np.ones((ROW_WIDTH, COL_HEIGHT))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 1, array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    truth = np.ones((ROW_WIDTH, COL_HEIGHT))

    assert np.array_equal(y, truth)


def test_five_samples_ideal():
    """
    Test which covers fitting a curve to five flawless samples of the mat
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=4)

    # add two samples 
    array = np.full((ROW_WIDTH, COL_HEIGHT), 0, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 0, array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 32, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 10, array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 64, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 30, array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 128, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 50, array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 255, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 200, array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    print(x)
    print(y)

    raise NotImplementedError("Decide whether this makes sense")

    # assert np.array_equal(y, truth)