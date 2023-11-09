""" 
Module responsible for handling the calibration of the mat
"""

import numpy as np
from numpy.polynomial.polynomial import Polynomial

from PyQt6.QtCore import QObject, pyqtSignal

import serial

from mat_handler import *


class MatReading:
    """
    A class that holds a 2D matrix representing the mat and a value for the actual weight on the mat
    """

    def __init__(self, matWidth:int, matHeight: int, actualWeight: float, rawMatValues: np.ndarray):
        self.width = matWidth
        self.height = matHeight
        self.actualWeight = actualWeight
        self.matMatrix = rawMatValues


    def update_values(self, actualWeight, rawMatValues: np.ndarray):
        """
        Change the actual weight and the raw mat values of the MatReading
        """
        self.actualWeight = actualWeight
        self.matMatrix = rawMatValues


class Calibration:
    """
    Class which handles calibrating the mat by taking raw mat readings and converting them into a calibrated mat output of the same size.
    Also responsible for calculating calibration curves
    """
    def __init__(self, matWidth: int, matHeight: int):
            self.width = matWidth
            self.height = matHeight
            self.polyFitDegree = 4
            self.listOfMatReadings = []
            self.cal_curves_array = np.empty((self.width,self.height, self.polyFitDegree + 1), dtype=Polynomial)   # +1 because of constant
            self.calibrated = False


    def add_reading(self, actualMatReading: MatReading):
        """
        add a MatReading instance to listOfMatReadings
        """
        self.listOfMatReadings.append(actualMatReading)


    def calculate_calibration_curves(self):
        """
        updates the listOfCoefficients at every sensor with the polyfit results 
        """

        # array of X and Y values to be put into polyfit X = mat reading, Y = actual weight on mat
        num_weights = len(self.listOfMatReadings)
        matXVals = np.empty(num_weights)
        matYVals = np.empty(num_weights)

        for rows in range(self.width):
            for cols in range(self.height):
                for i in range(num_weights):
                    matXVals[i] = self.listOfMatReadings[i].matMatrix[rows,cols]
                    matYVals[i] = self.listOfMatReadings[i].actualWeight

                self.cal_curves_array[rows,cols] = Polynomial.fit(matXVals, matYVals, self.polyFitDegree)

        self.calibrated = True


    def apply_calibration_curve(self, matReadings: np.ndarray):
        """
        takes in raw mat readings as a matrix and returns a matrix of the same size with calibrated values
        """

        # initialize return array to be correct width and height and all values equal to zero
        calibratedValues = np.zeros((self.width, self.height))

        # itterate through every sensor of the mat calculate the calibrated value at that sensor
        for rows in self.width:
            for cols in self.height:
                for i in self.polyFitDegree:
                    calibratedValues[rows, cols] += self.cal_curves_array[rows,cols,i]*(matReadings[rows,cols]**(i+1))

        return calibratedValues



class CalSampleWorker(QObject):
    """
    QObject which handles asynchronously acquiring samples of data from the mat for calibration calculations
    """
    # a signal which is emitted to indicate that the session is complete and the thread should be cleaned up
    finished = pyqtSignal()

    # a signal to return the sampled MatReading
    reading_result = pyqtSignal(MatReading)

    def __init__(self, port: int, baud: int, calibration_weight):
        """
        Init and run to collect one sample of readings for the weight calibration_weight
        """
        super(CalSampleWorker, self).__init__()

        self.port = port
        self.baud = baud
        self.calibration_weight = calibration_weight


    def run(self):
        """
        Work thread of the CalSampleWorker
        """
        # request calibration readings from the mat
        with serial.Serial(port=self.port, baudrate=self.baud, timeout=10) as ser:
            # send the message to start reading the mat
            ser.write((GET_CAL_VALS_COMMAND + '\n').encode('utf-8'))
            
            m = ser.readline()
            print(m)
            m = str(m.decode('utf-8')[:-2])

            mat_vals = mat_list_to_array(hex_string_to_array(m))
            reading = MatReading(ROW_WIDTH, COL_HEIGHT, self.calibration_weight, mat_vals)

            self.reading_result.emit(reading)

        self.finished.emit()