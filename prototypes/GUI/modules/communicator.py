"""
Module responsible for communicating directly with the mat interface board
"""

from PyQt6.QtCore import QObject, pyqtSignal

from datetime import datetime
import os

from pathlib import Path

import serial
import serial.tools.list_ports

import numpy as np
from PIL import Image

from modules.calibration import Calibration
from modules.mat_handler import *



class SessionWorker(QObject):
    """
    Class which represents a recording session and handles communications to the mat
    for that session
    """

    # a signal which is emitted to indicate that the session is complete and the thread should be cleaned up
    finished = pyqtSignal()

    # a signal which indicates an image has been saved at the path in the signal
    calculated_pressures = pyqtSignal(np.ndarray)

    def __init__(self, port: int, baud: int, calibrator: Calibration=None):
        super(SessionWorker, self).__init__()

        self.path = self.setup()
        self.port = port
        self.baud = int(baud)
        self.polling = False
        self.calibrator = calibrator


    def setup(self):
        """
        gets current date and time in the format of yy_mm_dd_THH_MM_SS
        finds the current working directory then adds a folder named after the current time to /sessions
        """
        now = datetime.now()
        folderName = now.strftime("%y_%m_%d_T%H_%M_%S")

        i = 0
        while(True):
            # attempt to create the folder, and increment its number by one if the creation fails
            try:
                path = os.getcwd() + "\sessions\\" + folderName + f"_{i}"
                os.mkdir(path)
                break
            except FileExistsError as e:
                i += 1
                continue

        return path


    def run(self):
        """
        Main loop of the session worker
        """
        # attempt to connect to the board over serial, exit if unable
        print('run.')

        # exit if the port does not exist
        ports = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]
        if self.port not in ports:
            print("Port does not exist")
            self.stop()
            return
        
        print("opening serial")
        with serial.Serial(self.port, baudrate=self.baud, timeout=10) as ser:
            # send the message to start reading the mat
            ser.write((START_READING_COMMAND + '\n').encode('utf-8'))
            self.polling = True
            while self.polling:
                # mat data is transmitted as a string in hexadecimal format
                m = ser.readline()

                # skip if the result of a timeout
                if m == b'':
                    continue

                # trim off the \n\r
                m = str(m.decode('utf-8')[:-2])

                # get the mat as a flat list
                flat_mat = hex_string_to_array(m)
                # prettyprint_mat(flat_mat)

                data_array = mat_list_to_array(flat_mat)
                # print_2darray(im_array)

                pressure_array = self.calibrator.apply_calibration_curve(data_array)

                # save the pressure values as an npy
                self.save_npy(pressure_array)

                self.calculated_pressures.emit(pressure_array)


    def stop(self):
        print('stopping')

        self.polling = False
        self.finished.emit()


    def save_npy(self, pressure_array: np.ndarray):
        """
        Saves a numpy array of pressure values to disk
        returns: filepath of the saved npy file
        """
        # create the image's filename
        sample_num = len(list(Path(self.path).glob('*')))
        sample_path = Path(self.path).joinpath(f"{sample_num:05d}.png")

        np.save(sample_path, pressure_array, allow_pickle=False)

        return sample_path


    def __str__(self):
        return f"Session at {self.port=}, {self.baud=}"

