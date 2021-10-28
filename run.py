#!/usr/bin/env python3
import argparse

import time
import coloredlogs
import logging

from lib.ad9512_device import Ad9512Device
from lib.freq_ctr_device import FreqCtr
from lib.global_device import GlobalDevice
from lib.ipbus_link import IPbusLink
from lib.twominus_device import TwominusDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


def fre_counter(freq_ctr_dev):
    N_CLK = 3
    clock_name = ["tm_clk", "adc9252_fclk", "data_fifo_wr_clk"]
    for i in range(N_CLK):
        time.sleep(2)
        freq = freq_ctr_dev.get_chn_freq(i)
        log.info("Tested {:s} frequency is : {}".format(clock_name[i], freq))

def main(ad9512_initial, dataout_file):
    ## Get ipbus connection
    ipbus_link = IPbusLink()
    
    global_dev = GlobalDevice(ipbus_link)
    # global_dev.set_nuke()
    ## Soft reset
    global_dev.set_soft_rst()

    if ad9512_initial == True:
        ad9512_dev = Ad9512Device(ipbus_link)
        # Set AD9512
        ad9512_dev.set_ad9512()
    
    ## Set TwoMinus
    twominus_dev = TwominusDevice(ipbus_link)
    twominus_dev.reset_ad9252()
    twominus_dev.path_reset_ad9252()
    # twominus_dev.pack_start_ad9252()

    twominus_dev.set_chip_cnt(0x70)
    twominus_dev.set_data_type(0)
    twominus_dev.set_time()

    twominus_dev.reset_scan()
    twominus_dev.start_scan()

    twominus_dev.resync()

    # read data
    mem = twominus_dev.read_ipb_data_fifo(10, safe_mode=True)
    print(mem)

    ## Test clock frq
    # freq_ctr_dev = FreqCtr(ipbus_link)
    # fre_counter(freq_ctr_dev)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-a', '--all',
                            help="Global reset, initial spi, dac70004 and start rolling shutter",
                            action="store_true")
    parser.add_argument('-ad9512', '--ad9512_initial',
                        help="Setting AD9512",
                        action="store_true")
    parser.add_argument('-o', '--output_file',
                        default="data/dataout.txt",
                        help="The path for saving the results (.txt) of pixel scanning.")
    args = parser.parse_args()

    if args.all:
        main(ad9512_initial=True, dataout_file=args.output_file)
    else:
        main(ad9512_initial=args.ad9512_initial, dataout_file=args.output_file)
