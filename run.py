#!/usr/bin/env python3

from lib.ad9512_device import Ad9512Device
import time
import coloredlogs
import logging
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
        freq = freq_ctr_dev.get_chn_freq(i)
        log.info("Tested {:s} frequency is : {}".format(clock_name[i], freq))
        time.sleep(1)

def main():
    ## Get ipbus connection
    ipbus_link = IPbusLink()
    
    global_dev = GlobalDevice(ipbus_link)
    ## Soft reset
    # global_dev.set_nuke()
    global_dev.set_soft_rst()

    ad9512_dev = Ad9512Device(ipbus_link)
    twominus_dev = TwominusDevice(ipbus_link)
    freq_ctr_dev = FreqCtr(ipbus_link)

    
    # Set AD9512
    ad9512_dev.set_ad9512()

    # ad9512_dev.ad9512_read_function()
    
    ## Set TwoMinus
    # twominus_dev.reset_ad9252()
    # twominus_dev.path_reset_ad9252()

    # twominus_dev.set_chip_cnt(0x70)
    # twominus_dev.set_data_type(0)
    # twominus_dev.set_time()

    # twominus_dev.pack_start_ad9252()

    ## Test clock frq
    # fre_counter(freq_ctr_dev)


if __name__ == '__main__':
    main()