import time
import os
from rpi_ws281x import PixelStrip, Color
import argparse
import random
import requests
import json
import datetime
import dateutil.parser

# LED strip configuration:
# Number of LED pixels.
LED_COUNT = int(os.environ.get('LED_COUNT') or 300)
# GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = int(os.environ.get('LED_PIN') or 18)
# LED signal frequency in hertz (usually 800khz)
LED_FREQ_HZ = int(os.environ.get('LED_FREQ_HZ') or 800000)
# DMA channel to use for generating signal (try 10)
LED_DMA = int(os.environ.get('LED_DMA') or 10)
# Set to 0 for darkest and 255 for brightest
LED_BRIGHTNESS = int(os.environ.get('LED_BRIGHTNESS') or 255)
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
# set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CHANNEL = 0

TIME_INTERVAL = int(os.environ.get('TIME_INTERVAL') or 5000)
RANDOM_PIXEL_DELAY = int(os.environ.get('RANDOM_PIXEL_DELAY') or 10)

start = int(round(time.time() * 1000))

next_color = Color(255, 0, 0)
events = {}

def push_pixels(strip):
    tick = TIME_INTERVAL / 1000
    now = int(datetime.datetime.utcnow().strftime("%s"))

    for i in range(LED_COUNT):
        lower = now - (tick * (i + 1))
        higher = now - (tick * i)
        app_id = None
        for date, app in events.items():
            if (date < higher) and (date > lower):
                print('found %s', app)
                app_id = app
                break
        color = 0
        if app_id != None:
            print('making pixel red: %i', i)
            color = Color(255, 0, 0)
            strip.setPixelColor(i, color)

    strip.show()

def add_pixel(strip):
    global next_color
    if next_color != None:
        strip.setPixelColor(0, next_color)
        next_color = None
        strip.show()

def get_es_data():
    auth_token = os.environ.get('AUTH_TOKEN')
    url = 'https://org-cru-prod1.elasticsearch.snplow.net/_plugin/kibana/api/console/proxy?path=_search&method=POST'
    headers = { 'kbn-version': '6.5.4', 'authorization': 'Basic ' + auth_token, 'content-type': 'application/json' }
    payload = {
        "_source": ["collector_tstamp","app_id"],
        "query": {
            "bool": {
            "must": [
                {
                "match_phrase": {
                    "unstruct_event_com_snowplowanalytics_snowplow_link_click_1.targetUrl": {
                    "query": "https://www.everystudent.com/features/followup.html"
                    }
                }
                },
                {
                "range": {
                    "collector_tstamp": { "gte" : "now-4h" }
                }
                }
            ]
            }
        }
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    return r.json()

def sync_data():
    global events
    data = {}
    for hit in get_es_data()['hits']['hits']:
        time = hit['_source']['collector_tstamp']
        seconds = int(dateutil.parser.parse(time).strftime("%s"))
        data[seconds] = hit['_source']['app_id']
    events = data

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
            sync_data()
            push_pixels(strip)
            # add_pixel(strip)
            wait()

    except KeyboardInterrupt:
        if args.clear:
            clear(strip)
