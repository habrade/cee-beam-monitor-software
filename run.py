#!/usr/bin/env python3

import os
import sys
import time
import socket

import logging
import coloredlogs

from lib.command_interpret import CommandInterpret
from lib.topmetal_minus2_cntl import TopmetalMinus2Cntl

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG', logger=log)

def main():
    # host socket
    # @param[in] AF_UNIX:AF_Local, base on the local
    # @param[in] AF_NETLINK:linux operating system support socket
    # @param[in] AF_INET:base on IPV4 network TCP/UDP socket
    # @param[in] AF_INET6:base on IPV6 network TCP/UDP socket
    # establish socket
    hostname = "192.168.2.3"  # server ip address
    port = 1024  # server port number
    log.info("Target IP address: {:s} \t port: {:d}".format(hostname, port))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))  # connet socket

    cmd_parse = CommandInterpret(s)
    control_inst = TopmetalMinus2Cntl(cmd_parse)

    """ Set data type"""
    control_inst.set_data_type(4)

    """ Set time"""
    control_inst.set_time()

    """ Start working"""
    control_inst.reset()
    control_inst.set_tm_rst_in()
    control_inst.set_tm_start_in()
    control_inst.set_tm_speak_in(1)

    """ Config ADC """
    control_inst.resync()
    control_inst.set_chip_cnt(start_nr=0x00, end_nr=0x07) #config_reg[143:128],0--ADC #A,#B,#C,#D

    # test
    # cmd_parse.set_config_full_range(123, 1)

    # test_status = cmd_parse.read_config_reg_range(0)
    # print(test_status)

    
    # cmd_parse.read_data_fifo(1)

    s.close()

if __name__ == "__main__":
    main()