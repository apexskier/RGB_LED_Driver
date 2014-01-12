#!/usr/bin/env python
"""
This software can be used to drive an analog RGB LED strip using a raspberry pi
and adafruit's 16-channel 12-bit PWM/Servo Driver - PCA9685:
http://www.adafruit.com/products/815




Copyright (C) 2013 Jeremy Smith

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import Adafruit_PWM_Servo_Driver
import time, re
from random import randrange


class RGB_Driver(object):
    def __init__(self, pwm = None, red_pin = 0, green_pin = 1, blue_pin = 2):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        if pwm is None:
            self.pwm = self.setup_pwm()
        else:
            self.pwm = pwm

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


    def set_rgb(self, rgb):
        """The rgb values must be between 0 and 4095"""
        #print "R: %d, G: %d, B: %d" % (red_value, green_value, blue_value)
        self.pwm.setPWM(self.red_pin, 0, rgb[0])
        self.pwm.setPWM(self.green_pin, 0, rgb[1])
        self.pwm.setPWM(self.blue_pin, 0, rgb[2])

    def set_rand(self):
        self.set_rgb((randrange(0, 4080), randrange(0, 4080), randrange(0, 4080)))

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

    def set_hex_color(self, color):
        self.set_rgb(self.hex_to_rgb(color))

    def from_to(self, rgb_s, rgb_e, duration, freq = 120):
        duration = float(duration)
        rgb = list(rgb_s)
        rgb_diff = [
                (rgb_e[0] - rgb_s[0]),
                (rgb_e[1] - rgb_s[1]),
                (rgb_e[2] - rgb_s[2])
            ]
        print duration
        print rgb_diff

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
            print elapsed / duration, rgb


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='drive a rgb led strip through a pwm module')

    parser.add_argument('-r', '--red', nargs=2, type=int, default=[0, 0], help="The beginning and end values for red in fade mode.  Max and min values for red in random mode.")
    parser.add_argument('-g', '--green', nargs=2, type=int, default=[0, 0], help="The beginning and end values for green in fade mode.  Max and min values for green in random mode..")
    parser.add_argument('-b', '--blue', nargs=2, type=int, default=[0, 0], help="The beginning and end values for blue in fade mode.  Max and min values for blue in random mode..")
    parser.add_argument('-s', '--steps', type=int, default=100, help="Number of steps in the fade.  Not used with --random")
    parser.add_argument('-d', '--delay', type=float, default=0.005, help="Number of seconds between the steps or random changes, can be a float")
    parser.add_argument('-o', '--off', action='store_true', help="Turn off after other actions.")
    parser.add_argument('--repeat', type=int, default=1, help="Repeat the fade this many times.  Unused with --random.")
    parser.add_argument('--reverse', action="store_true", help="Reverse the fade, to return back to the initial state.  Unused with --random.")
    parser.add_argument('--random', action="store_true", help="Move around randomly between the max and min values specified with --red --green and --blue.  Use with --time and --max-random-walk")
    parser.add_argument('--time', type=int, default=10, help="Used with --random.  Move randomly for this many seconds")
    parser.add_argument('--max-random-walk', type=int, default=10, help="The max that each channel will be allowed to change between steps in random mode.")
    parser.add_argument('-c', '--color', type=str, help='Set the strip to this color.')
    args = parser.parse_args()

    driver = RGB_Driver()
    try:
        """
        if args.color:
            driver.set_hex_color(args.color);
        elif args.random is False:
            for repeat in xrange(0, args.repeat):
                print "Repetition %d" % repeat
        else:
            # We need to sort the values to make sure randrange works correctly
            args.red.sort()
            args.green.sort()
            args.blue.sort()
            driver.random_walk(args.red[0], args.green[0], args.blue[0], args.red[1], args.green[1], args.blue[1], args.time, args.delay, args.max_random_walk)
        """
        driver.from_to(driver.hex_to_rgb("#6fff00"), driver.hex_to_rgb("#ae00ff"), 5000)
    finally:
        if args.off:
            driver.set_rgb((0, 0, 0))
