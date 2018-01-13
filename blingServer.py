#!/usr/bin/env python

import multiprocessing
import sys
import time
import logging

from networktables import NetworkTables
from neopixel import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

process = None

# LED strip configuration:
LED_COUNT      = 120      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()

def doBling(data):
    import logging
    import signal

    def clear():
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, 0)
        strip.show()

    def sig_term_handler(signal,frame):
        logger.debug("Received SIGTERM")
        clear()
        sys.exit(0)

    def colorWipe(strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChase(strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)

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

    def rainbow(strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):

            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)
    signal.signal(signal.SIGTERM, sig_term_handler)

    process = multiprocessing.current_process()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("doBling (%r PID %r)" % (process.name, process.pid,))

    logger.debug("Received data %r", data)

    # Real work goes here
    command=data[0]
    colorString=data[1]

    if colorString == "red":
        color=Color(255, 0, 0)
    elif colorString == "green":
        color=Color(0, 255, 0)
    elif colorString == "blue":
        color=Color(0, 0, 255)
    else:
        color=Color(32,32,32)

    if command == "colorWipe":
        colorWipe(strip, color)  # Red wipe
    elif command == "theaterChase":
        theaterChase(strip, color)
    elif command == "rainbow":
        rainbow(strip)
    elif command == "theaterChaseRainbow":
        theaterChaseRainbow(strip)
    elif command == "wheel":
        wheel(pos)
    clear()

    logger.debug("Terminating")


def connectionListener(connected, info):
    logger.debug("%r ; Connected=%r" % (info, connected))

def handleBlingRequest(table, key, value, isNew):
    import logging
    global process

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("handleBlingRequest")

    command = value
    color = sd.getString("color")
    data = (command, color)

    # Feedback to the roboRIO plus it means we will see a repeat of the previous
    # command as a change
    sd.putString("command", "received")

    logger.debug("handling %r %r" % (command, color))

    if process and process.is_alive():
        logger.debug("terminating doBling process")
        process.terminate()
        process.join()

    if command == "clear":
        logger.debug("got clear command")
    else:
        process = multiprocessing.Process(target=doBling, args=(data,))
        process.daemon = True
        process.start()
        
    logger.debug("ending %r %r" % (command, color))

    # Let the roboRIO know we are done
    sd.putString("command", "processed")

if __name__ == "__main__":

    #ip = "roboRIO-2706-FRC.local"
    ip = '127.0.0.1'
    NetworkTables.initialize(server=ip)
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)
    sd = NetworkTables.getTable("blingTable")
    sd.addTableListener(handleBlingRequest, True, "command")

    while True:
        time.sleep(1)
