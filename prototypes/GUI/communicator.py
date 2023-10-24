"""
Module responsible for communicating directly with the mat interface board
"""

from PyQt6.QtCore import QObject, pyqtSignal

from datetime import datetime
import os, time

from pathlib import Path

import serial
import serial.tools.list_ports

import numpy as np
from PIL import Image


ROW_WIDTH = 28
COL_HEIGHT = 56
MAT_SIZE = 1568

START_READING_COMMAND = "start_reading"

    
class SessionWorker(QObject):
    """
    Class which represents a recording session and handles communications to the mat
    for that session
    """

    # a signal which is emitted to indicate that the session is complete and the thread should be cleaned up
    finished = pyqtSignal()

    # a signal which indicates an image has been saved at the path in the signal
    imageSaved = pyqtSignal(str)

    def __init__(self, port: int, baud: int):
        super(SessionWorker, self).__init__()

        self.path = self.setup()
        self.port = port
        self.baud = int(baud)
        self.polling = False


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
                flat_mat = self.hex_string_to_array(m)
                self.prettyprint_mat(flat_mat)

                # convert the list to an image and save it
                self.save_image(flat_mat)


    def stop(self):
        print('stopping')

        self.polling = False
        self.finished.emit()


    def save_image(self, flat_mat: list):
        """
        Converts a buffer to an image and saves it in the session folder
        returns: filepath of the saved image
        """
        im_array = self.mat_list_to_array(flat_mat)
        # self.print_2darray(im_array)

        # create the image's filename
        im_num = len(list(Path(self.path).glob('*')))
        im_path = Path(self.path).joinpath(f"{im_num:05d}.png")

        # convert the np array to a greyscale image and save it
        im = Image.fromarray(im_array, mode='L')
        print(f"saving image to {im_path}")
        im.save(im_path)

        # indicate that an image has been saved
        self.imageSaved.emit(str(im_path))

        return im_path


    def hex_string_to_array(self, hex_string):
        """
        Converts a string of 02x hexadecimal numbers to an array
        """
        numbers = []
        for i in range(0, len(hex_string), 2):
            x = hex_string[i: i+2]
            numbers.append(int(x, 16))
        
        return numbers


    def print_2darray(self, array: np.ndarray):
        """
        Function which prints a 2d uint8 numpy array in a readable format
        """
        for row in range(array.shape[1]):
            line = ""
            for i in range(array.shape[0]):
                line += f"{array[i, row]:03d} "
            print(line)

    
    def prettyprint_mat(self, mat_as_list: list):
        """
        Python version of the board_code prettyprint_mat function
        """
        line = ""
        for i in range(MAT_SIZE):
            if (i % ROW_WIDTH) == 0:
                print(line[:-1])
                line = ""

            line += f"{mat_as_list[i]:02x}, "


    def mat_list_to_array(self, mat_as_list: list):
        """
        Converts a 1d python list (presumably the mat) to a 2D numpy array
        """
        array = np.empty((ROW_WIDTH, COL_HEIGHT), dtype=np.uint8)
        x = 0
        y = 0
        for i in range(MAT_SIZE):
            if (i % ROW_WIDTH) == 0 and i > 0:
                y += 1
                x = 0


            array[x, y] = mat_as_list[i]
            x += 1

        return array



    def __str__(self):
        return f"Session at {self.port=}, {self.baud=}"

