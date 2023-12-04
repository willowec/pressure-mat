"""
Program which calculates the sample rate of the mat without any calibration/data saving overhead
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

    successful_reads = 0

    with serial.Serial(args.port, baudrate=115200, timeout=10) as ser:
        # send the message to start reading the mat
        ser.write((START_READING_COMMAND + '\n').encode('utf-8'))

        try:
            while True:
                # mat data is transmitted as raw bytes
                bytes = ser.read(VERIFICATION_WIDTH + MAT_SIZE)
                if bytes == b'':
                    print("Serial timed out!")
                    continue
                
                flat_mat = [x for x in bytes]

                # ensure that the verifiation message was aligned
                for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
                    if not (ver == val):
                        print(f"Verification failure! On reading: \n{flat_mat}\nMade it {len(periods)} readings before failure")
                        raise KeyboardInterrupt # give up

                flat_mat = flat_mat[-4:] # trim the verification sequence

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



