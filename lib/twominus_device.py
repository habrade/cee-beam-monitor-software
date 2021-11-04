import os
import datetime

import coloredlogs
import logging

from lib.twominus_defines import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class TwominusDevice:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "twominus_dev."
        log.debug("TwoMinus device initailed.")


    def w_reg(self, reg_name, reg_val, is_pulse, go_dispatch):
        """
        The register write function for Twominus device.

        :param reg_name:
        :param reg_val:
        :param is_pulse:
        :param go_dispatch:
        :return:
        """
        self._ipbus_link.w_reg(self.reg_name_base, reg_name, reg_val, is_pulse, go_dispatch)

    def r_reg(self, reg_name):
        """
        The register read function for Twominus device.

        :param reg_name:
        :return:
        """
        return self._ipbus_link.r_reg(self.reg_name_base, reg_name)

    def start_scan(self):
        reg_name = "start_scan"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def reset_scan(self):
        reg_name = "reset_scan"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def resync(self):
        reg_name = "datapath_resync"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)
    
    def reset_datapath(self):
        reg_name = "datapath_soft_rst"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def path_reset_datapath(self):
        reg_name = "datapath_soft_path_rst"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def pack_start_datapath(self):
        reg_name = "datapath_soft_pack_start"
        return self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)
    
    def set_data_type(self, val):
        reg_name = "data_type"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)

    def set_time_high(self, val):
        reg_name = "time_high"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)

    def set_time_mid(self, val):
        reg_name = "time_mid"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)

    def set_time_low(self, val):
        reg_name = "time_low"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)

    def set_time_usec(self, val):
        reg_name = "time_usec"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)

    def set_chip_cnt(self, val):
        reg_name = "chip_cnt"
        return self.w_reg(reg_name, val, is_pulse=False, go_dispatch=True)
    
    def set_time(self):
        """ Set time"""
        now = datetime.datetime.now()
        log.debug("Now: {}".format(now))
        time_high = (now.year<<4) + now.month
        time_mid = (now.day<<8) + now.hour
        time_low = (now.minute<<8) + now.second
        time_us = now.microsecond

        log.debug("Time high: {} Time mid: {} Time low: {} time_us: {}".format(time_high, time_mid, time_low, time_us))

        self.set_time_high(time_high)
        self.set_time_mid(time_mid)
        self.set_time_low(time_low)
        self.set_time_usec(time_us)

    def get_data_lost(self):
        reg_name = "data_lost_counter"
        return self.r_reg(reg_name)

    def send_slow_ctrl_cmd(self, cmd):
        """
        Write to WFIFO.

        :param cmd: Data list.
        :return:
        """
        self._ipbus_link.send_slow_ctrl_cmd(self.reg_name_base, "SLCTRL_FIFO", cmd)

    def write_ipb_data_fifo(self, data_list):
        """
        Write to WFIFO (Block write).

        :param data_list:
        :return:
        """
        self._ipbus_link.write_ipb_slow_ctrl_fifo(self.reg_name_base, "SLCTRL_FIFO", data_list)

    def read_ipb_data_fifo(self, num, safe_mode):
        """
        Read from RFIFO.

        :param num:
        :param safe_mode: True: safe read. False: not safe read for fast speed.
        :param try_time: How many times to try to read
        :return:
        """
        return self._ipbus_link.read_ipb_data_fifo(self.reg_name_base, "DATA_FIFO", num, safe_mode)

    def reset_rfifo(self):
        """
        Reset RFIFO.

        :return:
        """
        log.info("Reset readout FIFO.")
        self.w_reg("DATA_FIFO.rst_rfifo", 0, is_pulse=True, go_dispatch=True)

    def read_fifo_len(self):
        len = self.r_reg("DATA_FIFO.RFIFO_LEN")
        log.debug("Valid number in DATA FIFO: {}".format(len))
        return len
        
    def read_data(self, read_times=1000, safe_mode=True):
        mem = []
        # while True:
        #     mem0 = self.read_ipb_data_fifo(slice_size, safe_mode=safe_mode)
        #     if len(mem0) > 0:
        #         mem.append(mem0)
        #     if not self.is_busy_rs():
        #         break
        # try read more data
        for i in range(read_times):
            mem0 = self.read_ipb_data_fifo(slice_size, safe_mode=safe_mode)
            if len(mem0) > 0:
                mem.append(mem0)

        return mem

    @staticmethod
    def write2txt(data_file, mem):
        if len(mem) == 0:
            log.error("Data memory is emtpy, quit!")
            return False
        else:
            try:
                os.remove(data_file)
            except OSError:
                pass

            data_string = []
            with open(data_file, 'a') as data_file:
                for mem0 in mem:
                    for data in mem0:
                        data_string.append("{:08x}\n".format(data))
                data_file.write("".join(data_string))
            log.info("Write to .txt end.")
            return True
   