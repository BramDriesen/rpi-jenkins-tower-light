#!/usr/bin/env python

# Program flow
# 1. On startup: beep twice and blink leds one by one.
# 2. Check if connection possible with Jenkins. If not blink red.
# 3. Get the status and display the color.

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

# GPIO Setup
# 18 = Red
# 23 = Buzzer
# 24 = Yellow
# 27 = Green
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

# Always set all outputs to false
GPIO.output(18, False)
GPIO.output(23, False)
GPIO.output(24, False)
GPIO.output(27, False)


time.sleep(5)
GPIO.output(27, True)
time.sleep(5)
GPIO.output(27, False)
