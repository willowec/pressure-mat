"""
File for helper functions related to the Mat that multiple modules may need to import
"""
import numpy as np
import os

ROW_WIDTH = 28
COL_HEIGHT = 56
MAT_SIZE = 1568
SENSOR_AREA_SQM = 0.0001        # Area of each individual sensor in square meters (1cm^2)

START_READING_COMMAND = "start_reading"
GET_CAL_VALS_COMMAND = "get_cal_vals"

# the verificaiton message sent by the board
VERIFICATION_WIDTH = 4
VERIFICATION_SEQUENCE = [255, 254, 254, 255]



def print_2darray(array: np.ndarray, highlight_max: bool=False):
    """
    Function which prints a 2d uint8 numpy array in a readable format
    """
    max_index = None
    if highlight_max:
        os.system("") # enable color printing on windows terminals
        max_index = np.unravel_index(array.argmax(), array.shape)

    for row in range(array.shape[1]):
        line = ""
        for col in range(array.shape[0]):

            suffix = ""
            if max_index is not None:
                # add a color code when printing the value if it is at the max index
                if (max_index[0] == col and max_index[1] == row):
                    line += "\x1b[1;92m" # make the value green
                    suffix = "\x1b[38;5;15m" # return to white afterwards
            try:
                line += f"{array[col, row]:03d} "
            except ValueError:
                line += f"{array[col, row]:3.2f} "

            line += suffix
        print(line)
    
    return max_index


def prettyprint_mat(mat_as_list: list):
    """
    Python version of the board_code prettyprint_mat function
    """
    line = ""
    for i in range(MAT_SIZE):
        if (i % ROW_WIDTH) == 0:
            print(line[:-1])
            line = ""
 
        line += f"{mat_as_list[i]:02x}, "


def mat_list_to_array(mat_as_list: list):
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


def lbs_to_neutons(force_lbs: float) -> float:
    """
    Function which converts pounds force to newtons force
    """
    return force_lbs * 4.44822


def calc_percent_error(experimental, theoretical):
    return (experimental - theoretical) / theoretical * 100


def calc_mat_reading_stats(mat_samples_pa: np.array, expected_weight: float):
    """
    Calculates some useful statistics about the mat reading and returns them as a string
    """
    flat_mat = mat_samples_pa.flatten()
    max_pa = np.max(flat_mat)
    min_pa = np.min(flat_mat)
    average_pa = round(np.average(flat_mat), 2)

    errors_msg = "Put the expected distributed weight value (in lbs) into the entry to the left to see error!"
    if expected_weight > 0:
        expected_pa = lbs_to_neutons(expected_weight) / (MAT_SIZE * SENSOR_AREA_SQM)

        errors = np.empty_like(flat_mat)
        for i in range(len(errors)):
            errors[i] = calc_percent_error(flat_mat[i], expected_pa)

        min_err = round(np.min(np.abs(errors)), 2)
        max_err = round(np.max(np.abs(errors)), 2)
        avg_err = round(np.average(np.abs(errors)), 2)
        median_err = round(np.median(np.abs(errors)), 2)

        errors_msg = f"    Errors:\n    Min % err: {min_err}\n    Max % err: {max_err}\n    Avg % err: {avg_err}\n    Median % err: {median_err}"

    return f"    Max pressure: {max_pa}Pa\n    Min pressure: {min_pa}Pa\n    Avg pressure: {average_pa}Pa\n    {errors_msg}"