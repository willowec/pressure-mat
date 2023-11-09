"""
Unit tests for the calibration module
"""
import numpy as np
from numpy.polynomial.polynomial import Polynomial

from modules.calibration import MatReading, Calibration
from modules.mat_handler import ROW_WIDTH, COL_HEIGHT


CONTRACT_MAX_ERROR_PERC = 15    # the maximum allowed percentage error as per our contract


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

    truth = np.ones((ROW_WIDTH, COL_HEIGHT), dtype=np.double)

    assert np.array_equal(y, truth)


def test_five_samples_ideal():
    """
    Test which covers fitting a curve to five flawless samples of the mat
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=4)

    # add 5 samples, fitting y = 0.001(x^2) + 0.001x + 1
    poly = Polynomial([1, 0.001, 0.001])
    array = np.full((ROW_WIDTH, COL_HEIGHT), 0, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(0), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 32, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(32), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 64, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(64), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 128, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(128), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 255, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(255), array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    # generate the expected result
    truth = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.double)
    for i in range(len(truth)):
        truth[i] = poly(int(truth[i]) % 256)

    truth = np.round(truth.reshape((ROW_WIDTH, COL_HEIGHT)), 2)

    # compare the actual and expected results. Interestingly enough, they are not exact
    perc_errors = np.empty((ROW_WIDTH, COL_HEIGHT))
    for i in range(ROW_WIDTH):
        for j in range(COL_HEIGHT):
            perc_errors[i, j] = 100 * ((y[i, j] - truth[i, j]) / truth[i, j])    # 100 * (meas - true) / true

    perc_error = np.max(np.abs(perc_errors.flatten()))
    print(f"Maximum percentage error between the true value and the polyfit value: {perc_error}")

    assert perc_error < CONTRACT_MAX_ERROR_PERC


def test_ten_samples_ideal_bad_case():
    """
    Test which covers fitting a curve to ten flawless samples of the mat
    Expects awful error due to the high degree the polynomial is fit to
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=9)

    # add 5 samples, fitting y = 0.001(x^2) + 0.001x + 1
    poly = Polynomial([1, 0.001, 0.001])
    array = np.full((ROW_WIDTH, COL_HEIGHT), 0, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(0), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 8, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(8), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 16, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(16), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 32, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(32), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 48, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(48), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 64, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(64), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 96, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(96), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 128, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(128), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 192, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(192), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 255, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(255), array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    # generate the expected result
    truth = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.double)
    for i in range(len(truth)):
        truth[i] = poly(int(truth[i]) % 256)

    truth = np.round(truth.reshape((ROW_WIDTH, COL_HEIGHT)), 2)

    # compare the actual and expected results. Interestingly enough, they are not exact
    perc_errors = np.empty((ROW_WIDTH, COL_HEIGHT))
    for i in range(ROW_WIDTH):
        for j in range(COL_HEIGHT):
            perc_errors[i, j] = 100 * ((y[i, j] - truth[i, j]) / truth[i, j])    # 100 * (meas - true) / true

    perc_error = np.max(np.abs(perc_errors.flatten()))
    print(f"Maximum percentage error between the true value and the polyfit value: {perc_error}")

    # Surprisingly, using a higher order polynomial seems to not have much affect until order 8 - 9, where error begins to explode
    # expect 2652.48 percent error (bad)
    assert perc_error > CONTRACT_MAX_ERROR_PERC