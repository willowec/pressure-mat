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

    # a signal used to transmit live formatted statistics about the session
    session_stats = pyqtSignal(str)

    # a signal used to transmit statistics about the session after it has finished
    finished_session_stats = pyqtSignal(str)

    def __init__(self, port: int, baud: int, calibrator: Calibration=None):
        super(SessionWorker, self).__init__()

        self.path = self.setup()
        self.port = port
        self.baud = int(baud)
        self.polling = False
        self.calibrator = calibrator

        # variables used to track statistics about the session
        self.start_time_ns = time.time_ns()
        self.delta_times = []
        self.transmission_errors = 0


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
            ser.set_buffer_size(rx_size = 1700, tx_size = 1700)
            # send the message to start reading the mat
            ser.write((START_READING_COMMAND + '\n').encode('utf-8'))
            self.polling = True

            prev_sample_time_ns = time.time_ns()
            while self.polling:
                # mat data is transmitted as raw bytes
                bytes = ser.read(VERIFICATION_WIDTH + MAT_SIZE)
                if bytes == b'':
                    print("Serial timed out!")
                    continue
                
                flat_mat = [x for x in bytes]

                # ensure that the verifiation message was aligned
                for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
                    if not (ver == val):
                        self.transmission_errors += 1
                        print("====TRANSMISSION ERROR OCCURED! FIXING!!!====")
                        # a verification error has occured, probably because the fifo filled up
                        # to resolve it, simply wipe the fifo and read until the next verification sequence
                        ser.reset_input_buffer()
                        hist = np.zeros(VERIFICATION_WIDTH, dtype=np.uint8)
                        while(not np.array_equal(hist, np.asarray(VERIFICATION_SEQUENCE, dtype=np.uint8))):
                            hist = np.roll(hist, -1)
                            hist[-1] = int.from_bytes(ser.read(1), "big")

                        break   # do not false positive another error

                data_array = mat_list_to_array(flat_mat)

                pressure_array = self.calibrator.apply_calibration_curve(data_array)
                pressure_array = self.calibrator.apply_dc_offsets(pressure_array)

                # save the pressure values as an npy
                self.save_npy(pressure_array)

                self.calculated_pressures.emit(pressure_array)

                # update the timing statistics
                now_ns = time.time_ns()
                delta_ns = now_ns - prev_sample_time_ns
                self.delta_times.append(delta_ns)
                prev_sample_time_ns = now_ns

                # prevent division by zero
                delta_ns = max(1, delta_ns)

                msg = f"Sample rate: {(1/delta_ns * 1000000000):.2f}Hz\nQueued RX size: {ser.in_waiting}\n"
                msg += f"Total session time: {((time.time_ns() - self.start_time_ns) / 1000000000):.2f}s\n"
                self.session_stats.emit(msg)


    def stop(self):
        print('stopping')
        self.polling = False

        # calculate the finished session stats
        average_delta_ns = np.average(self.delta_times)
        average_sample_rate = 1 / average_delta_ns * 1000000000

        msg = f"Average sample rate: {average_sample_rate:02f}Hz\n"
        msg += f"Total # transmission errors: {self.transmission_errors}\n"

        self.finished_session_stats.emit(msg)

        # clean up this thread
        self.finished.emit()


    def save_npy(self, pressure_array: np.ndarray):
        """
        Saves a numpy array of pressure values to disk
        returns: filepath of the saved npy file
        """
        # create the image's filename
        sample_num = len(list(Path(self.path).glob('*')))
        sample_path = Path(self.path).joinpath(f"{sample_num:05d}.npy")

        np.save(sample_path, pressure_array, allow_pickle=False)

        return sample_path


    def __str__(self):
        return f"Session at {self.port=}, {self.baud=}"

