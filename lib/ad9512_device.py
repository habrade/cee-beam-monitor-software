import logging
import time
from os import altsep

from lib.spi_device import SpiDevice

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Ad9512Device:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "ad9512_dev."

        self.ad9512_function_go()

        self.spi_data = []
        self.spi_dev = SpiDevice(self._ipbus_link)

        # self.reset_spi()
        self.set_spi()

        log.info("AD9512 device initial.")

    def w_reg(self, reg_name, reg_val, is_pulse, go_dispatch):
        """
        The register write function for Twominus device.

        :param reg_name:
        :param reg_val:
        :param is_pulse:
        :param go_dispatch:
        :return:
        """
        self._ipbus_link.w_reg(self.reg_name_base, reg_name,
                               reg_val, is_pulse, go_dispatch)

    def r_reg(self, reg_name):
        """
        The register read function for Twominus device.

        :param reg_name:
        :return:
        """
        return self._ipbus_link.r_reg(self.reg_name_base, reg_name)

    def is_busy_spi(self):
        """
        Check whether spi us busy.

        :return:
        """
        reg_name = "BUSY"
        spi_busy = self.r_reg(reg_name)
        if spi_busy == 1:
            return True
        else:
            return False

    def reset_spi(self, go_dispatch=True):
        """
        Reset SPI.

        :param go_dispatch:
        :return:
        """
        reg_name = "RST"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

    # def set_spi_data(self, d0):
    #     # self.update_spi_reg()
    #     self.spi_data = [0, 0, 0, 0, 0, 0, 0, 0]
    #     self.spi_data[0] = d0
        

    def set_spi(self, data_len=24, ie=False, ass=True, lsb=False, rx_neg=False, tx_neg=True, div=4, ss=0x00):
        """
        SPI configuration.

        @param data_len: Number of characters to be sent, default=200.
        @param ie: The interrupt output is set active after a transfer is finished.
        @param ass: Set how ss signal is generated.
        @param lsb: LSB or MSB send first.
        @param rx_neg: Receive data at which edge.
        @param tx_neg: Send data at which edge.
        @param div: Clock division.
        @param ss: Write to ss register.
        @return:
        """
        self.spi_dev.set_data_len(data_len)
        self.spi_dev.set_ie(ie)
        self.spi_dev.set_ass(ass)
        self.spi_dev.set_lsb(lsb)
        self.spi_dev.set_rx_neg(rx_neg)
        self.spi_dev.set_tx_neg(tx_neg)
        self.spi_dev.w_div(div)
        self.spi_dev.r_div()
        self.spi_dev.w_ctrl()
        self.spi_dev.w_ss(ss)

    def start_spi_config(self):
        """
        Config SPI.

        :return:
        """
        if self.is_busy_spi():
            log.error("SPI is busy now! Stop!")
        else:
            # spi_data = self.set_spi_data()
            self.spi_dev.w_data_regs(spi_data=self.spi_data)
            self.spi_dev.w_ctrl()
            self.spi_dev.start()

    
    def set_function(self, func):
        if self.is_busy():
            return False
        else:
            self.w_data(func)
            self.we()
            return True

    def ad9512_function_go(self):
        reg_name = "FUNCTION"
        self.w_reg(reg_name, 1, is_pulse=False, go_dispatch=False)
        self.w_reg(reg_name, 0, is_pulse=False, go_dispatch=False)
        self.w_reg(reg_name, 1, is_pulse=False, go_dispatch=True)
    
    def ad9512_read_function(self):
        reg_name = "FUNCTION"
        function = self.r_reg(reg_name)
        print("function: {}".format(function))

    
    def set_trans_header(self, rw, w1, w0, addr):
        trans_data = (rw << 15) + (w1 << 14) + (w0 << 13) + addr
        return trans_data

    def set_trans_data(self, rw, w1, w0, addr, data):
        nr_bytes = 0
        w_config = (w1, w0)
        if w_config == (0 , 0):
            nr_bytes = 1
        elif w_config == (0, 1):
            nr_bytes = 2
        elif w_config == (1, 0):
            nr_bytes = 3
        else:
            nr_bytes = 4
        
        log.debug("Number of trans data: {:} bytes".format(nr_bytes))
        trans_data = ((self.set_trans_header(rw, w1, w0, addr) << (8 * nr_bytes)) + data)
        self.spi_data = [trans_data, 0,0,0,0,0,0,0]
        return trans_data 
            
    def set_ad9512(self):
        rw = 0
        w1 = 0
        w0 = 0
        time.sleep(.1)
        self.set_trans_data(rw, w1, w0, addr=0x00, data=0x10)
        self.start_spi_config()

        time.sleep(.1)
        self.set_trans_data(rw, w1, w0, addr=0x4a, data=0x11)
        time.sleep(.1)
        self.start_spi_config()
        self.set_trans_data(rw, w1, w0, addr=0x4c, data=0x11)
        time.sleep(.1)
        self.start_spi_config()
        self.set_trans_data(rw, w1, w0, addr=0x4e, data=0x11)
        time.sleep(.1)
        self.start_spi_config()
        time.sleep(.1)
        self.set_trans_data(rw, w1, w0, addr=0x50, data=0x11)
        self.start_spi_config()

        self.set_trans_data(rw, w1, w0, addr=0x5a, data=0x01)
        time.sleep(.1)
        self.start_spi_config()


    def get_reg_onchip(self, addr):
        rw = 1
        w0 = 0
        w1 = 0
        self.set_trans_data(rw, w1, w0, addr, data=0x00)
        self.start_spi_config()
        reg_name = "d0"
        reg_val = self.spi_dev.r_reg(reg_name)
        log.debug("{:s}: {:#x}".format(reg_name, reg_val))
        return reg_val
    
        