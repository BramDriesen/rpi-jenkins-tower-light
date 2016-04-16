#!/usr/bin/env python

# Program flow
# 1. On startup: beep and blink leds one by one.
# 2. Check if connection possible with Jenkins. If not blink red. (TODO)
# 3. Get the status and display the color.
# 4. Check with threads if building or not / update status lught

import RPi.GPIO as GPIO
import time
import threading
import jenkinsapi
from jenkinsapi.jenkins import Jenkins

# Set the GPIO mode.
GPIO.setmode(GPIO.BCM)

# Get a gpio code for an string
# Set the correct GPIO's for your situation
def getcode(value):
    value = value.lower()
    return {
        'red': 18,
        'buzzer': 23,
        'yellow': 24,
        'green': 27,
    }.get(value, 24)

# GPIO Setup
GPIO.setup(getcode('red'), GPIO.OUT)
GPIO.setup(getcode('buzzer'), GPIO.OUT)
GPIO.setup(getcode('yellow'), GPIO.OUT)
GPIO.setup(getcode('green'), GPIO.OUT)

# Global variables
building = False
error = False

# ---------------------------------------------------- #
# --         All globally used functions            -- #
# ---------------------------------------------------- #

# Function to toggle everything off
def alloff():
    GPIO.output(getcode('red'), False)
    GPIO.output(getcode('buzzer'), False)
    GPIO.output(getcode('yellow'), False)
    GPIO.output(getcode('green'), False)
    return

# Toggle function with parameter output and duration
def toggle(gpio, duration):
    GPIO.output(gpio, True)
    time.sleep(duration)
    GPIO.output(gpio, False)
    time.sleep(duration)
    return

# Set according to status
def setstatus(build):
    if build != "":
        status = build.get_status()
        alloff()
        if status == "SUCCESS":
            GPIO.output(getcode('green'), True)

        if status == "UNSTABLE":
            GPIO.output(getcode('yellow'), True)

        if status == "FAILURE":
            GPIO.output(getcode('red'), True)
    return

# ---------------------------------------------------- #

# Turn all off if any GPIO is still on
alloff()

# Toggle everything once
toggle(getcode('buzzer'), .1)
toggle(getcode('red'), .2)
toggle(getcode('yellow'), .2)
toggle(getcode('green'), .2)

# Configure the Jenkins parameter and get the job
J = Jenkins('http://jenkinscap.cloudapp.net:8080', username="rpi", password="")
try:
    job = J.get_job("UTC Behat")
    # Get the status of the latest build before starting the threads
    latestbuild = job.get_last_build()
    setstatus(latestbuild)
except IOError:
    global error
    error = True
    print "IOERROR"
except ValueError:
    global error
    error = True
    print "Value Error"
except:
    global error
    error = True
    print "Could not connect to Jenkins, please check your internet connection and settings"
else:
    global error
    print "No error?"
    error = False

# Thread the blinking function
# Every 10s blink for 3s when we are building
def blinking():
    threading.Timer(10.0, blinking).start()
    # Only blink when we are actually building
    if building == True or error == True:
        # If error, blink red.
        if error == True:
            color = "red"
        else:
            color = "yellow"

        alloff()
        pin = getcode(color)

        GPIO.output(pin, True)
        time.sleep(3)
        GPIO.output(pin, False)

# Check every 10s if we are building, if not or done get latest status     
def buildrunning():
    threading.Timer(10.0, buildrunning).start()
    
    if job.is_running() == True:
        global building
        building = True
    else:
        global building
        building = False
        setstatus(job.get_last_build())

# Initiate the threads
blinking()
if error == False:
    buildrunning()