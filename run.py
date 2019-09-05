import time
from rpi_ws281x import PixelStrip, Color
import argparse
import random
import requests

# LED strip configuration:
LED_COUNT = 300       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

TIME_INTERVAL = 5000

start = int(round(time.time() * 1000))

next_color = Color(255, 0, 0)

def push_pixels(strip):
    for i in reversed(range(strip.numPixels())):
        if i > 0:
            prev_color = strip.getPixelColor(i - 1)
            strip.setPixelColor(i, prev_color)
            strip.setPixelColor(i - 1, Color(0, 0, 0))
    strip.show()

def add_pixel(strip):
    global next_color
    if next_color != None:
        strip.setPixelColor(0, next_color)
        next_color = None
        strip.show()

def sync_data():
    global next_color
    next_color = Color(random.randint(0,255),
                       random.randint(0,255),
                       random.randint(0,255))

    # requests.get('example.com')

def wait():
    current = int(round(time.time() * 1000))
    age = current - start
    needed_rest = age % TIME_INTERVAL
    time.sleep(needed_rest / 1000.0)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    return parser.parse_args()

def init_strip():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    return strip

def clear(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
    args = parse_args()

    strip = init_strip()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            push_pixels(strip)
            sync_data()
            add_pixel(strip)
            wait()

    except KeyboardInterrupt:
        if args.clear:
            clear(strip)
