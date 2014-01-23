#!/usr/bin/python
"""
This software can be used to drive an analog RGB LED strip using a raspberry pi
and adafruit's 16-channel 12-bit PWM/Servo Driver - PCA9685:
http://www.adafruit.com/products/815
"""

import Adafruit_PWM_Servo_Driver
import time, re
from random import randrange

DEFAULT_FADE = 200

class LEDDriver(object):
    @staticmethod
    def setup_pwm(freq = 200):
        pwm = Adafruit_PWM_Servo_Driver.PWM()
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
    def sanitize_int(x):
        if x < 0:
            return 0
        elif x > 4095:
            return 4095
        else:
            return int(x)

    @staticmethod
    def randrange(start, stop, step = 1):
        """A slightly modified version of randrange which allows start==stop"""
        if start == stop:
            return start
        else:
            return randrange(start, stop, step)

class SingleLEDDriver(LEDDriver):
    def __init__(self, pin = 3, pwm = None):
        self.pin = pin
        self.current_brightness = 0
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm

    def from_to(self, l_s, l_e, duration, freq = 120):
        duration = float(duration)
        l_diff = l_e - l_s

        start = time.time()
        while True:
            elapsed = float(time.time() - start) * 1000
            if elapsed >= duration:
                break
            l = l_s + l_diff * (elapsed / duration)
            #time.sleep(float(freq) / 1000)
            self.set_l(l)

    def set_l(self, l):
        """The rgb values must be between 0 and 4095"""
        #print "R: %d, G: %d, B: %d" % (red_value, green_value, blue_value)
        self.pwm.setPWM(self.pin, 0, self.sanitize_int(l))
        self.current_brightness = l
    def to_l(self, l, fade=DEFAULT_FADE):
        self.from_to(self.current_brightness, l, fade)

    def set_rand(self, l_range=(0, 4095)):
        self.set_l(randrange(l_range[0], l_range[1]))
    def to_rand(self, l_range=(0, 4095), fade=DEFAULT_FADE):
        self.to_l(randrange(l_range[0], l_range[1]), fade)

    def to_off(self):
        self.to_l(0)
        self.set_l(0)

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
    def hex_to_rgb(self, hex_color):
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

    def set_rgb(self, rgb):
        """The rgb values must be between 0 and 4095"""
        self.pwm.setPWM(self.red_pin, 0, self.sanitize_int(rgb[0]))
        self.pwm.setPWM(self.green_pin, 0, self.sanitize_int(rgb[1]))
        self.pwm.setPWM(self.blue_pin, 0, self.sanitize_int(rgb[2]))
        self.current_color = rgb
    def to_rgb(self, rgb, fade=DEFAULT_FADE):
        self.from_to(self.current_color, rgb, fade)

    def set_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095)):
        self.set_rgb((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])))
    def to_rand(self, r_range=(0, 4095), g_range=(0, 4095), b_range=(0, 4095), fade=DEFAULT_FADE):
        self.to_rgb((randrange(r_range[0], r_range[1]), randrange(g_range[0], g_range[1]), randrange(b_range[0], b_range[1])), fade)

    def set_hex_color(self, color):
        self.set_rgb(self.hex_to_rgb(color))
    def to_hex_color(self, color, fade=DEFAULT_FADE):
        self.to_rgb(self.hex_to_rgb(color), fade)

    def from_to(self, rgb_s, rgb_e, duration, freq = 120):
        duration = float(duration)
        rgb = list(rgb_s)
        rgb_diff = [
                (rgb_e[0] - rgb_s[0]),
                (rgb_e[1] - rgb_s[1]),
                (rgb_e[2] - rgb_s[2])
            ]

        start = time.time()
        while True:
            elapsed = float(time.time() - start) * 1000
            if elapsed >= duration:
                break
            rgb[0] = rgb_s[0] + rgb_diff[0] * (elapsed / duration)
            rgb[1] = rgb_s[1] + rgb_diff[1] * (elapsed / duration)
            rgb[2] = rgb_s[2] + rgb_diff[2] * (elapsed / duration)
            #time.sleep(float(freq) / 1000)
            self.set_rgb(map(int, rgb))

    def to_off(self):
        self.to_rgb((0, 0, 0))
        self.set_rgb((0, 0, 0))

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
            rgb_driver.to_hex_color("#ffffff")
            rgb_driver.to_hex_color("#ff0000")
            rgb_driver.to_hex_color("#00ff00")
            rgb_driver.to_hex_color("#0000ff")
            rgb_driver.to_hex_color("#000000")
            rgb_driver.set_hex_color("#000000")
            single_driver.to_l(4095);
            single_driver.to_off();
        if args.color:
            rgb_driver.set_hex_color(args.color)
        # rgb_driver.from_to(rgb_driver.hex_to_rgb("#6fff00"), rgb_driver.hex_to_rgb("#ae00ff"), 5000)
    finally:
        if args.off:
            rgb_driver.to_off()
            single_driver.to_off();
