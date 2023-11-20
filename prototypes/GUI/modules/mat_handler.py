"""
File for helper functions related to the Mat that multiple modules may need to import
"""
import numpy as np

ROW_WIDTH = 28
COL_HEIGHT = 56
MAT_SIZE = 1568

START_READING_COMMAND = "start_reading"
GET_CAL_VALS_COMMAND = "get_cal_vals"



def hex_string_to_array(hex_string):
    """
    Converts a string of 02x hexadecimal numbers to an array
    """
    numbers = []
    for i in range(0, len(hex_string), 2):
        x = hex_string[i: i+2]
        numbers.append(int(x, 16))
    
    return numbers


def print_2darray(array: np.ndarray):
    """
    Function which prints a 2d uint8 numpy array in a readable format
    """
    for row in range(array.shape[1]):
        line = ""
        for i in range(array.shape[0]):
            try:
                line += f"{array[i, row]:03d} "
            except ValueError:
                line += f"{array[i, row]:3.2f} "
        print(line)


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


def calc_mat_reading_stats(mat_samples_pa: np.array):
    """
    Calculates some useful statistics about the mat reading and returns them as a string
    """
    flat_mat = mat_samples_pa.flatten()
    max_pa = np.max(flat_mat)
    min_pa = np.min(flat_mat)
    average_pa = round(np.average(flat_mat), 2)

    return f"    Max pressure: {max_pa}Pa\n    Min pressure: {min_pa}Pa\n    Avg pressure: {average_pa}Pa"