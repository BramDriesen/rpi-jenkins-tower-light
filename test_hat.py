#!/usr/bin/env python

import time

import automationhat

if automationhat.is_automation_hat():
    automationhat.light.power.write(1)
    automationhat.light.comms.write(1)

while True:
    if automationhat.is_automation_hat():
        automationhat.light.comms.toggle()
        automationhat.light.warn.toggle()

    automationhat.output.one.toggle()

    print(automationhat.analog.read())

    time.sleep(1.5)
