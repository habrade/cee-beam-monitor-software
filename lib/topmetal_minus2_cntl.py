import logging
import datetime

import coloredlogs


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='INFO', logger=log)


class TopmetalMinus2Cntl:
    def __init__(self, cmd_parse):
        self._cmd_parse = cmd_parse

    def reset(self):
        self._cmd_parse.write_config_reg(31, 1)
        self._cmd_parse.write_config_reg(31, 0)
        self._cmd_parse.set_config_full_range(496, 1)
        self._cmd_parse.set_config_full_range(496, 0)

    def ddr_fifo_reset(self):
        self._cmd_parse.set_config_full_range(497, 1)
        self._cmd_parse.set_config_full_range(497, 0)
 

    def data_reset(self):
        self._cmd_parse.set_config_full_range(497, 1)
        self._cmd_parse.set_config_full_range(497, 0)

    # def tx_fifo_reset(self):
    #     self._cmd_parse.set_config_full_range(498, 1)
    #     self._cmd_parse.set_config_full_range(498, 0)


    # def fifo_reset(self):
    #     self._cmd_parse.set_config_full_range(498, 1)
    #     self._cmd_parse.set_config_full_range(498, 0)


    def dev_reset(self):
        self._cmd_parse.set_config_full_range(499, 1)
        self._cmd_parse.set_config_full_range(499, 0)

    def soft_reset(self):
        self._cmd_parse.set_config_full_range(499, 1)
        self._cmd_parse.set_config_full_range(499, 0)

    def adc_restart(self):
        self._cmd_parse.set_config_full_range(499, 0)
        self._cmd_parse.set_config_full_range(499, 1)
        self._cmd_parse.set_config_full_range(499, 0)

    def soft_pack_start(self):
        self._cmd_parse.set_config_full_range(500, 1)
        self._cmd_parse.set_config_full_range(500, 0)

    def resync(self):
        self._cmd_parse.set_config_full_range(501, 1)
        self._cmd_parse.set_config_full_range(501, 0)

    def soft_path_reset(self):
        self._cmd_parse.set_config_full_range(502, 1)
        self._cmd_parse.set_config_full_range(502, 0)

    def spi_start(self):
        self._cmd_parse.set_config_full_range(16, 0)
        self._cmd_parse.set_config_full_range(16, 1)
        self._cmd_parse.set_config_full_range(16, 0)

    def set_data_type(self, value):
        self._cmd_parse.write_config_reg(4, value)

    def set_time_high(self, value):
        self._cmd_parse.write_config_reg(5, value)

    def set_time_mid(self, value):
        self._cmd_parse.write_config_reg(6, value)

    def set_time_low(self, value):
        self._cmd_parse.write_config_reg(7, value)

    def set_chip_cnt(self, start_nr=0x00, end_nr=0x07):
        """ The upper 8 bits are the chip end number, and the lower eight bits are the chip start number"""
        # log.debug("Chip start number: {:d}, end number: {:d}".format(value>>8, value&0xff))
        self._cmd_parse.write_config_reg(8, start_nr+(end_nr<<8))

    def set_time_usec(self, value):
        self._cmd_parse.write_config_reg(9, value)

    def set_clk_div_in(self, value):
        self._cmd_parse.set_config_full_range(48, value & 0x1)
        self._cmd_parse.set_config_full_range(49, (value >> 1) & 0x1)
        self._cmd_parse.set_config_full_range(50, (value >> 2) & 0x1)
        self._cmd_parse.set_config_full_range(51, (value >> 3) & 0x1)

    def set_tm_rst_in(self):
        self._cmd_parse.set_config_full_range(52, 0)
        self._cmd_parse.set_config_full_range(52, 1)
        self._cmd_parse.set_config_full_range(52, 0)

    def set_tm_start_in(self):
        self._cmd_parse.set_config_full_range(53, 0)
        self._cmd_parse.set_config_full_range(53, 1)
        self._cmd_parse.set_config_full_range(53, 0)

    def set_tm_speak_in(self, bit_val):
        self._cmd_parse.set_config_full_range(54, bit_val & 0x1)

    def dac_datain(self, data):
        self._cmd_parse.write_config_reg(0, data)

    def switch(self, value):
        self._cmd_parse.set_config_full_range(17, value & 0x1)
        self._cmd_parse.set_config_full_range(18, value>>1 & 0x1)
        self._cmd_parse.set_config_full_range(19, value>>2 & 0x1)

    def adc_datain(self, data):
        self._cmd_parse.write_config_reg(2, data)


    def set_pulse_da(self):
        self._cmd_parse.write_pulse_reg(1 << 4)

    def set_pulse_ad(self):
        self._cmd_parse.write_pulse_reg(1 << 5)

    def spi_pulse_reg(self):
        self._cmd_parse.write_pulse_reg(1 << 9)

    def set_time(self):
        """ Set time"""
        now = datetime.datetime.now()
        time_high = (now.year<<4) + now.month
        time_mid = (now.day<<8) + now.hour
        time_low = (now.minute<<8) + now.second
        time_us = now.microsecond

        self.set_time_high(time_high)
        self.set_time_mid(time_mid)
        self.set_time_low(time_low)
        self.set_time_usec(time_us)

    def clear_reset(self):
        self._cmd_parse.write_config_reg(31, 0)

    def config_restart(self):
        self.clear_reset()
        self._cmd_parse.write_config_reg(31, 4) # tx_fifo_reset, fifo_reset
        self.clear_reset()

    def SendFIFOResart2(self):
        self._cmd_parse.write_config_reg(29, 0)
        self._cmd_parse.write_config_reg(29, 4)
        self._cmd_parse.write_config_reg(29, 0)

    def SendFIFOResart(self):
        self._cmd_parse.write_config_reg(31, 0)
        self._cmd_parse.write_config_reg(31, 4)
        self._cmd_parse.write_config_reg(31, 0)



        