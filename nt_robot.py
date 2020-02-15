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

import os
import json
import collections

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

def terminate(return_code):
    """Terminate the network tables server gracefully"""

    NetworkTables.shutdown()
    sys.exit(return_code)

def get_integer(var_name, default_value, min_value, max_value):
    """Get an integer value between a specified minimum and maximum value
       from the user and return it (sending the default if the user inputs
       nothing)
    """

    while True:
        try:
            tmp = input("Enter %s value [%d]: " % (var_name, default_value))
            if tmp == '':
                return default_value
            if not tmp.isdigit():
                print("*** value must be an integer in the range [%s-%s] ***" %(min_value, max_value))
            else:
               value = int(tmp)
               if value >= min_value and value <= max_value:
                   return value
                   break
               else:
                   print("*** value must be in the range [%s-%s] ***" %(min_value, max_value))
        except KeyboardInterrupt as e:
            print('keyboard interrupt in get_integer')
            terminate(0)

def get_string(var_name, valid_values, saved_value):
    """Get a string value from the user and verify it is one
       of the valid_values and return it (sending the saved_value if
       the user inputs nothing
    """

    while True:
        try:
            cmd = input("Enter %s [%s]: " % (var_name, saved_value))
            if cmd == '':
                return saved_value

            for value in valid_values:
                if cmd == value:
                    return cmd
            print("*** command must be one of %s" % valid_values)

        except KeyboardInterrupt as e:
            print('keyboard interrupt in get_string')
            terminate(0)


NetworkTables.initialize()
sd = NetworkTables.getTable("blingTable")

# The place we will squirrel away the last set of values passed to the
# bling server
saved_values_file = '/tmp/nt_robot_saved'

# We use an ordered dict here so that the user is always prompted for
# values in the same order (regular dicts don't retain key order)
# * NOTE * command should always be last as this is the value that
# the blingServer is waiting to see change before it reads any of the
# others
defaults = collections.OrderedDict([
('red',         {"default": 255, "min": 0, "max": 255}),
('green',       {"default": 255, "min": 0, "max": 255}),
('blue',        {"default": 255, "min": 0, "max": 255}),
('repeat',      {"default": 100, "min": 1, "max": 1000}),
('wait (ms)',   {"default": 10,  "min": 0, "max": 100}),
('brightness',  {"default": 128, "min": 0, "max": 255}),
('command', 'clear')
])

# The command strings recognized by the bling server
commands = [
"colorWipe",
"solid",
"blink",
"theaterChase",
"rainbow",
"rainbowCycle",
"theaterChaseRainbow",
"clear"
]

# Read in the saved defaults if the file exists. Since it is in /tmp it will
# disappear every time the PI reboots

if os.path.exists(saved_values_file):
    with open(saved_values_file, 'r') as f:
        saved_defaults=json.load(f)

        # When the defaults are written to the saved file no key order
        # is preserved so we have to reassign them one by one into defaults
        # (which has the correct order)
        for k in saved_defaults.keys():
            defaults[k] = saved_defaults[k]

try:
    # Keep asking for input until the user enters a keyboard interrrupt (<ctrl>C)
    print("Enter <ctrl>C to exit")
    while True:
        values_to_print = []
        try:
            for key in defaults.keys():
                if not key == 'command':
                    value = get_integer(key, defaults[key]["default"],
                                             defaults[key]["min"],
                                             defaults[key]["max"])
                    defaults[key]["default"] = value
                    values_to_print.append(value)
                else:
                    cmd_value = get_string(key, commands, defaults[key])
                    defaults[key] = cmd_value
                    values_to_print.append(cmd_value)

            print("Sending: Red Green Blue Repeat Wait Brightness Command")
            print("         %3d %5d %4d %6d %4d %10d %s" % tuple(values_to_print))

            # We could have sent all of these to the blingServer in the above loop
            # but don't so that there is not a significant delay (waiting for the
            # user to enter the next value) between sends

            for key in defaults.keys():
                if not key == 'command':
                    #print("sd.putNumber %s, %s" % (key, defaults[key]["default"]))
                    sd.putNumber(key, defaults[key]["default"])
                else:
                    #print("sd.putString %s, %s" % (key, defaults[key]))
                    sd.putString(key, defaults[key])

            with open(saved_values_file, 'w') as f:
                json.dump(defaults, f, indent=4)

        except KeyboardInterrupt as e:
            print("keyboard interrupt in main")
            terminate(0)

except Exception as e:
    print("Unexpected exception in main")
    print(str(e))
    terminate(1)
