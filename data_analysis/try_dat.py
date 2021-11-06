#!/usr/bin/env python3
import argparse


import coloredlogs
import logging
import matplotlib

# from lib.twominus_defines import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=log)

logging.getLogger("matplotlib").setLevel(logging.INFO)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


import numpy as np
from matplotlib import pyplot as plt

data_dir = "data/"
file_name = "AdcData-11-5-20-48-30.dat"
file_path = data_dir + file_name

frame_head = 0xeb9055aa
frame_tail = 0xeb905aa5

def main(plot_frame):

    with open(file_path, 'rb') as f:
        hexdata = f.read().hex()

    hexlist = list(map(''.join, zip(*[iter(hexdata)] * 8)))

    intlist = [int(x, 16) for x in hexlist]

    data_nparr = np.asarray(intlist, dtype=int)

    head_location = np.where(data_nparr == frame_head)[0]
    tail_location = np.where(data_nparr == frame_tail)[0]

    log.debug("Head location: {:}".format(head_location))
    log.debug("Tail location: {:}".format(tail_location))

    assert head_location.size >= tail_location.size

    if head_location[0] > tail_location[0]:
        tail_location = np.delete(tail_location, 0)

    log.debug("Head location: {:}".format(head_location))
    log.debug("New Tail location: {:}".format(tail_location))

    num_frame = tail_location.size

    frame_slices = []

    for i in range(num_frame):
        log.debug("head_location: {}, tail_location: {}".format(head_location[i], tail_location[i]))
        new_frame = data_nparr[(head_location[i]+8):tail_location[i]]
        print(hex(data_nparr[tail_location[i]-2]))
        log.debug("New frame index: {}, length: {}, number of channel data: {}".format(i, new_frame.size, new_frame.size/4))
        frame_slices.append(new_frame)

    frame_show = frame_slices[plot_frame]

    plt.plot(frame_show)

    ch_a = frame_show[0:frame_show.size:4]
    ch_b = frame_show[1:frame_show.size:4]
    ch_c = frame_show[2:frame_show.size:4]
    ch_d = frame_show[3:frame_show.size:4]

    np.savetxt(data_dir+"ch_a.txt", ch_a, delimiter='\n', fmt='%08x') 
    np.savetxt(data_dir+"ch_b.txt", ch_b, delimiter='\n', fmt='%08x') 
    np.savetxt(data_dir+"ch_c.txt", ch_c, delimiter='\n', fmt='%08x') 
    np.savetxt(data_dir+"ch_d.txt", ch_d, delimiter='\n', fmt='%08x') 

    # calculate volt

    fig, ((ax1, ax2), (ax3,ax4)) = plt.subplots(2,2)
    adc_index = 1
    fig.suptitle("The adc9252 ({:}) value of each channel. Frame index: {:}.".format(adc_index ,int(plot_frame)))

    ax1.plot(ch_a, marker='o', color="grey")
    ax2.plot(ch_b, marker='+', color="salmon")
    ax3.plot(ch_c, marker='s', color="wheat")
    ax4.plot(ch_d, marker=' ', color="yellowgreen")

    ax1.set_title("Channel: 1")
    ax2.set_title("Channel: 2")
    ax3.set_title("Channel: 3")
    ax4.set_title("Channel: 4")

    ax1.set_xlabel("Data index")
    ax1.set_ylabel("Data value")
    ax2.set_xlabel("Data index")
    ax2.set_ylabel("Data value")
    ax3.set_xlabel("Data index")
    ax3.set_ylabel("Data value")
    ax4.set_xlabel("Data index")
    ax4.set_ylabel("Data value")
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode_group = parser.add_mutually_exclusive_group()
    # mode_group.add_argument('-a', '--all',
                            # help="nothing here",
                            # action="store_true")
    parser.add_argument('-p', '--plot_frame',
                        type=int,
                        default=0,
                        help="The frame to be plot.")
    args = parser.parse_args()

    main(plot_frame=args.plot_frame)