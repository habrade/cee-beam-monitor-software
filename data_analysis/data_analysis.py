#!/usr/bin/env python3

import coloredlogs
import logging

from lib.twominus_defines import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


import numpy as np
from matplotlib import pyplot as plt

data_dir = "data/"
file_name = "dataout.txt"
file_path = data_dir + file_name

frame_head = 0xeb9055aa
frame_tail = 0xeb905aa5

def main():

    data_list = []

    fo = open(file_path, "r")
    
    for frame_hex_string in fo.readlines():
        
        frame_hex_string = frame_hex_string.strip()
        frame_data = int(frame_hex_string, 16)

        data_list.append(frame_data)

    data_nparr = np.asarray(data_list, dtype=int)

    head_location = np.where(data_nparr == frame_head)[0]
    tail_location = np.where(data_nparr == frame_tail)[0]

    log.debug("Head location: {:}".format(head_location))
    log.debug("Tail location: {:}".format(tail_location))

    assert head_location.size >= tail_location.size

    num_frame = tail_location.size

    frame_slices = []

    for i in range(num_frame):
        log.debug("head_location: {}, tail_location: {}".format(head_location[i], tail_location[i]))
        new_frame = data_nparr[(head_location[i]+8):tail_location[i]]
        log.debug("New frame index: {}, length: {}, number of data: {}".format(i, new_frame.size, new_frame.size/4))
        frame_slices.append(new_frame)

    num_chip = 4
    data_arr_ch = []

    # data_ch0_test = frame_slices[0].where()

    # b = np.reshape(frame_slices[8], (2593,4))

    frame_show = frame_slices[0]
    # print(frame_show.size)

    ch_a = frame_show[0:frame_show.size:4]
    ch_b = frame_show[1:frame_show.size:4]
    ch_c = frame_show[2:frame_show.size:4]
    ch_d = frame_show[3:frame_show.size:4]

    
    plt.plot(ch_a)    
    plt.plot(ch_b)    
    plt.plot(ch_c)    
    plt.plot(ch_d)    
    plt.show()


if __name__ == '__main__':
    main()