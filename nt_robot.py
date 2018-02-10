#!/usr/bin/env python3
#
# This is a NetworkTables server (eg, the robot or simulator side).
#
# On a real robot, you probably would create an instance of the 
# wpilib.SmartDashboard object and use that instead -- but it's really
# just a passthru to the underlying NetworkTable object.
#
# When running, this will continue incrementing the value 'robotTime',
# and the value should be visible to networktables clients such as 
# SmartDashboard. To view using the SmartDashboard, you can launch it
# like so:
#
#     SmartDashboard.jar ip 127.0.0.1
#

import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
sd = NetworkTables.getTable("blingTable")

while True:
    parms = input("Enter command color: ")
    #command=parms.split()[0]
   # color=parms.split()[1]
   # repeat=parms.split()[2]\
	
    red,green,blue,repeat,wait_ms,LED_BRIGHTNESS,command=parms.split(",")
    print("Command: %s" % command)
    print("red:   %s", red)
    print("green:   %s",  green)
    print("blue:   %s",  blue)
    print("Repeat:  %s",  repeat)
    print("wait_ms:    %s", wait_ms)
    print("LED_BRIGHTNESS: %s", LED_BRIGHTNESS)

   # sd.putNumber('red', red)
    #sd.putNumber('green', green)
 #   sd.putNumber('blue', blue)
    #sd.putNumber('red', red)
    sd.putNumber('red', red)
    sd.putNumber('green', green)
    sd.putNumber('blue', blue)
    sd.putNumber('repeat', repeat)
    sd.putNumber('wait_ms', wait_ms)
    sd.putNumber('LED_BRIGHTNESS', LED_BRIGHTNESS)
    sd.putString('command', command)
 
