#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import threading
import jenkinsapi
import config as cfg
import signal
from jenkinsapi.jenkins import Jenkins
from requests.exceptions import ConnectionError

# Set the GPIO mode.
GPIO.setmode(GPIO.BCM)

# Get a gpio code for an string
def getcode(value):
    value = value.lower()
    return cfg.gpios.get(value, cfg.gpios.get('red'))

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setup(getcode('red'), GPIO.OUT)
GPIO.setup(getcode('buzzer'), GPIO.OUT)
GPIO.setup(getcode('yellow'), GPIO.OUT)
GPIO.setup(getcode('green'), GPIO.OUT)


# Global variables
building = False
error = False
keepalive = True

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

def setError(value):
    global error
    if value == True or value == False:
        error = value
    else:
        error = True
        print "[ERROR] Only supply True or False to the setError function"

# ---------------------------------------------------- #

# Turn all off if any GPIO is still on
alloff()

# Toggle everything once
# toggle(getcode('buzzer'), .1)
toggle(getcode('red'), .2)
toggle(getcode('yellow'), .2)
toggle(getcode('green'), .2)

# Configure the Jenkins parameter and get the job
try:
    J = Jenkins(cfg.jenkinsurl, username=cfg.username, password=cfg.password)
except jenkinsapi.custom_exceptions.JenkinsAPIException:
    setError(True)
    print "[ERROR] Jenkins authentication error!"
except ConnectionError:
    setError(True)
    print "[ERROR] Jenkins connection error!"
else:
    print "[INFO] No Jenkins error!"
    setError(False)
    # Get the status of the latest build before starting the threads
    job = J.get_job(cfg.jobs[0])
    latestbuild = job.get_last_build()
    setstatus(latestbuild)

# Thread the blinking function
# Every 10s blink for 3s when we are building
def blinking():
    if keepalive == True:
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
    if keepalive == True:
        threading.Timer(10.0, buildrunning).start()
        if error == False:
            global building
            if job.is_running() == True:
                building = True
            else:
                building = False
                setstatus(job.get_last_build())

# Initiate the threads
blinking()
if error == False:
    buildrunning()

# Catch the keyboard intterupt and stop the threads from executing
def main():
    global keepalive
    while keepalive == True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "[NOTICE] Jenkinslight terminated!"
            alloff()
            keepalive = False
main()
