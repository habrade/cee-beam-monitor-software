# from _typeshed import WriteableBuffer
import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class FreqCtr:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "freq_ctr_dev."
        log.debug("Frequency Counter Device")


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

    def enable_crap_mode(self, enable=False):
        reg_name = "en_crap_mode"
        self.w_reg(reg_name, enable, is_pulse=False, go_dispatch=True)

    def sel_chn(self, chn):
        chn &= 0xf
        reg_name =  "chan_sel"
        self.w_reg(reg_name, chn, is_pulse=False, go_dispatch=True)

    def get_sel_chn(self):
        reg_name = "chan_sel"
        return self.r_reg(reg_name)

    def is_valid(self):
        reg_name = "valid"
        return self.r_reg(reg_name)

    def get_freq(self):
        reg_name = "count"
        freq = self.r_reg(reg_name)
        reg_name = "valid"
        valid = self.r_reg(reg_name)
        if valid != 1:
            print("valid: {}".format(valid))
            return 0
        else:
            return freq

    def get_chn_freq(self, chn):
        self.sel_chn(chn)
        freq_counter = 0
        if self.is_valid():
            freq_counter = self.get_freq()
            log.debug("Frequency counter: {:d}".format(freq_counter))
        freq = 31.25E6 * freq_counter / (2**18 * 1E6)
        return freq
