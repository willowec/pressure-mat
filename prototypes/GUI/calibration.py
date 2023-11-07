""" 
Module responsible for handling the calibration of the mat
"""

import numpy as np

class Calibration:

    def __init__(self, matWidth: int, matHeight: int, numWeights: int):
            self.width = matWidth
            self.height = matHeight
            self.polyFitDegree = 4
            self.listOfMatReadings = []
            self.listOfCoefficients = np.zeros((self.matWidth,self.matHeight, self.polyFitDegree))

            for i in numWeights:
                self.listOfMatReadings.append(MatReading(self.width,self.height))


    #add actual calibration weight value and matrix of mat readings to listOfMatReadings
    def add_readings(actualWeight, actualMatReading: np.ndarray, index: int):
        self.listOfMatReadings[index].update_values(actualWeight, actualMatReading)

    #updates the listOfCoefficients at every sensor with the polyfit results 
    def calculate_calibration_curves():

        #array of X and Y values to be put into polyfit X = mat reading, Y = actual weight on mat
        matXVals = [self.numWeights]
        matYVals = [self.numWeights]

        for rows in self.matWidth:
            for cols in self.matHeight:
                for i in self.numWeights:
                    matXVals[i] = self.listOfMatReadings[i].matMatrix[rows,cols]
                    matYVals[i] = self.listOfMatReadings[i].actualWeight

                self.listOfCoefficients[rows,cols] = np.polyfit(matXVals,matYVals, self.polyFitDegree)


    #takes in raw mat readings as a matrix and returns a matrix of the same size with calibrated values
    def apply_calibration_curve(matReadings: np.ndarray):

        #initialize return array to be correct width and height and all values equal to zero
        calibratedValues = np.zeros(self.matWidth, self.matHeight)

        #itterate through every sensor of the mat calculate the calibrated value at that sensor
        for rows in self.matWidth:
            for cols in self.matHeight:
                for i in self.polyFitDegree:
                    calibratedValues[rows, cols] += self.listOfCoefficients[rows,cols,i]*(matReadings[rows,cols]**(i+1))

        return calibratedValues

#holds a 2D matrix representing the mat and a value for the actual weight on the mat
class MatReading:

    def __init__(self, matWidth:int, matHeight: int):
        self.width = matWidth
        self.height = matHeight
        self.actualWeight = 0
        self.matMatrix = np.zeros[self.width,self.height]

    def update_values(actualWeight, actualMatReadings: np.ndarray):
        self.actualWeight = actualWeight
        self.matMatrix = actualMatReadings
