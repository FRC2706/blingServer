#!/usr/bin/env python

import multiprocessing
import sys
import time
import logging
import argparse

from networktables import NetworkTables
from neopixel import *

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", help="The networktables server address",
                                      default='127.0.0.1')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

process = None

# LED strip configuration:
LED_COUNT      = 128     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN       = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

# Create the strip object for use by all pattern functions
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

# Intialize the library (must be called once before other functions).
strip.begin()

def doBling(data):
    import logging
    import signal

    def sig_term_handler(signal,frame):
        logger.debug("Received SIGTERM")
        clear()
        sys.exit(0)

    def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def clear():
        """Clear the strip"""

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, 0)
        strip.show()


    def solid(strip, color, wait_ms, iterations, brightness):
        """Generate a solid bar of color"""

        strip.setBrightness(brightness)

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)

        strip.show()
        if wait_ms == 0:
            while True:
                time.sleep(1)

        time.sleep(wait_ms/1000)

        clear()

    def blink(strip ,color, wait_ms, iterations, brightness):
        """Blink all the LEDs on and off at the same time"""

        strip.setBrightness(brightness)

	for j in range(iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)

            strip.show()
            time.sleep(wait_ms/1000.0)

            for i in range(strip.numPixels()):
                strip.setPixelColor(i, 0)

            strip.show()
            time.sleep(wait_ms/1000.0)

    def colorWipe(strip, color, iterations, wait_ms, brightness):
        """Wipe color across display a pixel at a time."""

        strip.setBrightness(brightness)

	for j in range(iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
                strip.show()
                time.sleep(wait_ms/1000.0)

            clear()

    def theaterChase(strip, color, iterations, wait_ms, brightness):
	"""Movie theater light style chaser animation."""

        strip.setBrightness(brightness)

        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, color)

                strip.show()
                time.sleep(wait_ms/1000.0)

                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)
        clear()

    def rainbow(strip, wait_ms, iterations, brightness):
	"""Draw rainbow that fades across all pixels at once."""

        strip.setBrightness(brightness)

        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))

            strip.show()
            time.sleep(wait_ms/1000.0)

        clear()

    def rainbowCycle(strip, wait_ms, iterations, brightness):
	""" Draw rainbow that uniformly distributes itself across all pixels."""

        strip.setBrightness(brightness)

        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))

            strip.show()
            time.sleep(wait_ms/1000.0)

        clear()

    def theaterChaseRainbow(strip, iterations, wait_ms, brightness):
	"""Rainbow movie theater light style chaser animation."""

        strip.setBrightness(brightness)

        for j in range(256*iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))

                strip.show()
                time.sleep(wait_ms/1000.0)

                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)
        clear()

    # ------------------------------------------------------------------------#

    signal.signal(signal.SIGTERM, sig_term_handler)

    process = multiprocessing.current_process()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("doBling (%r PID %r)" % (process.name, process.pid,))

    logger.debug("Received data %r", data)

    # Real work goes here
    command=data[0]

    red=data[1]
    green=data[2]
    blue=data[3]
    repeat=data[4]
    wait_ms=data[5]
    LED_BRIGHTNESS=data[6]


    Red=int(red)
    Green=int(green)
    Blue=int(blue)

    color=Color(Red,Green,Blue)
    #color=Color(int(red),int(green),int(blue))
    #color=Color(red,green,blue)

    #RBG=int(255)
    #color=Color(0,RBG,0)

    #GREEN=int(green)
    #color=Color(0,GREEN,0)

    iterations=int(repeat)
    wait_ms=int(wait_ms)
    LED_BRIGHTNESS=int(LED_BRIGHTNESS)

    if command == "colorWipe":
        colorWipe(strip, color, iterations, wait_ms, LED_BRIGHTNESS)  # Red wipe
    elif command == "solid":
        solid(strip, color, wait_ms, iterations, LED_BRIGHTNESS)
    elif command == "blink":
        blink(strip, color, wait_ms, iterations, LED_BRIGHTNESS)
    elif command == "theaterChase":
        theaterChase(strip, color, iterations, wait_ms, LED_BRIGHTNESS)
    elif command == "rainbow":
        rainbow(strip, iterations, wait_ms, LED_BRIGHTNESS)
    elif command == "theaterChaseRainbow":
        theaterChaseRainbow(strip, iterations, wait_ms, LED_BRIGHTNESS)
    elif command == "rainbowCycle":
        rainbowCycle(strip, iterations, wait_ms, LED_BRIGHTNESS)
    elif command == "clear":
	clear()

#   clear()

    logger.debug("Terminating")


def connectionListener(connected, info):
    logger.debug("%r ; Connected=%r" % (info, connected))

def handleBlingRequest(table, key, value, isNew):
    import logging
    global process

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("handleBlingRequest")

    command = value
   # color = sd.getString("color", "")
    red = sd.getNumber('red', int)
    green = sd.getNumber('green', int)
    blue = sd.getNumber('blue', int)
    iterations = sd.getNumber('repeat', int)
    wait_ms = sd.getNumber('wait_ms', int)
    LED_BRIGHTNESS = sd.getNumber('LED_BRIGHTNESS', int)

    data = (command, red, green, blue, iterations, wait_ms, LED_BRIGHTNESS)

    # Feedback to the roboRIO plus it means we will see a repeat of the previous
    # command as a change
    sd.putString("command", "received")

   # logger.debug("handling %r %r" % (command, color))

    if process and process.is_alive():
        logger.debug("terminating doBling process")
        process.terminate()
        process.join()

#   if command == "clear":
#       logger.debug("got clear command")
#   else:
    process = multiprocessing.Process(target=doBling, args=(data,))
    process.daemon = True
    process.start()

   # logger.debug("ending %r %r" % (command, color))

    # Let the roboRIO know we are done
    sd.putString("command", "processed")

if __name__ == "__main__":

    #ip = "roboRIO-2706-FRC.local"
    ip = args.server
    logger.info("ip = %s" % ip)
    NetworkTables.initialize(server=ip)
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)
    sd = NetworkTables.getTable("blingTable")
    sd.addTableListener(handleBlingRequest, True, "command")

    while True:
        time.sleep(1)
