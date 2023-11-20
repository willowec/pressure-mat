# GUI which displays data from the mat interpreted by the board and transmitted over serial
import sys, os
from datetime import datetime
import numpy as np

from PIL import Image

from PyQt6.QtGui import  *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from pathlib import Path

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('QtAgg')

from modules.calibration import Calibration, MatReading, CalSampleWorker, MAX_RATED_PRESSURE_PA, DEFAULT_CAL_CURVES_PATH
from modules.communicator import SessionWorker, ROW_WIDTH, COL_HEIGHT
from modules.mat_handler import print_2darray, calc_mat_reading_stats


class MainWindow(QMainWindow):
    """
    Class which handles the main 
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("28x56 Mat Interface")

        self.current_img_path = "default.png"
        self.current_img_index = -1

        self.layout = QGridLayout()
        
        # com port input box
        self.port_input = QLineEdit("COM3", self)
        self.layout.addWidget(QLabel("Port:", self), 1, 0)
        self.layout.addWidget(self.port_input, 2, 0)

        # baud rate input box
        self.baud_input = QLineEdit("115200", self)
        self.baud_input.setValidator(QIntValidator(self))
        self.layout.addWidget(QLabel("Baud rate:", self), 1, 1)
        self.layout.addWidget(self.baud_input, 2, 1)

        # start/stop mat recording session
        self.start_session_b = QPushButton("Start Session")
        self.start_session_b.clicked.connect(self.start_session)
        self.stop_session_b = QPushButton("Stop Session")
        self.stop_session_b.setEnabled(False)   # start disabled because there is no session yet
        self.stop_session_b.clicked.connect(self.stop_session)
        self.session_status = QLabel("Status: Session Stopped")
        self.layout.addWidget(self.start_session_b, 5, 0)
        self.layout.addWidget(self.stop_session_b, 6, 0)
        self.layout.addWidget(self.session_status, 5, 2)
        self.calibration = Calibration(ROW_WIDTH, COL_HEIGHT)    # the calibration class instance to apply to the session when it is started
        
        # load past session
        self.load_past_img_b = QPushButton("Load Past Session")
        self.load_past_img_b.clicked.connect(self.load_past_img)
        self.layout.addWidget(self.load_past_img_b, 7, 0)

        # navigate past session buttons
        self.load_past_img_next_b = QPushButton("-->")
        self.load_past_img_prev_b = QPushButton("<--")
        self.load_past_img_next_b.clicked.connect(self.load_past_img_next)
        self.load_past_img_prev_b.clicked.connect(self.load_past_img_prev)
        self.layout.addWidget(self.load_past_img_next_b, 8, 1)
        self.layout.addWidget(self.load_past_img_prev_b, 8, 0)
   
        # set up image label
        self.im_size = QSize(COL_HEIGHT*10, ROW_WIDTH*10)
        self.im_label = QLabel()
        self.qimage = QImage()
        self.layout.addWidget(self.im_label, 0, 2)

        # add a label for showing stats about the image
        self.mat_stats_label = QLabel("Mat reading stats:\nNone")
        self.layout.addWidget(self.mat_stats_label, 0, 1)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.show()

        # declare the existance of a session thread
        self.session_thread = None


    def show_reading_statistics(self, reading: np.ndarray):
        """
        Updates the mat_stats_label with statistics about the mat
        """
        stats = calc_mat_reading_stats(reading)
        self.mat_stats_label.setText(stats)


    def get_calibration_data(self):
        """
        Should be called after the user has entered a value into the calibrate_input corresponding to a weight they have placed on the mat\
        Adds the mat readings to a list of mat readings that are used to calculate mat calibration curves by self.get_calibration_data()
        """
        calibration_weight = float(self.calibrate_input.text())
        print("Calibrating with weight", calibration_weight)

        # start up the thread to collect a reading from the mat
        cal_thread = QThread(self)
        cal_worker = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=calibration_weight)
        cal_worker.moveToThread(cal_thread)

        # connect important signals to the new thread
        cal_thread.started.connect(cal_worker.run)
        cal_worker.finished.connect(cal_thread.quit)
        cal_worker.finished.connect(cal_worker.deleteLater)
        cal_thread.finished.connect(cal_thread.deleteLater)

        # start the thread to collect a reading from the mat
        cal_thread.start()
        self.calibrate_status.setText("Getting data...")
        self.calibrate_b.setEnabled(False)
        self.calibrate_complete_b.setEnabled(False)

        # connect cleanup signals
        cal_worker.reading_result.connect(
            self.add_calibration_data
        )
        cal_thread.finished.connect(
            lambda: self.calibrate_status.setText(f"{len(self.calibration.listOfMatReadings)} Cal Samples")
        )
        cal_thread.finished.connect(lambda: self.calibrate_b.setEnabled(True))
        cal_thread.finished.connect(lambda: self.calibrate_complete_b.setEnabled(True))


    def add_calibration_data(self, reading: MatReading):
        """
        Adds a MatReading to the calibration instance
        """
        self.calibration.add_reading(reading)


    def complete_calibration(self):
        """
        Calculate the calibration curves and prevent further readings from being added
        """
        print(f"Calculating calibration curves")
        self.calibration.calculate_calibration_curves()
        self.calibrate_status.setText("Calibrated!")


    def start_session(self):
        print("I will start a mat recording session capped at 1 hour")

        # set up the thread which the session worker will run on
        self.session_thread = QThread()

        # load default calibration if the calibrator is uncalibrated
        if not self.calibration.calibrated:
            print("Using default calibration curves")
            self.calibration.load_cal_curves(DEFAULT_CAL_CURVES_PATH)

        self.session = SessionWorker(self.port_input.text(), self.baud_input.text(), calibrator=self.calibration)

        # move the session worker onto the thread
        self.session.moveToThread(self.session_thread)

        # connect relevant signals
        self.session_thread.started.connect(self.session.run)
        self.session.finished.connect(self.session_thread.quit)
        self.session.finished.connect(self.session.deleteLater)
        self.session_thread.finished.connect(self.session_thread.deleteLater)

        # start the thread with the session on it
        self.session_thread.start()
        self.session_status.setText("Session running")

        self.stop_session_b.setEnabled(True)

        # connect useful signals
        self.session_thread.finished.connect(
            lambda: self.stop_session_b.setEnabled(False)
        )
        self.session_thread.finished.connect(
            lambda: self.session_status.setText("Session stopped")
        )
        self.session.calculated_pressures.connect(
            self.render_pressure_array
        )


    def stop_session(self):
        print("I will stop the mat recording session")
        if self.session:
            self.session.stop()
 

    def render_pressure_array(self, pressure_array: np.ndarray):
        """
        Converts an array of pressure values to an image based on the saved 
        """

        self.show_reading_statistics(pressure_array)

        # 1. Convert the raw pressure values to color values based on a function
        print(np.max(pressure_array.flatten()))
        scaled_array = (pressure_array / MAX_RATED_PRESSURE_PA)


        im_array = np.full((ROW_WIDTH, COL_HEIGHT, 3), 255) * scaled_array[..., np.newaxis]
        im_array = im_array.astype(np.uint8)
        print(scaled_array.shape, im_array.shape)

        #for i in range(COL_HEIGHT):
        #    line = ""
        #    for j in range(ROW_WIDTH):
        #        line += str((im_array[j, i])) + " "
        #    print(line)

        # https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
        # https://copyprogramming.com/howto/pyqt5-convert-2d-np-array-to-qimage
        
        image = QImage(im_array.data, im_array.shape[1], im_array.shape[0], QImage.Format.Format_RGB888)
        self.im_label.setPixmap(QPixmap(image).scaled(self.im_size))

        # 3. Force the GUI to update its image



    def load_img(self, im_path):
        """
        Loads the image at im_path and puts it on the image label for viewing
        """
        # find the relative path of the image (sessions/sessionname/xxxx.png), i.e. the last three elements of the path
        self.current_img_path = Path('').joinpath(*Path(im_path).parts[-3:])

        # get just the number from the filename
        self.current_img_index = int(self.current_img_path.stem)

        # update the pixmap with the new image
        self.im_label.setPixmap(QPixmap(im_path).scaled(self.im_size))


    def load_past_img(self):
        """
        opens file selector, saves a selected image, scales it, then displays it
        """
        fname = self.getfile()
        print("fname = ", fname)

        self.load_img(im_path=fname)


    def get_next_file(self, prev_or_next):
        """
        input 1 for next file, -1 for previous file. 
        Performs string manipulations to update the current image index and file path
        """
        #check if valid arguement was passed to function
        if(prev_or_next == 1 or prev_or_next == -1):

            #check if trying to access a negative index file
            if(self.current_img_index == 0 and prev_or_next == -1):
                print("there is no image before image 0")
                return            

            next_file_index = self.current_img_index + prev_or_next
            next_file_name = str(next_file_index)

            #add zeros to next_index to make it the propper file name
            while(len(next_file_name) < 4):
                next_file_name = "0" + next_file_name

            #remove the previous image's file name, but keep its path, add the next/previous file name
            next_file_path = self.current_img_path[:(len(self.current_img_path)-8)] + next_file_name + ".png"

            #if the next file exists then open it
            if(os.path.isfile(next_file_path)):
                self.current_img_index = next_file_index
                self.current_img_path = next_file_path
                
            else:
                print("next file does not exist")
                return
        else:
            print("invalid arguement passed to get_next_img()")
            return
        

    def load_past_img_next(self):
        """
        when image navigator is clicked, this updates the image to the file with the next index
        """
        self.get_next_file(1)
        self.im_label.setPixmap(QPixmap(self.current_img_path).scaled(self.im_size))


    def load_past_img_prev(self):
        """
        when image navigator is clicked, this updates the image to the file with the previous index
        """
        self.get_next_file(-1)
        self.im_label.setPixmap(QPixmap(self.current_img_path).scaled(self.im_size))


    def closeEvent(self, event):
        """
        Called when the window is closed. Exit the application
        """
        self.stop_session()


    def getfile(self):
        """
        opens file selector, allows user to navigate their directories, 
        and returns a string of the full file name
        """
        #default file path below
        file_path = ('./')

        fname_full = QFileDialog.getOpenFileName(self, 'Open file', file_path,"Image files (*.png)")
        return fname_full[0]



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    # 4. Show your application's GUI
    window.show()

    # 5. Run your application's event loop
    sys.exit(app.exec())

