import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# hack to allow importing the modules: add parent directory to path
sys.path.append('..')
from modules.calibration import *
from modules.mat_handler import *

data_files = list(Path("./raw_data").glob("*.csv"))

for path in data_files:
    pa = float(str(path).split('_')[2].split('pa')[0])
    acc_pa = pa * SENSOR_AREA_SQM / MAT_AREA_SQM
    print(pa, acc_pa)