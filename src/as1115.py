from adafruit_bus_device import i2c_device
from adafruit_register import i2c_bit
from adafruit_register import i2c_bits
# from typing import Union, List, Tuple, Optional
from busio import I2C
import time

AS1115_REGISTER = {
	'DECODE_MODE'		: 0x09,  # Enables decoding on selected digits
	'GLOBAL_INTENSITY'	: 0x0A,  # Sets the entire display intensity.
	'SCAN_LIMIT'		: 0x0B,  # Controls how many digits are to be displayed.
	'SHUTDOWN'			: 0x0C,  #
	'SELF_ADDRESSING'	: 0x2D,  # Uses 2 of the 16 keys to change the device's address.
	'FEATURE'			: 0x0E,  # Enables various features such as clock mode and blinking.
	'DISPLAY_TEST_MODE'	: 0x0F,  # Detects open or shorted LEDs.
	'DIG01_INTENSITY'	: 0x10,  # Sets the display intensity for digit 0 and 1.
	'DIG23_INTENSITY'	: 0x11,  # Sets the display intensity for digit 2 and 3.
	'DIG45_INTENSITY'	: 0x12,  # Sets the display intensity for digit 4 and 5.
	'DIG67_INTENSITY'	: 0x13,  # Sets the display intensity for digit 6 and 7.
	'KEY_A'				: 0x1C,  # Gets the result of the debounced keyscan for KEYA.
	'KEY_B'				: 0x1D	 # Gets the result of the debounced keyscan for KEYB.
}

LED_DIGIT = {
    'G': 0,
    'F': 1,
    'E': 2,
    'D': 3,
    'C': 4,
    'B': 5,
    'A': 6,
    'DP': 7
}

AS1115_SHUTDOWN_MODE = {
	'SHUTDOWN_MODE'	    : 0x00,  #  Shutdown and reset FEATURE register to default settings.
	'NORMAL_OPERATION'  : 0x01,  #  Resume operation and reset FEATURE register to default settings.
	'RESET_FEATURE'	    : 0x00,  #  FEATURE register is resetted to default settings.
	'PRESERVE_FEATURE'  : 0x80,  #  FEATURE register is unchanged.
}

AS1115_DECODE_SEL ={
	'CODE_B_DECODING'	: 0x00,
	'HEX_DECODING'	    : 0x01,
}

AS1115_DISPLAY_TEST_MODE = {
	'DISP_TEST':    0,  #  Optical display test.
	'LED_SHORT':    1,  #  Starts a test for shorted LEDs.
	'LED_OPEN':     2,  #  Starts a test for open LEDs.
	'LED_TEST':     3,  #  Indicates an ongoing open/short LED test.
	'LED_GLOBAL':   4,  #  Indicates that the last open/short LED test has detected an error.
	'RSET_OPEN':    5,  #  Checks if external resistor Rset is open.
	'RSET_SHORT':   6,  #  Checks if external resistor Rset is shorted.
}

# AS1115_DOT = 0x80
# LETTERS = {
#     'A': 0x77,
#     'B': 0x1F,
#     'C': 0x4E,
#     'D': 0x3D,
#     'E': 0x4F,
#     'F': 0x47,
#     'G': 0x5E,
#     'H': 0x37,
#     'I': 0x30,
#     'J': 0x3C,
#     'K': 0x2F,
#     'L': 0x0E,
#     'M': 0x54,
#     'N': 0x15,
#     'O': 0x1D,
#     'P': 0x67,
#     'Q': 0x73,
#     'R': 0x05,
#     'S': 0x5B,
#     'T': 0x0F,
#     'U': 0x3E,
#     'V': 0x1C,
#     'W': 0x2A,
#     'X': 0x49,
#     'Y': 0x3B,
#     'Z': 0x25,
# }

AS1115_DIGIT_REGISTER = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
AS1115_LED_DIAG_REG = [0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B]
NUMBERS = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47]

def nthdigit(value:int, idx:int):
    return value // 10**idx % 10

try:
    from typing import Optional, Type, NoReturn
    from circuitpython_typing.device_drivers import I2CDeviceDriver
except ImportError:
    pass


class RWBitsExplicit:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        obj: Optional[I2CDeviceDriver],
        num_bits: int,
        register_address: int,
        lowest_bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
        signed: bool = False,
        objtype: Optional[Type[I2CDeviceDriver]] = None,
    ) -> None:
        self.bit_mask = ((1 << num_bits) - 1) << lowest_bit
        # print("bitmask: ",hex(self.bit_mask))
        if self.bit_mask >= 1 << (register_width * 8):
            raise ValueError("Cannot have more bits than register size")
        self.lowest_bit = lowest_bit
        self.buffer = bytearray(1 + register_width)
        self.buffer[0] = register_address
        self.lsb_first = lsb_first
        self.sign_bit = (1 << (num_bits - 1)) if signed else 0
        self.obj = obj

    def get(self) -> int:
        with self.obj as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
        # read the number of bytes into a single variable
        reg = 0
        order = range(len(self.buffer) - 1, 0, -1)
        if not self.lsb_first:
            order = reversed(order)
        for i in order:
            reg = (reg << 8) | self.buffer[i]
        reg = (reg & self.bit_mask) >> self.lowest_bit
        # If the value is signed and negative, convert it
        if reg & self.sign_bit:
            reg -= 2 * self.sign_bit
        return reg

    def set(self, value: int) -> None:
        value <<= self.lowest_bit  # shift the value over to the right spot
        with self.obj as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
            reg = 0
            order = range(len(self.buffer) - 1, 0, -1)
            if not self.lsb_first:
                order = range(1, len(self.buffer))
            for i in order:
                reg = (reg << 8) | self.buffer[i]
            # print("old reg: ", hex(reg))
            reg &= ~self.bit_mask  # mask off the bits we're about to change
            reg |= value  # then or in our new value
            # print("new reg: ", hex(reg))
            for i in reversed(order):
                self.buffer[i] = reg & 0xFF
                reg >>= 8
            i2c.write(self.buffer)


class RWBitExplicit:
    """
    Single bit register that is readable and writeable.

    Values are `bool`

    :param int register_address: The register address to read the bit from
    :param int bit: The bit index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    :param bool lsb_first: Is the first byte we read from I2C the LSB? Defaults to true

    """

    def __init__(
        self,
        obj,
        register_address: int,
        bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
    ) -> None:
        self.obj = obj
        self.bit_mask = 1 << (bit % 8)  # the bitmask *within* the byte!
        self.buffer = bytearray(1 + register_width)
        self.buffer[0] = register_address
        if lsb_first:
            self.byte = bit // 8 + 1  # the byte number within the buffer
        else:
            self.byte = register_width - (bit // 8)  # the byte number within the buffer

    def get(self) -> bool:
        with self.obj as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
        return bool(self.buffer[self.byte] & self.bit_mask)

    def set(self, value: bool) -> None:
        with self.obj as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
            if value:
                self.buffer[self.byte] |= self.bit_mask
            else:
                self.buffer[self.byte] &= ~self.bit_mask
            i2c.write(self.buffer)


class ROBitExplicit(RWBitExplicit):
    def set(self, value: bool) -> NoReturn:
        raise AttributeError()



class AS1115_REG:
    # enables external clock
    feature_clock_active = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=0)
    # resets all control registers except for feature register
    feature_reset_all = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=1)
    # enable Code-B or HEX decoding for the selected digits
    feature_decode_sel = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=2)
    # enable blinking
    feature_blink_enable = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=4)
    # set blinking frequency
    feature_blink_freq_sel = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=5)
    # sync blinking with LD/CS pin
    feature_blink_freq_sel = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=6)
    # whether to start blinking w/ display turned on or off
    feature_blink_freq_sel = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=7)

    #  Optical display test.
    disp_test_visual = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=0)
    #  Starts a test for shorted LEDs.
    disp_test_led_short = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=1)
    #  Starts a test for open LEDs.
    disp_test_led_open = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=2)
    #  Indicates an ongoing open/short LED test.
    disp_test_led_test = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=3)
    #  Indicates that the last open/short LED test has detected an error.
    disp_test_led_global = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=4)
    #  Checks if external resistor Rset is open.
    disp_test_rset_open = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=5)
    #  Checks if external resistor Rset is shorted.
    disp_test_rset_short = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=6)

    global_intensity = i2c_bits.RWBits(num_bits=4, register_address=AS1115_REGISTER['GLOBAL_INTENSITY'], lowest_bit=0)
    scan_limit = i2c_bits.RWBits(num_bits=3, register_address=AS1115_REGISTER['SCAN_LIMIT'], lowest_bit=0)
    decode_mode = i2c_bits.RWBits(num_bits=4, register_address=AS1115_REGISTER['DECODE_MODE'], lowest_bit=0)
    self_addressing = i2c_bit.RWBit(register_address=AS1115_REGISTER['SELF_ADDRESSING'], bit=0)
    shutdown_mode_unchanged = i2c_bit.RWBit(register_address=AS1115_REGISTER['SHUTDOWN'], bit=7)  # no reset
    shutdown_mode_normal = i2c_bit.RWBit(register_address=AS1115_REGISTER['SHUTDOWN'], bit=0)  # normal operation

    def __init__(self,
                    i2c: I2C,
                    address: int = 0x00
                    ) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c, address)
        self.digit = [None] * 8
        self.keyA = [None] * 8
        self.keyB = [None] * 8
        self.led_diag = [[[None] for i in range(8)] for i in range(8)]

        for i in range(8):
            self.digit[i] = RWBitsExplicit(obj=self.i2c_device, num_bits=4, register_address=AS1115_DIGIT_REGISTER[i], lowest_bit=0)
            self.keyA[i] = ROBitExplicit(obj=self.i2c_device, register_address=AS1115_REGISTER['KEY_A'], bit=i)
            self.keyB[i] = ROBitExplicit(obj=self.i2c_device, register_address=AS1115_REGISTER['KEY_B'], bit=i)
            for j in range(8):
                self.led_diag[i][j] = ROBitExplicit(obj=self.i2c_device, register_address=AS1115_LED_DIAG_REG[i], bit=i)

class AS1115:
    """
    :param ~busio.I2C i2c: The I2C bus object
    :param int|list|tuple address: The I2C addess(es).
    :param bool auto_write: True if the display should immediately change when
        set. If False, `show` must be called explicitly.
    :param float brightness: 0.0 - 1.0 default brightness level.
    """
    def __init__(
        self,
        i2c: I2C,
        address: int = 0x00,
        brightness: float = 1.0,
        n_digits: int = 6,
    ) -> None:
        self.device = AS1115_REG(i2c, address)

        self._temp = bytearray(1)  # init bytearray
        self.n_digits = n_digits

        # --- start writing to chip --- #
        self.device.shutdown_mode_normal = 1
        self.device.shutdown_mode_unchanged = 0

        if address != 0x00:
            self.device.self_addressing = 1

        self._blink_rate = None
        self._brightness = None

        self.device.decode_mode = 0x0F  # this enables decoding on D0-D3
        self.device.feature_decode_sel = 0
        self.device.scan_limit = n_digits - 1

        self.blink_rate = 0
        self.brightness = brightness

    def clear(self) -> None:
        n = self.n_digits
        for i in range(n):
            self.device.digit[i].set(None)  # is this how you clear a register?

    def clear_idx(self, idx: int) -> None:
        self.device.digit[idx].set(None)

    def display_idx(self, idx: int, value: int) -> None:
        # display int 0-9 on an individual digit
        self.device.digit[idx].set(value)

    def display_int(self, value: int) -> None:
        # display int on entire display
        n = self.n_digits
        for i in range(n):
            self.device.digit[i].set(nthdigit(value, i))

    def visualTest(self) -> None:
        self.device.disp_test_visual = 1

    def ledShortTest(self) -> None:
        self.device.disp_test_led_short = 1
        self.device.disp_test_led_open = 0
        test_ongoing = True
        while test_ongoing:
            print('test ongoing...')
            test_ongoing = self.device.disp_test_led_test
            time.sleep(1)
        result = self.device.disp_test_led_global
        if result is True:
            print('ledTest has detected an error')
            for i in range(8):
                for j in range(8):
                    led_diag_i_j = self.device.led_diag[i][j].get()
                    print(i, j, led_diag_i_j)
        return result

    def ledOpenTest(self) -> None:
        self.device.disp_test_led_short = 0
        self.device.disp_test_led_open = 1
        test_ongoing = True
        while test_ongoing:
            print('test ongoing...')
            test_ongoing = self.device.disp_test_led_test
            time.sleep(1)
        result = self.device.disp_test_led_global
        if result is True:
            print('ledTest has detected an error')
            for i in range(8):
                for j in range(8):
                    led_diag_i_j = self.device.led_diag[i][j].get()
                    print(i, j, led_diag_i_j)
        return result

    def rsetTest(self) -> None:
        rset_open = self.device.disp_test_rset_open
        rset_short = self.device.disp_test_rset_short
        if rset_open is True:
            print('rsetTest has detected an open circuit')
        elif rset_short is True:
            print('rsetTest has detected a short circuit')
        return rset_open or rset_short

    @property
    def blink_rate(self) -> int:
        """The blink rate."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, rate: int) -> None:
        if rate not in [0, 1, 2]:
            raise ValueError("Blink rate must be an integer in the set: 0, 1, 2")
        self._blink_rate = rate
        if rate != 0:
            self.device.feature_blink_enable = 1
            self.device.feature_blink_freq_sel = rate - 1
        else:
            self.device.feature_blink_enable = 0

    @property
    def brightness(self) -> float:
        """The brightness. Range 0.0-1.0"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness: float) -> None:
        if not 0.0 <= brightness <= 1.0:
            raise ValueError(
                "Brightness must be a decimal number in the range: 0.0-1.0"
            )

        self._brightness = brightness
        duty_cycle = int(brightness * 15)
        self.device.global_intensity = duty_cycle


