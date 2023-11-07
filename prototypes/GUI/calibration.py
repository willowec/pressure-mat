""" 
Module responsible for handling the calibration of the mat
"""

import numpy as np


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
            self.arrayOfCoefficients = np.zeros((self.matWidth,self.matHeight, self.polyFitDegree))


    def add_readings(self, actualWeight, actualMatReading: np.ndarray):
        """
        add actual calibration weight value and matrix of mat readings to listOfMatReadings
        """
        self.listOfMatReadings.append(MatReading(self.width, self.height, actualWeight, actualMatReading))


    def calculate_calibration_curves(self):
        """
        updates the listOfCoefficients at every sensor with the polyfit results 
        """

        # array of X and Y values to be put into polyfit X = mat reading, Y = actual weight on mat
        matXVals = np.empty(self.numWeights)
        matYVals = np.empty(self.numWeights)

        for rows in self.width:
            for cols in self.height:
                for i in self.numWeights:
                    matXVals[i] = self.listOfMatReadings[i].matMatrix[rows,cols]
                    matYVals[i] = self.listOfMatReadings[i].actualWeight

                self.arrayOfCoefficients[rows,cols] = np.polyfit(matXVals, matYVals, self.polyFitDegree)


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
                    calibratedValues[rows, cols] += self.arrayOfCoefficients[rows,cols,i]*(matReadings[rows,cols]**(i+1))

        return calibratedValues
