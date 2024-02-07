""" 
Module responsible for handling the calibration of the mat
"""

import numpy as np
import scipy
from scipy.optimize import Bounds
from numpy.polynomial.polynomial import Polynomial

from PyQt6.QtCore import QObject, pyqtSignal

import serial

from modules.mat_handler import *

MAX_RATED_PRESSURE_PA = 2.5  # Maximum pressure we expect any individual sensor to see in pascals

DEFAULT_CAL_CURVES_PATH = "./resources/default_calibration_curves.npy"
AVERAGED_CAL_CURVES_PATH = "./resources/averaged_calibration_curves.npy"

CAL_CURVE_P0 = [0.05, 0.05, 100]    # initial parameters for calibration curve fitting routine
CAL_CURVE_BOUNDS = Bounds([0.00001, 0.00001, 0], [100, 10, 500])    # bound for cal curve fitting routine


class MatReading:
    """
    A class that holds a 2D matrix representing the mat and a value for the actual pressure each sensor on the mat is supposed to be seeing
        actualWeight should be passed in unit lbs
    """

    def __init__(self, matWidth:int, matHeight: int, actualWeight: float, rawMatValues: np.ndarray):
        self.width = matWidth
        self.height = matHeight

        self.actual_pressure = distributed_lbs_to_sensor_pressure(actualWeight)
        self.matMatrix = rawMatValues



class Calibration:
    """
    Class which handles calibrating the mat by taking raw mat readings and converting them into a calibrated mat output of the same size.
    Also responsible for calculating calibration curves
    """
    def __init__(self, mat_width: int, mat_height: int, polyfit_degree: int=4):
            # set up member variables
            self.width = mat_width
            self.height = mat_height
            self.polyfit_degree = polyfit_degree
            self.listOfMatReadings = []
            self.cal_curves_array = np.empty((self.width, self.height, 3), dtype=np.float64)  # list of coefficients
            self.calibrated = False
            self.dc_offsets = np.zeros((self.width, self.height), dtype=np.float64)
            self.zeroing_data = []

            # load the default cal curves
            try:
                self.load_cal_curves(DEFAULT_CAL_CURVES_PATH)
            except FileNotFoundError as e:
                print("Could not load default calibration curves")


    def add_reading(self, actualMatReading: MatReading):
        """
        add a MatReading instance to listOfMatReadings
        """
        self.listOfMatReadings.append(actualMatReading)


    def calculate_calibration_curves(self, drop_values_greater_than=255) -> list:
        """
        updates the cal_curves_array at every sensor with the polyfit results 
        returns the curve fit characteristics
        """
        # clamp the polyfit degree to be one less than the number of calibration samples acquired
        num_weights = len(self.listOfMatReadings)
        if self.polyfit_degree >= num_weights:
            self.polyfit_degree = num_weights - 1
            print("Warning: calibrating using lower polyfit degree than specified due to not being fed enough samples")

        num_failures = 0
        r_squareds = []

        # calculate the calibration curves for each sensor
        for rows in range(self.width):
            for cols in range(self.height):
                matXVals = []
                matYVals = []

                # iterate over each data sample for this sensor
                for i in range(num_weights):
                    x_val = self.listOfMatReadings[i].matMatrix[rows,cols]
                    y_val = self.listOfMatReadings[i].actual_pressure

                    # eliminate from matXVals and matYVals any values at or over drop_values_greater_than
                    if x_val < drop_values_greater_than:
                        matXVals.append(x_val)
                        matYVals.append(y_val)
                    else:
                        print(f"        Skipped datapoint (x={x_val}) at ({rows}, {cols})")
                
                x_vals = np.asarray(matXVals)
                y_vals = np.asarray(matYVals)

                try:
                    # attempt to fit an exponential curve to this sensor
                    self.cal_curves_array[rows,cols] = self.fit(x_vals, y_vals, CAL_CURVE_P0)
                except RuntimeError as e:
                    # if the calibration fails, use the default calibration values
                    num_failures += 1
                    self.cal_curves_array[rows, cols] = CAL_CURVE_P0

                # determine quality of the fit
                squaredDiffs = np.square(y_vals - self.fit_function(x_vals, *self.cal_curves_array[rows,cols]))
                squaredDiffsFromMean = np.square(y_vals - np.mean(y_vals))
                rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
                r_squareds.append(rSquared)

        print(f"   Calibrated with {num_failures} failures. \n        params min: {np.min(self.cal_curves_array, axis=1)}\n        params max: {np.max(self.cal_curves_array, axis=1)}")

        self.calibrated = True

        # calculate and return the characteristics of the fits
        r_squareds = np.asarray(r_squareds)
        min_r2 = np.min(r_squareds)
        avg_r2 = np.average(r_squareds)

        return min_r2, avg_r2
    

    def fit(self, x: np.array, y: np.array, p0: list) -> np.array:
        """
        Function which takes an x and y, and uses scipy to find coefficients that when applied to self.fit_function closely fit (x, y). 
        p0 is the starting point for the function's coefficients
        """

        params, cv = scipy.optimize.curve_fit(self.fit_function, x, y, p0=p0, bounds=CAL_CURVE_BOUNDS, method='trf')
        return np.asarray([params]) # return [a, b, c]


    def apply_calibration_curve(self, matReadings: np.ndarray):
        """
        Takes in raw mat readings as a matrix and returns a matrix of the same size with calibrated values
        """

        # initialize return array to be correct width and height and all values equal to zero
        # datatype is double because the calibrated value will correspond to a real weight value, and for +- 15% error, needs to be 
        #   at least one decimal of precision at 1lbs
        calibratedValues = np.zeros((self.width, self.height), dtype=np.double)

        # iterate through every sensor of the mat and calculate the calibrated value at that sensor
        for rows in range(self.width):
            for cols in range(self.height):
                # apply the curve
                calibratedValues[rows, cols] = self.fit_function(matReadings[rows,cols], * self.cal_curves_array[rows,cols])

        # clamp the results to sane values
        calibratedValues = np.clip(calibratedValues, 0, MAX_RATED_PRESSURE_PA)

        return np.round(calibratedValues, 2)


    def load_cal_curves(self, curves_path: str):
        """
        Loads calibration curves from a numpy file
        """
        self.cal_curves_array = np.load(curves_path, allow_pickle=False)
        self.calibrated = True

    
    def fit_function(self, x: np.array, a, b, c):
        """
        A general exponential function, which calibration curves should be fit to
        """
        return a * np.exp(b * x) + c


    def apply_dc_offsets(self, array_to_offset: np.ndarray):
        """
        Applys the dc offsets to a passed ndarray/matreading. Run calc_dc_offsets() before use. 
        """

        # ensure the offset values never go below zero
        return np.clip((array_to_offset - self.apply_calibration_curve(self.dc_offsets)), 0, 1000000000)


    def calc_dc_offsets(self):
        """
        Updates the dc_offsets array by averaging the zeroing data. 
        """

        for i in range(len(self.zeroing_data)):
            self.dc_offsets += self.zeroing_data[i].matMatrix
        
        self.dc_offsets = (self.dc_offsets / len(self.zeroing_data))


    def add_zeroing_data(self, new_zeroing_data: np.ndarray):
        """
        Appends new mat readings to the zeroing data list. 
        """

        print("Added zeroing data")
        self.zeroing_data.append(new_zeroing_data)



class CalSampleWorker(QObject):
    """
    QObject which handles asynchronously acquiring samples of data from the mat for calibration calculations
    """

    # a signal which is emitted to indicate that the session is complete and the thread should be cleaned up
    finished = pyqtSignal()

    # a signal to return the sampled MatReading to the caller thread
    reading_result = pyqtSignal(MatReading)

    def __init__(self, port: int, baud: int, calibration_weight):
        """
        Init and run to collect one sample of readings for the weight calibration_weight
        calibration_weight must be in units lbs
        """

        super(CalSampleWorker, self).__init__()

        self.port = port
        self.baud = baud
        self.calibration_weight = calibration_weight


    def run(self):
        """
        Main function of the CalSampleWorker
        """

        with serial.Serial(port=self.port, baudrate=self.baud, timeout=10) as ser:
            # request calibration readings from the mat
            ser.write((START_READING_COMMAND + '\n').encode('utf-8'))

            # read the mat's response
            bytes = ser.read(VERIFICATION_WIDTH + MAT_SIZE)
            if bytes == b'':
                print("Serial timed out!")
                return
                
            flat_mat = [x for x in bytes]

            # ensure that the verifiation message was aligned
            for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
                if not (ver == val):
                    raise Exception("Verification sequence not found in mat transmission")

            # construct a reading from the response
            mat_vals = mat_list_to_array(flat_mat)
            reading = MatReading(ROW_WIDTH, COL_HEIGHT, self.calibration_weight, mat_vals)

            # send the reading to the main thread
            self.reading_result.emit(reading)

        self.finished.emit()