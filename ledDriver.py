#!/usr/bin/python
"""
This software can be used to drive an analog RGB LED strip using a raspberry pi
and adafruit's 16-channel 12-bit PWM/Servo Driver - PCA9685:
http://www.adafruit.com/products/815
"""

import time, re, math
from random import randrange
from threading import Thread
import pwmDriver

DEFAULT_FADE = 200

class _LEDDriver(object):
    """
    Private class for use in this package. Defines procedures that should be
    implemented by any extensions to the package.
    """

    @staticmethod
    def setup_pwm(freq=200):
        """
        Sets up and returns a pulse-width modulation object for hardware
        control.

        Parameters
        freq (optional): frequency for the PWM object.
        """
        pwm = pwmDriver.PWM()
        pwm.setPWMFreq(freq)
        return pwm

    @staticmethod
    def convert_eight_to_twelve_bit(eight_bit):
        """
        Returns a number converted between 0 and 4095 to between 0 and
        255.

        Parameters:
        eight_bit: number to be converted

        The PWM chip has 10 bit resolution, so we need to convert regular 8 bit
        rgb codes
        >>> instance.convert_eight_to_ten_bit(0)
        0
        >>> instance.convert_eight_to_ten_bit(255)
        4080
        >>> instance.convert_eight_to_ten_bit(128)
        2048
        """
        return eight_bit << 4

    @staticmethod
    def randrange(start, stop, step = 1):
        """
        A slightly modified version of randrange which allows start==stop
        """
        if start == stop:
            return start
        else:
            return randrange(start, stop, step)

    def from_to(self, start, end, duration):
        """
        Fade from one value [start] to another [end] over a specified time
        [duration] in milliseconds.
        """
        pass

    def set(self, target):
        """
        Set value [target]
        """
        pass
    def to(self, target, fade=DEFAULT_FADE):
        """
        Fade to value [target] over a time [fade (optional)] in milliseconds.
        """
        pass

    def off(self):
        """
        Turns light off
        """

    def repeat(self, pin, function, duration=-1):
        """
        Cycle a pin over an arbitrary [function] for a time [duration] in
        milliseconds.
        Returns a thread object that must be started.

        Parameters
        pin: I2C microcontroller pin.
        function: Should return a value between 0 and 4095 and take in a time
                  in milliseconds
        duration: time in milliseconds

        >>> def sinefunc(time):
                return (math.sin(time/500 + 2000) * 2047) + 2047
        >>> r = rgb_driver.repeat(2, sinefunc, 5000)
        >>> r_r.start()
        The above cycles a sine function on pin 2 for 5 seconds.
        """
        def repeat_internal(pin, function, duration=5000):
            duration = float(duration)
            start_time = time.time()
            while True:
                if duration < 0:
                    elapsed = float(time.time() - start_time) * 1000
                    if elapsed >= duration:
                        break
                self.pwm.setPWM(pin, function(elapsed))
        t = Thread(target=repeat_internal, args=(pin, function, duration))
        return t

class SingleLEDDriver(_LEDDriver):
    def __init__(self, pin=3, pwm=None):
        self.pin = pin
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm
        self.current_brightness = self.pwm.readPWM(self.pin)

    def from_to(self, start, end, duration):
        duration = float(duration)
        diff = end - start

        start_time = time.time()
        while True:
            elapsed = float(time.time() - start_time) * 1000
            if elapsed >= duration:
                break
            l = start + diff * (elapsed / duration)
            self.set(l)

    def set(self, l):
        """The rgb values must be between 0 and 4095"""
        #print "R: %d, G: %d, B: %d" % (red_value, green_value, blue_value)
        self.pwm.setPWM(self.pin, l)
        self.current_brightness = l
    def to(self, l, fade=DEFAULT_FADE):
        self.from_to(self.current_brightness, l, fade)

    def set_rand(self, l_range=(0, 4095)):
        self.set(randrange(l_range[0], l_range[1]))
    def to_rand(self, l_range=(0, 4095), fade=DEFAULT_FADE):
        self.to(randrange(l_range[0], l_range[1]), fade)

    def off(self):
        self.to(0)
        self.set(0)

class RGBDriver(_LEDDriver):
    def __init__(self, red_pin = 0, green_pin = 1, blue_pin = 2, pwm = None):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm
        self.current_color = (
                self.pwm.readPWM(self.red_pin),
                self.pwm.readPWM(self.green_pin),
                self.pwm.readPWM(self.blue_pin)
            )

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lower()
        hex_match = re.match("^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$", hex_color)
        if hex_match:
            r = _LEDDriver.convert_eight_to_twelve_bit(int(hex_match.group(1), 16))
            g = _LEDDriver.convert_eight_to_twelve_bit(int(hex_match.group(2), 16))
            b = _LEDDriver.convert_eight_to_twelve_bit(int(hex_match.group(3), 16))
            return (r, g, b)
        elif hex_color == "rand" or hex_color == "random":
            r = randrange(0, 4080)
            g = randrange(0, 4080)
            b = randrange(0, 4080)
            return (r, g, b)
        else:
            print "Invalid hex color supplied: {:s}".format(hex_color)
            return None

    def update_color(self):
        self.current_color = (
                self.pwm.readPWM(self.red_pin),
                self.pwm.readPWM(self.green_pin),
                self.pwm.readPWM(self.blue_pin)
            )
        return self.current_color

    def set(self, rgb):
        """
        Input must be between 0 and 4095.
        """
        self.pwm.setPWM(self.red_pin, rgb[0])
        self.pwm.setPWM(self.green_pin, rgb[1])
        self.pwm.setPWM(self.blue_pin, rgb[2])
        self.current_color = rgb
    def to(self, rgb, fade=DEFAULT_FADE):
        """
        Input must be between 0 and 4095.
        """
        self.from_to(self.current_color, rgb, fade)

    def set_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095)):
        self.set((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])))
    def to_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095), fade=DEFAULT_FADE):
        self.to((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])), fade)

    def set_hex_color(self, color):
        self.set(RGBDriver.hex_to_rgb(color))
    def to_hex_color(self, color, fade=DEFAULT_FADE):
        self.to(RGBDriver.hex_to_rgb(color), fade)

    def from_to(self, start, end, duration):
        duration = float(duration)
        rgb = list(start)
        diff = [
                (end[0] - start[0]),
                (end[1] - start[1]),
                (end[2] - start[2])
            ]

        start_time = time.time()
        while True:
            elapsed = float(time.time() - start_time) * 1000
            if elapsed >= duration:
                break
            rgb[0] = start[0] + diff[0] * (elapsed / duration)
            rgb[1] = start[1] + diff[1] * (elapsed / duration)
            rgb[2] = start[2] + diff[2] * (elapsed / duration)
            self.set(map(int, rgb))

    def off(self):
        self.to((0, 0, 0))
        self.set((0, 0, 0))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='drive a rgb led strip through a pwm module')

    parser.add_argument('-c', '--color', type=str, help='Set the strip to this color.')
    parser.add_argument('-o', '--off', action='store_true', help="Turn off after other actions.")
    parser.add_argument('-t', '--test', action='store_true', help="test.")
    args = parser.parse_args()

    rgb_driver = RGBDriver()
    single_driver = SingleLEDDriver()
    try:
        if args.test:
            print "Starting everything off."
            single_driver.set(0)
            rgb_driver.set((0, 0, 0))
            def test_func_r(time):
                return (math.sin(time/500) * 2047) + 2047
            def test_func_g(time):
                return (math.sin(time/500 + 1000) * 2047) + 2047
            def test_func_b(time):
                return (math.sin(time/500 + 2000) * 2047) + 2047
            r_r = rgb_driver.repeat(0, test_func_r, 5000)
            g_r = rgb_driver.repeat(1, test_func_g, 5000)
            b_r = rgb_driver.repeat(2, test_func_b, 5000)
            print "Cycling some sine functions."
            r_r.start()
            g_r.start()
            b_r.start()
            r_r.join()
            g_r.join()
            b_r.join()
            print "Turning off, then fading to..."
            rgb_driver.to_off()
            print "  white"
            rgb_driver.to_hex_color("#ffffff")
            print "  red"
            rgb_driver.to_hex_color("#ff0000")
            print "  green"
            rgb_driver.to_hex_color("#00ff00")
            print "  blue"
            rgb_driver.to_hex_color("#0000ff")
            print "  off"
            rgb_driver.to_hex_color("#000000")
            rgb_driver.set_hex_color("#000000")
            print "Turning simple led strip on and off."
            single_driver.to(4095)
            single_driver.to_off()
        if args.color:
            rgb_driver.set_hex_color(args.color)
    finally:
        if args.off:
            rgb_driver.to_off()
            single_driver.to_off()
