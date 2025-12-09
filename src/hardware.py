# hardware.py
# Sets up all the hardware components for my ESP32-C3 game
# Includes: display, accelerometer, buzzer, NeoPixel, buttons, and rotary encoder

import board
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
import adafruit_mpu6050
import pwmio
import digitalio
from rotary_encoder import RotaryEncoder

# Release any displays from previous runs (MUST be first!)
displayio.release_displays()

# Initialize I2C bus for OLED and accelerometer
i2c = busio.I2C(board.SCL, board.SDA)

# OLED Display Setup (128x64 monochrome)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Accelerometer Setup (MPU-6050)
accelerometer = adafruit_mpu6050.MPU6050(i2c, address=0x68)

# Buzzer Setup (PWM output for different frequencies)
buzzer = pwmio.PWMOut(board.D6, frequency=440, duty_cycle=0, variable_frequency=True)

# NeoPixel LED Setup (single RGB LED)
pixel_pin = digitalio.DigitalInOut(board.D3)
pixel_pin.direction = digitalio.Direction.OUTPUT

# Rotary Encoder Setup (for menu navigation)
# D1 = CLK, D0 = DT, range 0-3 for 4 menu options
encoder = RotaryEncoder(board.D1, board.D0, min_val=0, max_val=3)

# Rotary Encoder Button (press to select)
encoder_btn = digitalio.DigitalInOut(board.D2)
encoder_btn.direction = digitalio.Direction.INPUT
encoder_btn.pull = digitalio.Pull.UP

# Game Control Buttons (A, C, D for lane switching and shooting)
button_a = digitalio.DigitalInOut(board.D8)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.DOWN

button_c = digitalio.DigitalInOut(board.D7)
button_c.direction = digitalio.Direction.INPUT
button_c.pull = digitalio.Pull.DOWN

button_d = digitalio.DigitalInOut(board.D10)
button_d.direction = digitalio.Direction.INPUT
button_d.pull = digitalio.Pull.DOWN

def set_neopixel(r, g, b):
    """Set NeoPixel color with brightness control"""
    import neopixel_write
    brightness = 0.3
    data = bytearray([int(g*brightness), int(r*brightness), int(b*brightness)])
    neopixel_write.neopixel_write(pixel_pin, data)

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB for rainbow effects
    h: hue (0-360 degrees)
    s: saturation (0-1)
    v: value/brightness (0-1)
    Returns: (r, g, b) tuple with values 0-255
    """
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)