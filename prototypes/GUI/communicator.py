"""
Module responsible for communicating directly with the mat interface board
"""

from PyQt6.QtCore import QObject, pyqtSignal

from datetime import datetime
import os, serial, time


    
class SessionWorker(QObject):
    """
    Class which represents a recording session and handles communications to the mat
    for that session
    """

    # a signal which is emitted to indicate that the session is complete and the thread should be cleaned up
    finished = pyqtSignal()

    def __init__(self, port: int, baud: int):
        super(SessionWorker, self).__init__()

        self.path = self.setup()
        self.port = port
        self.baud = int(baud)


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

        try:
            with serial.Serial(self.port, baudrate=self.baud, timeout=10) as ser:
                print(ser)
        except serial.SerialException as e:
            print(f"Failed to connect board to session: {e}")

        self.stop()


        """
        # open a serial port connection
        ser = QSerialPort(self.port)
        ser.setBaudRate(int(self.baud))
        opened = ser.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        print(opened)

        print(ser)


        # close the serial port connection
        ser.close()
        

        self.stop()
        """

    def stop(self):
        print('stopping')

        self.finished.emit()


    def read_mat(self):
        pass


    def __str__(self):
        return f"Session at {self.port=}, {self.baud=}"

