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

color_map = {
    'www.everyarabstudent.com-web': Color(255, 0, 0),
    'www.mirstudentov.com-web': Color(255, 153, 0),
    'www.suaescolha.com-web': Color(204, 255, 0),
    'www.mahasiswakeren.com-web': Color(51, 255, 0),
    'www.kazdystudent.pl-web': Color(0, 255, 102),
    'www.everystudent.com-web': Color(0, 255, 255),
    'www.cadaestudiante.com-web': Color(0, 102, 255),
    'www.kampusweb.com-web': Color(51, 0, 255),
    'www.everystudent.hu-web': Color(204, 0, 255),
    'www.everystudent.ro-web': Color(255, 0, 153)
}

es_prc_links = [
    "https://www.everystudent.com/features/followup.html",
    "https://www.cadaestudiante.com/articulos/conociendo2.html",
    "https://www.suaescolha.com/pessoalmente2/",
    "https://www.kampusweb.com/konular/kabul.html",
    "https://www.mahasiswakeren.com/artikel/402mengenal.html",
    "https://www.kazdystudent.pl/a/nowezycie.html",
    "https://www.everyarabstudent.com/a/fol.html",
    "https://www.everystudent.ro/a/interesa.html",
    "https://www.everystudent.hu/a/hogyantovabb.html",
    "https://www.mirstudentov.com/a/fol.html"
]

es_query_payload = {
    "size" : 300,
    "_source": ["collector_tstamp", "app_id", "unstruct_event_com_snowplowanalytics_snowplow_link_click_1.targetUrl"],
    "query": {
        "bool": {
            "should": [],
            "minimum_should_match" : 1,
            "must": {
                "range": {
                    "collector_tstamp": { "gte" : "now-4h" }
                }
            }
        }
    }
}
for es_url in es_prc_links:
    es_query_payload['query']['bool']['should'].append(
        {
            "term": {
                "unstruct_event_com_snowplowanalytics_snowplow_link_click_1.targetUrl": es_url
            }
        }
    )

def push_pixels(strip):
    tick = TIME_INTERVAL / 1000
    now = int(datetime.datetime.utcnow().strftime("%s"))

    for i in range(LED_COUNT):
        lower = now - (tick * (i + 1))
        higher = now - (tick * i)
        app_id = None
        for date, app in events.items():
            if (date < higher) and (date >= lower):
                print('found %s', app)
                app_id = app
                break
        strip.setPixelColor(i, color_for(app_id))

    strip.show()

def color_for(app_id):
    if app_id == None:
        return 0
    if app_id in color_map:
        return color_map[app_id]
    return Color(255, 255, 255)

def get_es_data():
    auth_token = os.environ.get('AUTH_TOKEN')
    url = 'https://org-cru-prod1.elasticsearch.snplow.net/_plugin/kibana/api/console/proxy?path=_search&method=POST'
    headers = { 'kbn-version': '6.5.4', 'authorization': 'Basic ' + auth_token, 'content-type': 'application/json' }
    r = requests.post(url, headers=headers, data=json.dumps(es_query_payload))
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
            wait()

    except KeyboardInterrupt:
        if args.clear:
            clear(strip)
