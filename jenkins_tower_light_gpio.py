#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import threading
import jenkinsapi
import config as cfg
import signal
import copy
from jenkinsapi.jenkins import Jenkins
from requests.exceptions import ConnectionError

# Set the GPIO mode.
GPIO.setmode(GPIO.BCM)

# Get a GPIO code for a string
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
keepAlive = True


# ---------------------------------------------------- #
# --         All globally used functions            -- #
# ---------------------------------------------------- #

# Function to toggle everything off
def all_off():
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
def set_status(status):
    if status != "":
        all_off()
        if status == "SUCCESS":
            GPIO.output(getcode('green'), True)

        if status == "UNSTABLE":
            GPIO.output(getcode('yellow'), True)

        if status == "FAILURE":
            GPIO.output(getcode('red'), True)
    return


def set_error(value):
    global error
    if value is True or value is False:
        error = value
    else:
        error = True
        print("[ERROR] Only supply True or False to the setError function")


# Get all the jobs by a given name.
def get_jenkins_job_by_name(name):
    # Support sub-folders.
    if '/' in name:
        folder, name = name.rsplit('/', 1)
        server = copy.deepcopy(J)
        folder_path = '/'.join([f'job/{x}' for x in folder.split('/')])
        server.baseurl = server.baseurl + '/' + folder_path
        return server.get_job(name)
    else:
        return J.get_job(name)


def check_jobs_build_status():
    jobs = cfg.jobs
    success = 0
    unstable = 0
    failed = 0

    for item in jobs:
        try:
            job = get_jenkins_job_by_name(item)
        except jenkinsapi.custom_exceptions.UnknownJob:
            set_error(True)
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
        set_status('SUCCESS')
    if unstable > 0 and failed == 0:
        set_status('UNSTABLE')
    if failed > 0:
        set_status('FAILURE')


def check_jobs_building():
    global building
    jobs = cfg.jobs
    building = 0

    for item in jobs:
        try:
            job = get_jenkins_job_by_name(item)
        except jenkinsapi.custom_exceptions.UnknownJob:
            set_error(True)
        else:
            if job.is_running():
                building += 1

    if building > 0:
        building = True
    else:
        building = False
        check_jobs_build_status()


# ---------------------------------------------------- #

# Turn all off if any GPIO is still on
all_off()

# Toggle everything once
# toggle(getcode('buzzer'), .1)
toggle(getcode('red'), .2)
toggle(getcode('yellow'), .2)
toggle(getcode('green'), .2)

# Configure the Jenkins parameter and get the job
try:
    J = Jenkins(cfg.jenkinsurl, username=cfg.username, password=cfg.password)
except jenkinsapi.custom_exceptions.JenkinsAPIException:
    set_error(True)
    print("[ERROR] Jenkins authentication error!")
except ConnectionError:
    set_error(True)
    print("[ERROR] Jenkins connection error!")
else:
    print("[INFO] No Jenkins error!")
    set_error(False)
    # Get the status of the latest build before starting the threads
    check_jobs_build_status()


# Thread the blinking function
# Every 10s blink for 3s when we are building
def blinking():
    if keepAlive:
        threading.Timer(10.0, blinking).start()

        # Only blink when we are actually building
        if building or error:
            # If error, blink red.
            if error:
                color = "red"
            else:
                color = "yellow"

            all_off()
            pin = getcode(color)
            GPIO.output(pin, True)
            time.sleep(3)
            GPIO.output(pin, False)


# Check every 10s if we are building, if not or done get latest status
def build_running():
    if keepAlive:
        threading.Timer(10.0, build_running).start()
        if not error:
            check_jobs_building()


# Initiate the threads
blinking()
if not error:
    build_running()


# Catch the keyboard interrupt and stop the threads from executing
def main():
    global keepAlive
    while keepAlive:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[NOTICE] Jenkins Light terminated!")
            all_off()
            keepAlive = False


main()
