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

from modules.calibration import Calibration, CalSampleWorker, MAX_RATED_PRESSURE_PA, DEFAULT_CAL_CURVES_PATH
from modules.communicator import SessionWorker, ROW_WIDTH, COL_HEIGHT
from modules.mat_handler import calc_mat_reading_stats


class MainWindow(QMainWindow):
    """
    Class which handles the main 
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("28x56 Mat Interface")

        self.current_img_path = "default.png"

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
        self.session_stats = QLabel("Session stats: No session")
        self.layout.addWidget(self.start_session_b, 5, 0)
        self.layout.addWidget(self.stop_session_b, 6, 0)
        self.layout.addWidget(self.session_status, 5, 2)
        self.layout.addWidget(self.session_stats, 6, 2)
        self.calibration = Calibration(ROW_WIDTH, COL_HEIGHT)    # the calibration class instance to apply to the session when it is started
        
        # load past session
        self.load_past_session_b = QPushButton("Load Past Session")
        self.load_past_session_b.clicked.connect(self.load_past_session)
        self.layout.addWidget(self.load_past_session_b, 7, 0)

        # zero mat
        self.zero_mat_b = QPushButton("Zero Mat")
        self.zero_mat_b.clicked.connect(self.zero_mat)
        self.zeroing_status = QLabel("Status: Not Zeroed")
        self.layout.addWidget(self.zero_mat_b, 8, 0)
        self.layout.addWidget(self.zeroing_status, 8, 1)


        # navigate images with slider
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self.get_npy_file_from_slider)
        self.layout.addWidget(self.slider, 1, 2)
   
        # set up image label
        self.im_size = QSize(COL_HEIGHT*10, ROW_WIDTH*10)
        self.im_label = QLabel()
        self.qimage = QImage()
        self.layout.addWidget(self.im_label, 0, 2)

        # add a label for showing stats about the image
        self.mat_stats_label = QLabel("Mat reading stats:\nNone")
        self.layout.addWidget(self.mat_stats_label, 0, 1)

        # add an entry for putting in the expected uniform weight value in lbs
        self.mat_expected_weight = QLineEdit("-1", self)
        self.mat_expected_weight.setValidator(QDoubleValidator(self))
        self.layout.addWidget(self.mat_expected_weight, 0, 0)

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
        expected = -1
        if self.mat_expected_weight.text() != '':
            expected = float(self.mat_expected_weight.text())

        stats = calc_mat_reading_stats(reading, expected)
        self.mat_stats_label.setText(stats)


    def zero_mat(self, index:int=0):
        """
        A recursive function that reads the mat 10 times, and adds those readings to the zeroing zeroing data in the calibration class
        """
            
        if(index == 0):
            print("Zeroing mat")
            self.zero_mat_b.setEnabled(False)

            # start up the thread to collect a reading from the mat
            self.cal_thread0 = QThread(self)
            self.cal_worker0 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread0, self.cal_worker0,index)
        elif(index == 1):
            # start up the thread to collect a reading from the mat
            self.cal_thread1 = QThread(self)
            self.cal_worker1 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread1, self.cal_worker1,index)
        elif(index == 2):
            # start up the thread to collect a reading from the mat
            self.cal_thread2 = QThread(self)
            self.cal_worker2 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread2, self.cal_worker2, index)
        elif(index == 3):
            # start up the thread to collect a reading from the mat
            self.cal_thread3 = QThread(self)
            self.cal_worker3 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread3, self.cal_worker3, index)
        elif(index == 4):
            # start up the thread to collect a reading from the mat
            self.cal_thread4 = QThread(self)
            self.cal_worker4 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread4, self.cal_worker4, index)
        elif(index == 5):
            # start up the thread to collect a reading from the mat
            self.cal_thread5 = QThread(self)
            self.cal_worker5 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread5, self.cal_worker5, index)
        elif(index == 6):
            # start up the thread to collect a reading from the mat
            self.cal_thread6 = QThread(self)
            self.cal_worker6 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread6, self.cal_worker6, index)
        elif(index == 7):
            # start up the thread to collect a reading from the mat
            self.cal_thread7 = QThread(self)
            self.cal_worker7 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread7, self.cal_worker7, index)
        elif(index == 8):
            # start up the thread to collect a reading from the mat
            self.cal_thread8 = QThread(self)
            self.cal_worker8 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread8, self.cal_worker8, index)
        elif(index == 9):
            # start up the thread to collect a reading from the mat
            self.cal_thread9 = QThread(self)
            self.cal_worker9 = CalSampleWorker(self.port_input.text(), int(self.baud_input.text()), calibration_weight=0)
            self.run_cal_worker_thread(self.cal_thread9, self.cal_worker9,index)
        else:
            print("End of zeroing")
            self.calibration.calc_dc_offsets()
            self.zero_mat_b.setEnabled(True)
            self.zeroing_status.setText("Zeroing Complete")
            return
        


    def run_cal_worker_thread(self, thread: QThread, worker: CalSampleWorker, index:int):
        """
        Runs QThread and Worker to gather mat readings. Calls Zero_mat() of the next index when done
        """
        # start up the thread to collect a reading from the mat
        worker.moveToThread(thread)

        # connect important signals to the new thread
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # start the thread to collect a reading from the mat
        thread.start()
        self.zeroing_status.setText("Getting data...")
        
        # connect cleanup signals
        worker.reading_result.connect(
            self.calibration.add_zeroing_data
        )

        thread.finished.connect(
            lambda: self.zero_mat(index+1)
        )


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
        self.session.session_stats.connect(
            self.update_session_stats
        )
        self.session.finished_session_stats.connect(
            self.finish_session_stats
        )

    def stop_session(self):
        print("I will stop the mat recording session")
        if self.session:
            self.session.stop()
 

    def update_session_stats(self, message):
        """
        Callback function for the session_stats signal of the SessionWorker. Updates the GUI with some live statistics
        """
        self.session_stats.setText(f"Session stats:\n{message}")


    def finish_session_stats(self, message):
        """
        Callback function for the finished_session_stats signal of SessionWorker, adds overall stats to the GUI
        """
        print("calling finish")
        self.session.session_stats.disconnect()
        stats_text = self.session_stats.text()
        self.session_stats.setText(stats_text + '\n' + message)


    def render_pressure_array(self, pressure_array: np.ndarray):
        """
        Converts an array of pressure values to an image based on the saved 
        """

        # write the stats of the current reading
        self.show_reading_statistics(pressure_array)

        # convert the raw pressure values to color values
        scaled_array = (pressure_array / MAX_RATED_PRESSURE_PA)

        im_array = np.full((ROW_WIDTH, COL_HEIGHT, 3), 255) * scaled_array[..., np.newaxis]
        im_array = im_array.astype(np.uint8)


        # convert the numpy array directly to an image in memory. See these resources:
        #   https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
        #   https://copyprogramming.com/howto/pyqt5-convert-2d-np-array-to-qimage
        image = QImage(im_array.data, im_array.shape[1], im_array.shape[0], QImage.Format.Format_RGB888)
        self.im_label.setPixmap(QPixmap(image).scaled(self.im_size))


    def load_past_session(self):
        """
        opens file selector, saves a selected image, scales it, then displays it, and updates the slider
        """
        fname = self.getfile()
        #print("fname = ", fname)

        self.current_img_path = fname

        new_npy = np.load(fname, allow_pickle=False)

        self.render_pressure_array(new_npy)

        #updating the slider with the current session folder
        self.update_slider()


    def get_npy_file_from_slider(self):
        """
        gets the current slider value, 
        converts that value to a npy file name (xxxxx.npy), 
        then renders the .npy file to the screen
        """

        #convert slider value to string with padded zeros and .npy extension
        next_npy_file = f"{self.slider.value():05}"
        next_npy_file = next_npy_file + ".npy"

        #converts current_img_path to path type to get the parent directory and then find the next npy file in that directory, then converts back to string
        self.current_img_path = str((Path(self.current_img_path).parents[0]).joinpath(Path(next_npy_file)))

        new_npy = np.load(self.current_img_path, allow_pickle=False)

        self.render_pressure_array(new_npy)


    def update_slider(self):
        """
        sets the maximum value of the slider bassed on how many images are in the session and sets slider position to zero
        """

        self.slider.setMaximum(self.count_files_in_folder(Path(self.current_img_path).parents[0])-1)
        self.slider.setValue(0)


    def count_files_in_folder(self, dir_path):
        """
        Used to count the number of files in a folder. From https://pynative.com/python-count-number-of-files-in-a-directory/
        """

        count = 0
        # Iterate directory
        for path in os.listdir(dir_path):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1

        return count


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

        fname_full = QFileDialog.getOpenFileName(self, 'Open File', file_path)
        self.current_img_path = fname_full
        return fname_full[0]


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    # 4. Show your application's GUI
    window.show()

    # 5. Run your application's event loop
    sys.exit(app.exec())

