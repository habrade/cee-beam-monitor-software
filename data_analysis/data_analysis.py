#!/usr/bin/env python3

import numpy as np

data_dir = "../data/"

file_name = "arst1.1_30k_200mV_in.dat"

file_path = data_dir + file_name

print(file_path)

c = np.fromfile(file_path, dtype=int)

print(type(c))
