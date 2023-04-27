import math
import time
from typing import Dict, Literal

import smbus2 as smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================
# https://www.waveshare.com/wiki/Robot_Arm_for_Pi


class Driver:
    bus: smbus.SMBus
    address: int
    debug: bool

    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09

    def __init__(self, address: int = 0x40, debug: bool = False) -> None:
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug:
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg: int, value: int) -> None:
        """Writes an 8-bit value to the specified register/address"""
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg: int) -> int:
        """Read an unsigned byte from the I2C device"""
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print(
                "I2C: Device 0x%02X returned 0x%02X from reg 0x%02X"
                % (self.address, result & 0xFF, reg)
            )
        return result

    def set_pwm_freq(self, freq: int) -> None:
        """Sets the PWM frequency"""
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if self.debug:
            print(f"Setting PWM frequency to {freq} Hz")
            print(f"Estimated pre-scale: {prescaleval}")
        prescale = math.floor(prescaleval + 0.5)
        if self.debug:
            print(f"Final pre-scale: {prescale}")
        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def set_pwm(self, channel: int, on: int, off: int) -> None:
        """Sets a single PWM channel"""
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if self.debug:
            print(f"channel: {channel}  LED_ON: {on} LED_OFF: {off}")

    def set_servo_pulse(self, channel: int, pulse: int) -> None:
        """Sets the Servo Pulse,The PWM frequency must be 50HZ"""
        # PWM frequency is 50HZ,the period is 20000us
        new_pulse = pulse * 4096 / 20000
        self.set_pwm(channel, 0, int(new_pulse))


ActionType = Literal["x", "y", "grab", "rotate"]
DEFAULT_POS: Dict[ActionType, int] = {"x": 0, "y": 0, "grab": 0, "rotate": 90}


class Controller:
    pwm: Driver
    debug: bool
    # Channel mapping depending on how cables are connected
    channels = {"y": 0, "x": 1, "grab": 2, "rotate": 3}

    def __init__(
        self,
        default: Dict[ActionType, int] = DEFAULT_POS,
        debug: bool = False,
        debug_driver: bool = False,
    ) -> None:
        self.pwm = Driver(0x40, debug=debug_driver)
        self.pwm.set_pwm_freq(50)
        self.debug = debug
        self.default_pos = default
        self.position = default
        self.reset()

    def _get_degree(self, deg: int) -> int:
        if deg > 180:
            return 180
        if deg < 0:
            return 0
        return deg

    def reset(self) -> None:
        """Reset robot arm to initial position"""
        self.set("y", self.default_pos["y"])
        self.set("x", self.default_pos["x"])
        self.set("rotate", self.default_pos["rotate"])
        self.set("grab", self.default_pos["grab"])

    def set(
        self, action: Literal["x", "y", "grab", "rotate"], deg: int, delay: float = 0.5
    ) -> None:
        deg = self._get_degree(deg)
        pulse = int(500 + (500 / 45 * deg))
        if self.debug:
            print(f"{action}: {deg}° (pulse: {pulse})")
        self.pwm.set_servo_pulse(self.channels[action], pulse)
        self.position[action] = deg
        time.sleep(delay)

    def move(
        self, action: Literal["x", "y", "grab", "rotate"], deg: int, delay: float = 0.5
    ) -> None:
        current = self.position[action]
        self.set(action, current + deg, delay)
