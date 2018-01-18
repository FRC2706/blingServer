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
   # repeat=parms.split()[2]

    command,color,repeat=parms.split(",")
    print("Command: %s" % command)
    print("Color:   %s" % color)
    print("Repeat:    ",  repeat)

    sd.putString('command', command)
    sd.putString('color', color)
    sd.putNumber('repeat', repeat)
