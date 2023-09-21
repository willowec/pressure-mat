# GUI which displays data from the mat interpreted by the board and transmitted over serial
import sys, serial

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QGridLayout, QWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QThread

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('QtAgg')

from PIL import Image

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

MAT_DIM = (28, 56)
HIST_LEN = 25


class MplCanvas(FigureCanvasQTAgg):
    """
    https://www.pythonguis.com/tutorials/pyqt6-plotting-matplotlib/
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class MainWindow(QMainWindow):
    """
    Class which handles the main 
    """

    # initial class generated by chatgpt
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("28x56 Mat Interface")

        self.layout = QGridLayout()
        
        #com port input box
        self.port_input = QLineEdit("COM8", self)
        self.layout.addWidget(QLabel("Port:", self), 0, 0)
        self.layout.addWidget(self.port_input, 1, 0)

        #baud rate input box
        self.baud_input = QLineEdit("115200", self)
        self.layout.addWidget(QLabel("Baud rate:", self), 0, 1)
        self.layout.addWidget(self.baud_input, 1, 1)

        #button to initialize serial connection to pi
        self.connect_b = QPushButton("Connect")
        self.connect_b.clicked.connect(self.connect_board)
        self.status_l = QLabel("Status: N/A")
        self.layout.addWidget(self.connect_b, 2, 0)
        self.layout.addWidget(self.status_l, 2, 1)

        #calibrate mat
        self.calibrate_b = QPushButton("Calibrate Mat")
        self.calibrate_b.clicked.connect(self.calibrate_mat)
        self.calibrate_status = QLabel("Status: Not Calibrated")
        self.layout.addWidget(self.calibrate_b, 3, 0)
        self.layout.addWidget(self.calibrate_status, 3, 1)

        #start/stop mat recording session
        self.start_session_b = QPushButton("Start Session")
        self.start_session_b.clicked.connect(self.start_session)
        self.stop_session_b = QPushButton("Stop Session")
        self.stop_session_b.clicked.connect(self.stop_session)
        self.session_status = QLabel("Status: Session Stopped")
        self.layout.addWidget(self.start_session_b, 4, 0)
        self.layout.addWidget(self.stop_session_b, 5, 0)
        self.layout.addWidget(self.session_status, 4, 1)
        
        #load past session
        self.load_past_img_b = QPushButton("Load Past Session")
        self.load_past_img_b.clicked.connect(self.load_past_img)
        self.layout.addWidget(self.load_past_img_b, 6, 0)


        #navigate past session buttons
        self.load_past_img_next_b = QPushButton("-->")
        self.load_past_img_prev_b = QPushButton("<--")
        self.load_past_img_next_b.clicked.connect(self.load_past_img_next)
        self.load_past_img_prev_b.clicked.connect(self.load_past_img_prev)
        self.layout.addWidget(self.load_past_img_next_b, 8, 3)
        self.layout.addWidget(self.load_past_img_prev_b, 8, 2)

        self.data_pixmap = QPixmap()
        self.data_display = QLabel()
        self.data_text = QLabel()
        self.data_display.setPixmap(self.data_pixmap)
        self.layout.addWidget(self.data_display, 7, 0)
        self.layout.addWidget(self.data_text, 7, 1)

        self.hist_display = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout.addWidget(self.hist_display, 0, 2, 7, 3)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.show()

        # set up the reciever thread
        self.reciever = Reciever("COM8", 115200, self)


    def connect_board(self):
        """
        Called by the connect button
        """
        # attempt to start the reciever thread
        self.reciever.start()

    def calibrate_mat(self):
        print("I will calibrate the board")

    def start_session(self):
        print("I will start a mat recording session capped at 1 hour")

    def stop_session(self):
        print("I will stop the mat recording session")
 
    def load_past_img(self):
        print("I will open a file explorer to select a session from disk memory")

    def load_past_img_next(self):
        print("I will navigate to next image in folder in chronological order")

    def load_past_img_prev(self):
        print("I will navigate to previous image in folder in chronological order")

    def closeEvent(self, event):
        """
        Called when the window is closed. Exit the application
        """
        self.reciever.terminate()


class Reciever(QThread):
    """
    Thread which handles communcations to and from the board
    """
    def __init__(self, port: str, baud: int, parent):
        """
        Port is the com port to connect to and baud is its baud rate
        """
        super(Reciever, self).__init__()
        self.port = port
        self.baud = baud
        self.parent = parent


    def run(self):
        """
        Overrides the run() function. Called by reciever.start()
        """
        # attempt to connect to the board
        with serial.Serial(self.port, baudrate=self.baud, timeout=10) as ser:
            print(f"Connected to {ser.name}")

            # history stores the last HIST_LEN grid values
            self.history = np.zeros((HIST_LEN, 9))

            # poll incoming messages
            i = 0
            while True:
                m = ser.readline().decode('utf-8')
                print('recieved', m)
                if m == '':
                    raise serial.SerialTimeoutException("Timed out")

                # process the message
                vals = m.split('|')[:-1]
                imarray = np.asarray(vals, dtype=np.uint8).reshape(MAT_DIM)
                print('data\n', imarray)

                im = Image.fromarray(imarray, mode='L')
                im.save("sensor_data.png")  # Hack. ideally we should not have to save to file

                # update the pixmap
                self.parent.data_pixmap = QPixmap("sensor_data.png").scaled(100, 100)
                self.parent.data_display.setPixmap(self.parent.data_pixmap)
                self.parent.data_text.setText(str(imarray))

                # update the history array and render it
                self.history = np.roll(self.history, 1, axis=0)
                self.history[0, :] = imarray.flatten()
                #print(self.history)

                # plot it
                self.parent.hist_display.axes.cla()
                self.parent.hist_display.axes.set_ylim(bottom=0, top=256, auto=False)
                self.parent.hist_display.axes.plot(self.history)
                self.parent.hist_display.draw()





if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    # 4. Show your application's GUI
    window.show()

    # 5. Run your application's event loop
    sys.exit(app.exec())