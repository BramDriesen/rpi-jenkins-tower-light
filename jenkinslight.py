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

# GPIO Setup
# 18 = Red
# 23 = Buzzer
# 24 = Yellow
# 27 = Green
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

# ---------------------------------------------------- #
# --         All globally uesd functions            -- #
# ---------------------------------------------------- #

# Function to toggle everything off
def alloff():
    GPIO.output(18, False)
    GPIO.output(23, False)
    GPIO.output(24, False)
    GPIO.output(27, False)
    return

# Toggle function with parameter output and duration
def toggle(gpio, duration):
    GPIO.output(gpio, True)
    time.sleep(duration)
    GPIO.output(gpio, False)
    time.sleep(duration)
    return

# Switch on/of
def onoff(gpio):
    alloff()
    GPIO.output(gpio, True)
    return

# Set according to status
def setstatus(build):
    if build != "":
        status = build.get_status()

        if status == "SUCCESS":
            onoff(27)

        if status == "UNSTABLE":
            onoff(24)

        if status == "FAILURE":
            onoff(18)
    return
        

# ---------------------------------------------------- #

# Turn all off if any GPIO is still on
alloff()

# Toggle everything once
toggle(23, .1)
toggle(18, .2)
toggle(24, .2)
toggle(27, .2)

# Configure the Jenkins parameter and get the job
J = Jenkins('http://jenkinscap.cloudapp.net:8080', username="rpi", password="")
job = J.get_job("UTC Behat")

# Get the status of the latest build before starting the threads
latestbuild = job.get_last_build()
setstatus(latestbuild)

# Thread the blinking function
building = False

# Every 10s blink for 3s when we are building
def blinking():
    threading.Timer(10.0, blinking).start()
    # Only blink when we are actually building
    if building == True:
        alloff()
        GPIO.output(24, True)
        time.sleep(3)
        GPIO.output(24, False)    

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
buildrunning()
blinking()


