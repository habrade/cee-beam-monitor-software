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


class Ad9252Device:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "ad9252_dev."

        log.info("AD9252 device initial.")

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

    def is_busy(self):
        """
        Check whether ad9252 spi is busy.

        :return:
        """
        reg_name = "BUSY"
        busy = self.r_reg(reg_name)
        if busy == 1:
            return True
        else:
            return False

    def reset(self, go_dispatch=True):
        """
        Reset ad9252 control module.

        :param go_dispatch:
        :return:
        """
        reg_name = "RST"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

    def get_state(self):
        reg_name = "STATE"
        self.r_reg(reg_name)

    def start(self):
        reg_name = "START"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def restart(self):
        reg_name = "RESTART"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def pulse(self):
        reg_name = "PULSE"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def test_mode(self):
        reg_name = "TEST_MODE"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)
