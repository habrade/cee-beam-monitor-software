import logging
import coloredlogs
import struct

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG', logger=log)


## Command interpret
class CommandInterpret:
    ## constructor
    # @param[in] ss socket name
    def __init__(self, ss):
        self.ss = ss

    ## write config_reg
    # @param[in] Addr Address of the configuration register 0-31
    # @param[in] Data write into the configuration register 0-65535, [15:0]
    def write_config_reg(self, Addr, Data):
        data = 0x00200000 + (Addr << 16) + Data
        self.ss.sendall(struct.pack('I', data)[::-1])

    ## read config_reg
    # @param[in] Addr Address of the configuration register 0-31
    # return 32bit data
    def read_config_reg_range(self, Addr):
        log.debug("Read config Addr: {:}".format(Addr))
        data = 0x80200000 + (Addr << 16)
        self.ss.sendall(struct.pack('I', data)[::-1])
        return struct.unpack('I', self.ss.recv(4)[::-1])[0]

    def read_config_full_range(self, bit):
        if bit < 0 or bit > 511:
            log.error("set_config_bit_value: Invalid bit number")

        reg_val = self.read_config_reg_range(int(bit/16))
        shift = int(bit%16)
        bit_val = ((1 << shift) & reg_val) >> shift
        log.debug("Read config register bit {:}: {:}".format(bit, bit_val))
        return bit_val

    def set_config_reg_range(self, addr, bit_index, set_value):
        if bit_index < 0 or bit_index > 31:
            log.error("set_config_bit_value: Invalid bit number")
        else:
            config = self.read_config_reg_range(addr)
            config &= ~(1 << bit_index)
            if set_value:
                config |= 1 << bit_index
            self.write_config_reg(addr, config)

    def set_config_full_range(self, bit, set_value):
        log.debug("Set config register {:}: {:}".format(bit, set_value))
        
        if bit < 0 or bit > 511:
            log.error("set_config_bit_value: Invalid bit number")
        self.set_config_reg_range(int(bit / 16), bit % 16, set_value)

        if self.read_config_full_range(bit) != set_value:
            log.error("Setting config bit: Failed!")
            return False
        else:
            log.debug("Setting config bit: Success!")
            return True

    ## write pulse_reg
    # @param[in] Data write into the pulse register 0-65535
    def write_pulse_reg(self, Data):
        data = 0x000b0000 + Data
        self.ss.sendall(struct.pack('I', data)[::-1])

    ## read status_reg
    # @param[in] Addr Address of the configuration register 0-10
    def read_status_reg(self, Addr):
        data = 0x80000000 + (Addr << 16)
        self.ss.sendall(struct.pack('I', data)[::-1])
        return struct.unpack('I', self.ss.recv(4)[::-1])[0]

    ## write memeoy
    # @param[in] Addr write address of memeoy 0-65535
    # @param[in] Data write into memory data 0-65535
    def write_memory(self, Addr, Data):
        data = 0x00110000 + (0x0000ffff & Addr)  # memory address LSB register
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x00120000 + ((0xffff0000 & Addr) >> 16)  # memory address MSB register
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x00130000 + (0x0000ffff & Data)  # memory Data LSB register
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x00140000 + ((0xffff0000 & Data) >> 16)  # memory Data MSB register
        self.ss.sendall(struct.pack('I', data)[::-1])

    ## read memory
    # @param[in] Cnt read data counts 0-65535
    # @param[in] Addr start address of read memory 0-65535
    def read_memory(self, Cnt, Addr):
        data = 0x00100000 + Cnt  # write sMemioCnt
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x00110000 + (0x0000ffff & Addr)  # write memory address LSB register
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x00120000 + ((0xffff0000 & Addr) >> 16)  # write memory address MSB register
        self.ss.sendall(struct.pack('I', data)[::-1])
        data = 0x80140000  # read Cnt 32bit memory words
        self.ss.sendall(struct.pack('I', data)[::-1])
        for i in range(Cnt):
            print(hex(struct.unpack('I', self.ss.recv(4)[::-1])[0]))

    ## read_data_fifo
    # @param[in] Cnt read data counts 0-65535
    def read_data_fifo(self, Cnt):
        data = 0x00190000 + Cnt  # write sDataFifoHigh address = 25
        self.ss.sendall(struct.pack('I', data)[::-1])
        for i in range(Cnt):
            print(hex(struct.unpack('I', self.ss.recv(4)[::-1])[0]))
