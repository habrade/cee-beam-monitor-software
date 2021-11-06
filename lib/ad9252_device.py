import logging
import time

from lib.spi_device import SpiDevice

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Ad9252Device:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "ad9252_dev."

        self.spi_data = []
        self.spi_chanel = 1
        self.spi_dev = SpiDevice(self._ipbus_link, self.spi_chanel)

        self.set_spi()

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

    # def reset_spi(self, go_dispatch=True):
    #     """
    #     Reset SPI.
    #
    #     :param go_dispatch:
    #     :return:
    #     """
    #     reg_name = "RST"
    #     self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

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
        self.spi_dev.w_data_regs(spi_data=self.spi_data)
        self.spi_dev.w_ctrl()
        self.spi_dev.start()

    def set_trans_header(self, rw, w1, w0, addr):
        trans_data = (rw << 15) + (w1 << 14) + (w0 << 13) + addr
        return trans_data

    def set_trans_data(self, rw, w1, w0, addr, data):
        nr_bytes = 0
        w_config = (w1, w0)
        if w_config == (0, 0):
            nr_bytes = 1
        elif w_config == (0, 1):
            nr_bytes = 2
        elif w_config == (1, 0):
            nr_bytes = 3
        else:
            nr_bytes = 4

        log.debug("Number of trans data: {:} bytes".format(nr_bytes))
        trans_data = ((self.set_trans_header(rw, w1, w0, addr) << (8 * nr_bytes)) + data)
        self.spi_data = [trans_data, 0, 0, 0, 0, 0, 0, 0]
        return trans_data

    def spi_write(self, addr, data):
        rw = 0
        w1 = 0
        w0 = 0
        self.set_trans_data(rw, w1, w0, addr, data)
        self.start_spi_config()

    def chip_port_config(self, val=0x18):
        """The nibbles should be mirrored so that LSB- or MSB-first mode is set correctly regardless of shift mode."""
        self.spi_write(0x00, val)

    def device_index_2(self, val=0x0f):
        """Bits are set to determine which on-chip device receives the next write command."""
        self.spi_write(0x04, val)

    def device_index_1(self, val=0x0f):
        """Bits are set to determine which on-chip device receives the next write command."""
        self.spi_write(0x05, val)

    def device_update(self, val=0x01):
        """Synchronously transfers data from the master shift register to the slave."""
        self.spi_write(0xff, 0x00)
        self.spi_write(0xff, 0x01)
        self.spi_write(0xff, 0x00)

    def set_function_modes(self, val=0x00):
        """Determines various generic modes of chip operation."""
        log.debug("Set mode to: {:#x}".format(val))
        self.spi_write(0x08, val)
        self.device_update()

    def set_function_clock(self, val=0x01):
        """Turns the internal duty cycle stabilizer on and off."""
        self.spi_write(0x09, val)
        self.device_update()

    def set_function_test_io(self, val=0x00):
        """When this register is set, the test data is placed on the output pins in place of normal data."""
        log.debug("set test_io to: {:}".format(val))
        self.spi_write(0x0D, val)
        self.device_update()

    def set_function_output_mode(self, val=0x00):
        """Configures the outputs and the format of the data."""
        self.spi_write(0x14, val)
        self.device_update()

    def set_function_output_adjust(self, val=0x00):
        """Determines LVDS or other output properties. Primarily functions to set the LVDS span
         and common-mode levels in place of an external resistor."""
        self.spi_write(0x15, val)
        self.device_update()

    def set_function_output_phase(self, val=0x03):
        """On devices that utilize global clock divide, this register determines which phase of
        the divider output is used to supply the output clock. Internal latching is unaffected."""
        self.spi_write(0x16, val)
        self.device_update()

    def set_function_user_patt1_lsb(self, val=0x00):
        """User-defined pattern, 1 LSB"""
        self.spi_write(0x19, val)
        self.device_update()

    def set_function_user_patt1_msb(self, val=0x00):
        """User-defined pattern, 1 MSB"""
        self.spi_write(0x1A, val)
        self.device_update()

    def set_function_user_patt2_lsb(self, val=0x00):
        """User-defined pattern, 2 LSB"""
        self.spi_write(0x1B, val)
        self.device_update()

    def set_function_user_patt2_msb(self, val=0x00):
        """User-defined pattern, 2 MSB"""
        self.spi_write(0x1C, val)
        self.device_update()

    def set_function_serial_control(self, val=0x00):
        """Serial stream control. Default causes MSB first and the native bit stream (global)."""
        self.spi_write(0x21, val)
        self.device_update()

    def set_function_serial_ch_stat(self, val=0x00):
        """Used to power down individual sections of a converter (local)."""
        self.spi_write(0x22, val)
        self.device_update()

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

    def go_test_mode(self):
        log.debug("Setting ad9252 to test mode")
        self.set_function_test_io(0x0C)

    def go_working(self):
        log.debug("Setting ad9252 to working mode")
        self.set_function_test_io(0x00)

    def soft_reset_chip(self):
        log.debug("Soft reset AD9252")
        self.chip_port_config(0x3c)
