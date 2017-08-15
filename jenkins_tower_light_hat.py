#!/usr/bin/env python

from __future__ import print_function
import time
import threading
import jenkinsapi
import config as cfg
import signal
import automationhat
from jenkinsapi.jenkins import Jenkins
from requests.exceptions import ConnectionError

# ---------------------------------------------------- #
# --         General output information             -- #
# ---------------------------------------------------- #
# -- RED = output.one                               -- #
# -- YELLOW = output.two                            -- #
# -- GREEN = output.three                           -- #
# -- BUZZER = relay.one = unused                    -- #
# ---------------------------------------------------- #

# Global variables
building = False
error = False
keepAlive = True

# ---------------------------------------------------- #
# --         All globally used functions            -- #
# ---------------------------------------------------- #


# Function to toggle everything off
def all_off():
    automationhat.output.one.off()
    automationhat.output.two.off()
    automationhat.output.three.off()
    automationhat.relay.one.off()
    return


# Toggle function with parameter output and duration
def toggle(output_type, index, duration):
    # Create the function based on the parameters
    result = getattr(automationhat, output_type)
    full_function = getattr(result, index)

    full_function.on()
    time.sleep(duration)
    full_function.off()
    return


# Set according to status
def set_status(status):
    if status != "":
        all_off()
        if status == "SUCCESS":
            automationhat.output.three.on()

        if status == "UNSTABLE":
            automationhat.output.two.on()

        if status == "FAILURE":
            automationhat.output.one.on()
    return


def set_error(value):
    global error
    if value is True or value is False:
        error = value
    else:
        error = True
        print("[ERROR] Only supply True or False to the setError function")


def check_jobs_build_status():
    jobs = cfg.jobs
    success = 0
    unstable = 0
    failed = 0

    for item in jobs:
        try:
            job = J.get_job(item)
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
            job = J.get_job(item)
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
toggle("output", "one", .2)
toggle("output", "two", .2)
toggle("output", "three", .2)

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
    set_error(False)
    print("[INFO] No Jenkins error!")
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
                all_off()
                toggle("output", "one", 3)
            else:
                all_off()
                toggle("output", "two", 3)


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
