# RGB LED Driver

This software can be used to drive an analog RGB LED strip using a raspberry pi
and adafruit's 16-channel 12-bit PWM/Servo Driver - PCA9685:
http://www.adafruit.com/products/815


## The Circuit

Here's the basic idea:

  - Hook up the pi to the PCA9685 breakout board using the I2C connections.
  - Connect the pi's 3.3V output to VCC on the PCA9685 breakout board. Leave V+
    floating.
  - Follow this tutorial for the RGB LED strips:
    http://learn.adafruit.com/rgb-led-strips/usage
      - I used N-channel MOSFETs - three of them, one for each channel
      - Connect the +12V from the LED strip to an external power supply (do NOT
        use your pi for this!)
      - Connect the ground side of the power supply to the pi ground
      - Instead of using the PWM outputs from the arduino, we'll use the PWM
        outputs from the PCA9685.
      - Connect up the PWM output 0 to the MOSFET with the red wire from the
        LED strip.  Output 1 goes to green, output 2 goes to blue.

![Breadboard image](https://raw2.github.com/apexskier/rgbLED/master/LED_Strip_bb.png)


## Dependencies

Adafruit's [PWM Servo
Driver](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_PWM_Servo_Driver/Adafruit_PWM_Servo_Driver.py)
and
[Adafruit_I2C](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py).
Either include these two files somewhere in your PYTHONPATH or in this git repo's
directory.


## Usage

This program is designed to be included as a python module, but also has some
command line options. It, or any python code importing it, must be run as root
(sudo), because of the I2C interface.

### CLI Options

- `-c [hex color]` - sets the led strip to the color specified.
- `-o` - turn the led strip off after other actions

### As a module

```
from rgbDriver import RGBDriver
rgb_driver = RGBDriver()
```

Methods in the module use tuples to describe rgb colors: `(red_value,
green_value, blue_value)`.

Each color value can range between 0 and 4095, due to the PWM driver's 12 bit
resolution. The `convert_eight_to_twelve_bit()` method can convert a standard 0
to 255 color value to this scale.

To describe a color you can use the string representation of a hex color code
and the method `hex_to_rgb()` to convert it or `set_hex_color()` and
`to_hex_color()` to use it directly.

Two types of color setting methods exist. `to_...` will transition a color
change over a set time. The last argument of any `to_...` method is that delay
in milliseconds. `set_...` will set a color immediately.


## Examples


## What's Next?

The PWM breakout board has 16 outputs, so, with the right power supply, we
could drive up to 5 strips at the same time.

I plan on updating the code to allow for driving multiple strips.
