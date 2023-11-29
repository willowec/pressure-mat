"""
Program which calculates mat read speed of the mat without any overhead
"""

import matplotlib.pyplot as plt
import numpy as np
import sys, time, argparse

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *
from modules.communicator import *
from modules.mat_handler import *


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=str, default="COM3", help="The com port the mat is plugged in to")

    args = parser.parse_args()

    total_errors = 0
    periods = []
    prev_time = time.time_ns()
    start_time = time.time()

    with serial.Serial(args.port, baudrate=115200, timeout=10) as ser:
        # send the message to start reading the mat
        ser.write((START_READING_COMMAND + '\n').encode('utf-8'))

        try:
            while True:
                # mat data is transmitted as a string in hexadecimal format
                m = ser.readline()
                m = str(m.decode('utf-8'))
                
                # skip if the result of a timeout (empty)
                if m == '' or m == '\r\n':
                    continue

                # skip if the result of a timeout (no newline)
                if not (m[-1] == '\n'):
                    print("Serial timed out!! b", m)
                    continue

                # skip if the line is a debug message
                if m.startswith("DEBUG"):
                    print(m)
                    continue

                # trim off the \n\r
                m = m[:-2]

                # get the mat as a flat list
                flat_mat = hex_string_to_array(m)

                try:
                    data_array = mat_list_to_array(flat_mat)
                except IndexError:
                    total_errors += 1
                    print("INDEX ERROR~!!")
                    continue

                now = time.time_ns()
                delta = now - prev_time
                prev_time = now
                periods.append(delta)

                # print(f"{delta:05f}")

        except KeyboardInterrupt as e:
            # plot the periods over time

            periods = np.asarray(periods[1:])
            avg_period = np.average(periods)

            print(f"Total run time in seconds: {time.time() - start_time}s")
            print(f"Average delta time between mat reads: {avg_period}ns")
            print(f"Total errors: {total_errors}")
            plt.plot(periods)
            plt.show()



