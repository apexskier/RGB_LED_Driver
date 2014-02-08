#!/usr/bin/python
"""
This software can be used to drive an analog RGB LED strip using a raspberry pi
and adafruit's 16-channel 12-bit PWM/Servo Driver - PCA9685:
http://www.adafruit.com/products/815
"""

import time, re, math
from random import randrange
from threading import Thread
import PWMDriver

DEFAULT_FADE = 200

class LEDDriver(object):
    @staticmethod
    def setup_pwm(freq=200):
        pwm = PWMDriver.PWM()
        pwm.setPWMFreq(freq)
        return pwm

    @staticmethod
    def convert_eight_to_twelve_bit(eight_bit):
        """The PWM chip has 10 bit resolution, so we need to
            convert regular 8 bit rgb codes
        >>> RGB_Driver.convert_eight_to_ten_bit(0)
        0
        >>> RGB_Driver.convert_eight_to_ten_bit(255)
        4080
        >>> RGB_Driver.convert_eight_to_ten_bit(128)
        2048
        """
        return eight_bit << 4

    @staticmethod
    def randrange(start, stop, step = 1):
        """A slightly modified version of randrange which allows start==stop"""
        if start == stop:
            return start
        else:
            return randrange(start, stop, step)

    def from_to(self, start, end, duration, freq = 120):
        pass

    def set_(self, target):
        # change to target
        # update stored value
        pass
    def to_(self, target):
        pass

    def repeat(self, pin, function, duration):
        """
        function should return a value between 0 and 4095 and take in a time in
        milliseconds
        """
        def repeat_internal(pin, function, duration=5000):
            duration = float(duration)
            start_time = time.time()
            while True:
                elapsed = float(time.time() - start_time) * 1000
                if elapsed >= duration:
                    break
                self.pwm.setPWM(pin, function(elapsed))
        t = Thread(target=repeat_internal, args=(pin, function, duration))
        return t

class SingleLEDDriver(LEDDriver):
    def __init__(self, pin = 3, pwm = None):
        self.pin = pin
        self.current_brightness = 0
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm

    def from_to(self, start, end, duration, freq = 120):
        duration = float(duration)
        diff = end - start

        start_time = time.time()
        while True:
            elapsed = float(time.time() - start_time) * 1000
            if elapsed >= duration:
                break
            l = start + diff * (elapsed / duration)
            #time.sleep(float(freq) / 1000)
            self.set_(l)

    def set_(self, l):
        """The rgb values must be between 0 and 4095"""
        #print "R: %d, G: %d, B: %d" % (red_value, green_value, blue_value)
        self.pwm.setPWM(self.pin, l)
        self.current_brightness = l
    def to_(self, l, fade=DEFAULT_FADE):
        self.from_to(self.current_brightness, l, fade)

    def set_rand(self, l_range=(0, 4095)):
        self.set_(randrange(l_range[0], l_range[1]))
    def to_rand(self, l_range=(0, 4095), fade=DEFAULT_FADE):
        self.to_(randrange(l_range[0], l_range[1]), fade)

    def to_off(self):
        self.to_(0)
        self.set_(0)

class RGBDriver(LEDDriver):
    def __init__(self, red_pin = 0, green_pin = 1, blue_pin = 2, pwm = None):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.current_color = (0, 0, 0)
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm
        #TODO Set self.current color after setting up pwm

    #TODO: convert to static method?
    def hex_to_(self, hex_color):
        hex_color = hex_color.lower()
        hex_match = re.match("^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$", hex_color)
        if hex_match:
            r = self.convert_eight_to_twelve_bit(int(hex_match.group(1), 16))
            g = self.convert_eight_to_twelve_bit(int(hex_match.group(2), 16))
            b = self.convert_eight_to_twelve_bit(int(hex_match.group(3), 16))
            return (r, g, b)
        elif hex_color == "rand" or hex_color == "random":
            r = randrange(0, 4080)
            g = randrange(0, 4080)
            b = randrange(0, 4080)
            return (r, g, b)
        else:
            print "Invalid hex color supplied: {:s}".format(hex_color)
            return None

    def set_(self, rgb):
        """The rgb values must be between 0 and 4095"""
        self.pwm.setPWM(self.red_pin, rgb[0])
        self.pwm.setPWM(self.green_pin, rgb[1])
        self.pwm.setPWM(self.blue_pin, rgb[2])
        self.current_color = rgb
    def to_(self, rgb, fade=DEFAULT_FADE):
        self.from_to(self.current_color, rgb, fade)

    def set_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095)):
        self.set_((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])))
    def to_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095), fade=DEFAULT_FADE):
        self.to_((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])), fade)

    def set_hex_color(self, color):
        self.set_(self.hex_to_(color))
    def to_hex_color(self, color, fade=DEFAULT_FADE):
        self.to_(self.hex_to_(color), fade)

    def from_to(self, start, end, duration, freq = 120):
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
            self.set_(map(int, rgb))

    def to_off(self):
        self.to_((0, 0, 0))
        self.set_((0, 0, 0))

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
            single_driver.set_(0)
            rgb_driver.set_((0, 0, 0))
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
            single_driver.to_(4095)
            single_driver.to_off()
        if args.color:
            rgb_driver.set_hex_color(args.color)
        # rgb_driver.from_to(rgb_driver.hex_to_("#6fff00"), rgb_driver.hex_to_("#ae00ff"), 5000)
    finally:
        if args.off:
            rgb_driver.to_off()
            single_driver.to_off()
