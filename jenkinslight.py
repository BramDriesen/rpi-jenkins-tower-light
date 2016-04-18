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


# Get a GPIO code for an string
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
def setstatus(status):
    if status != "":
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
    if value is True or value is False:
        error = value
    else:
        error = True
        print "[ERROR] Only supply True or False to the setError function"


def checkJobsBuildStatus():
    jobs = cfg.jobs
    success = 0
    unstable = 0
    failed = 0

    for item in jobs:
        try:
            job = J.get_job(item)
        except jenkinsapi.custom_exceptions.UnknownJob:
            setError(True)
        else:
            getstatus = job.get_last_build().get_status()
            if getstatus == "SUCCESS":
                success += 1
                continue
            if getstatus == "UNSTABLE":
                unstable += 1
                continue
            if getstatus == "FAILURE":
                failed += 1
                continue

    if success > 0 and unstable == 0 and failed == 0:
        setstatus('SUCCESS')
    if unstable > 0 and failed == 0:
        setstatus('UNSTABLE')
    if failed > 0:
        setstatus('FAILURE')


def checkJobsBuilding():
    global building
    jobs = cfg.jobs
    building = 0

    for item in jobs:
        try:
            job = J.get_job(item)
        except jenkinsapi.custom_exceptions.UnknownJob:
            setError(True)
        else:
            if job.is_running():
                building += 1

    if building > 0:
        building = True
    else:
        building = False
        checkJobsBuildStatus()


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
    checkJobsBuildStatus()


# Thread the blinking function
# Every 10s blink for 3s when we are building
def blinking():
    if keepalive:
        threading.Timer(10.0, blinking).start()

        # Only blink when we are actually building
        if building or error:
            # If error, blink red.
            if error:
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
    if keepalive:
        threading.Timer(10.0, buildrunning).start()
        if not error:
            checkJobsBuilding()


# Initiate the threads
blinking()
if not error:
    buildrunning()


# Catch the keyboard interrupt and stop the threads from executing
def main():
    global keepalive
    while keepalive:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "[NOTICE] Jenkins Light terminated!"
            alloff()
            keepalive = False


main()
